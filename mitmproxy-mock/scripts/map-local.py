"""Serve fixtures from MOCK_DIR. Load with: mitmdump -s map-local.py

MOCK_DIR is required. Pass the profile path. The usual path is
~/.mitmproxy/mock/<name>/, and <name> is required. Another absolute path
is fine when the caller supplies it. There is no default profile.

Layout of MOCK_DIR:
  routes.json     Route list. Required, may be [].
  data/           Fixture files named by routes.
  handlers.py     Optional. Functions named handle_<name>.

routes.json entries:
  pattern         Regex searched against flow.request.pretty_url. Required.
  handler         Default "standard".
  file            Path relative to data/. The standard handler requires it.
  status_code     Default 200. Used by the standard handler.
  delay_seconds   Default 0. The standard handler sleeps this long and blocks
                  the proxy while it sleeps.

The first matching route wins. No match stays pass-through. A custom handler
that returns without interceptor.respond also stays pass-through.

A custom handler is handle_<name>(interceptor, flow, rule):
  rule.pattern, rule.file_path, rule.status_code, rule.delay_seconds,
  rule.handler_name
  interceptor.respond(flow, status_code, content, headers=None)
  content is str or bytes. The default Content-Type is application/json.

Routes and handlers load once. Restart mitmdump after changing routes.json
or handlers.py. The standard handler reads its file on every request.

An empty routes.json only observes: requests stay pass-through.
"""

import importlib.util
import json
import os
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from mitmproxy import ctx, http

DEFAULT_HEADERS = {"Content-Type": "application/json; charset=utf-8"}


@dataclass
class Route:
    pattern: str
    handler_name: str
    file_path: Path | None = None
    status_code: int = 200
    delay_seconds: float = 0
    compiled_pattern: re.Pattern = field(init=False)

    def __post_init__(self):
        self.compiled_pattern = re.compile(self.pattern)


def _mock_dir() -> Path:
    raw = os.environ.get("MOCK_DIR", "").strip()
    if not raw:
        raise RuntimeError("MOCK_DIR is required and has no default")
    path = Path(raw).expanduser().resolve()
    if not path.is_dir():
        raise RuntimeError(f"MOCK_DIR is not a directory: {path}")
    return path


def _load_routes(mock_dir: Path) -> list[Route]:
    routes_file = mock_dir / "routes.json"
    try:
        entries = json.loads(routes_file.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise RuntimeError(f"routes.json is missing: {routes_file}") from error
    except json.JSONDecodeError as error:
        raise RuntimeError(f"routes.json is invalid JSON: {routes_file}") from error
    if not isinstance(entries, list):
        raise RuntimeError("routes.json must be a list")

    routes: list[Route] = []
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict) or "pattern" not in entry:
            raise RuntimeError(f"routes.json[{index}] needs a pattern")
        file_name = entry.get("file")
        file_path = (mock_dir / "data" / file_name) if file_name else None
        try:
            routes.append(
                Route(
                    pattern=entry["pattern"],
                    handler_name=entry.get("handler", "standard"),
                    file_path=file_path,
                    status_code=entry.get("status_code", 200),
                    delay_seconds=entry.get("delay_seconds", 0),
                )
            )
        except re.error as error:
            raise RuntimeError(
                f"routes.json[{index}] has an invalid pattern: {error}"
            ) from error
    return routes


def _load_handlers(mock_dir: Path) -> dict[str, Callable]:
    handlers_file = mock_dir / "handlers.py"
    if not handlers_file.exists():
        return {}
    spec = importlib.util.spec_from_file_location(
        "mitmproxy_mock_handlers", handlers_file
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load handlers: {handlers_file}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return {
        name[len("handle_"):]: getattr(module, name)
        for name in dir(module)
        if name.startswith("handle_") and callable(getattr(module, name))
    }


class Interceptor:
    def __init__(self, mock_dir: Path):
        self.mock_dir = mock_dir
        self.handlers = _load_handlers(mock_dir)
        self.routes = _load_routes(mock_dir)
        ctx.log.info(
            f"MOCK_DIR={mock_dir} routes={len(self.routes)} "
            f"handlers={list(self.handlers) or '(none)'}"
        )

    def respond(
        self,
        flow: http.HTTPFlow,
        status_code: int,
        content: str | bytes,
        headers: dict | None = None,
    ):
        flow.response = http.Response.make(
            status_code, content, headers or DEFAULT_HEADERS
        )

    def _handle_standard(self, flow: http.HTTPFlow, rule: Route):
        if rule.delay_seconds > 0:
            time.sleep(rule.delay_seconds)
        if rule.file_path is None:
            raise RuntimeError("standard handler requires file")
        try:
            content = rule.file_path.read_text(encoding="utf-8")
            json.loads(content)
        except (OSError, json.JSONDecodeError) as error:
            raise RuntimeError(f"fixture {rule.file_path}: {error}") from error
        self.respond(flow, rule.status_code, content)
        ctx.log.info(f"matched handler=standard file={rule.file_path.name}")

    def _dispatch(self, flow: http.HTTPFlow, rule: Route):
        if rule.handler_name == "standard":
            self._handle_standard(flow, rule)
            return
        handler = self.handlers.get(rule.handler_name)
        if handler is None:
            raise RuntimeError(f"unknown handler: {rule.handler_name}")
        handler(self, flow, rule)
        if flow.response is not None:
            ctx.log.info(f"matched handler={rule.handler_name}")

    def process(self, flow: http.HTTPFlow):
        ctx.log.info(f"--> {flow.request.method} {flow.request.pretty_url}")
        for rule in self.routes:
            if not rule.compiled_pattern.search(flow.request.pretty_url):
                continue
            try:
                self._dispatch(flow, rule)
            except Exception as error:
                ctx.log.error(f"mock failed: {type(error).__name__}: {error}")
                self.respond(
                    flow,
                    500,
                    json.dumps({"error": "mock failed"}),
                )
            return


interceptor = Interceptor(_mock_dir())


def request(flow: http.HTTPFlow) -> None:
    interceptor.process(flow)
