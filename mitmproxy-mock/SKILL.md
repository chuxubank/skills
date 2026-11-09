---
name: mitmproxy-mock
description: >-
  Simulate HTTP APIs with mitmproxy in WireGuard mode and check how the client
  behaves. Use when mocking or stubbing an app API (模拟接口), putting a phone
  or tablet on a mitmproxy WireGuard tunnel, or confirming which response the
  client rendered.
---

# mitmproxy WireGuard mocks

The addon is `scripts/map-local.py` in this skill's directory, the directory
that contains this file. Resolve that path from the skill, not from the
project cwd. Read the addon's module docstring before writing a route. The
docstring is the route contract.

A profile is one directory: `routes.json`, `data/`, optional
`hosts.json`, and optional `handlers.py`. That layout stays. The profile
name is `$HOST_ENV`. Pass
`--set mock_profile=<name>` only when the user wants a different profile.

The profile root is `$MITMPROXY_MOCK_DIR` when that variable is set,
otherwise `$HOME/.mitmproxy/mock`. The profile path is `<root>/$HOST_ENV/`
unless overridden. Pass an absolute path as `mock_profile` only when the user
gives one, such as fixtures in a repo. Do not put `routes.json` directly in
the root. Do not use `~/.config/mitmproxy`:
mitmproxy's own home is `~/.mitmproxy`. Keep fixtures out of the skill
directory. Keys, the client config, and logs stay in the run directory.

Intercept only environments the user authorized. Put the test hosts in
the profile `hosts.json`, once. A string is an exact hostname. An object
`{"pattern": "<regex>"}` matches the whole hostname. A missing or empty
file ignores the host. Route patterns match the path and query, not the
scheme or host.

## Prepare the profile

Use `$HOST_ENV` unless the user names another profile. Create
`<root>/$HOST_ENV/` only when that directory is missing. An empty
`routes.json` (`[]`) only observes live traffic. If `HOST_ENV` is empty and
the user names no profile, stop and ask.

This step is done when the profile path is that directory and every route
field is one the addon docstring lists.

Unmatched requests stay pass-through. A handler that returns without
`interceptor.respond` also stays pass-through. Restart mitmdump after
`routes.json` or `handlers.py` changes. A standard JSON file is read on each
request.

## Capture an unknown body

When the response shape is unknown, add `-w "$RUN/flows"` to the start command
and let one real response through. Read it back offline:

```bash
mitmdump -n -r "$RUN/flows" "~u <host/path> & ~s" --flow-detail 3
```

`-n` only prints the dump. Save the body under the profile `data/` directory, add the
route, then restart so the route loads. Raise `--flow-detail` if the body is
still hidden. Keep tokens and cookies out of fixtures and out of the summary.

## Start the tunnel

WireGuard is the mode. The server is UDP 51820 unless you select another
port. Its keys stay in `~/.mitmproxy/wireguard.conf`, so an existing client
config keeps working across runs.

If UDP 51820 is already taken, read that process's command line. Reuse it
when it is this addon, `mock_profile` is the profile you prepared, and you can read
its log. Otherwise stop and ask before taking the port. A second server needs
its own key file and port: `--mode wireguard:<keyfile>@<port>`.

`SKILL` is this skill's directory. Start one server in the background and
record its pid:

```bash
RUN="$HOME/.mitmproxy/runs/<name>"
mkdir -p "$RUN"
mitmdump --mode wireguard \
  -s "$SKILL/scripts/map-local.py" \
  >"$RUN/startup.log" 2>&1
```

Add `--set mock_profile=<name>` only for a profile other than `$HOST_ENV`.
This step is done when the log contains `profile=<path>` for that directory
and `WireGuard server listening`, plus the client config block.
Give that block to the user to import into the WireGuard app. Keep the
printed `Endpoint` and `DNS`. A QR, if they want one, goes in `$RUN` via
`qrencode`. The config, its keys, and any QR stay out of git.

The device connects with that config. The printed `AllowedIPs` is a full
tunnel: the device's other traffic uses this machine until they disconnect.
For HTTPS, install the mitmproxy CA from `http://mitm.it` while the tunnel is
up, then enable trust. On iOS that is Certificate Trust Settings. On Android
the app must trust the user CA. The cert files are
`~/.mitmproxy/mitmproxy-ca-cert.pem` and `.cer`.

## Watch the client

Drive the screen the user named, or ask them to. The check is done when both
are true: the log shows `-->` for that request and `matched handler=` for the
intended fixture, and the client UI matches that fixture.

When the log says the client does not trust the proxy certificate, stop. Ask
for a build that trusts the user CA. Leave certificate pinning in place.

When that URL never appears, report a tunnel miss. The client result is not
evidence about the product.

## Stop

Stop the pid recorded for this run and confirm its UDP port is closed. Tell
the user to disconnect the tunnel.
