---
name: aep
description: >-
  Parse Adobe After Effects project files (.aep) on disk without After Effects.
  Use when inspecting comps, layers, footage, effects, keyframes, or the render
  queue from an .aep; comparing two projects; or dumping structure as JSON.
---

# AEP

Prefer the installed `py-aep` CLIs on PATH. After Effects does not need to be running. Docs: https://forticheprod.github.io/py-aep/

A running After Effects app is a different skill (`after-effects`). `.aepx` is XML — read it as XML, not with these commands.

## First commands

```bash
command -v aep-visualize aep-inspect aep-compare aep-validate
aep-visualize project.aep --depth 2 --no-properties
aep-visualize project.aep --format json --depth 2
```

Start with `--depth 2 --no-properties`. Raise depth only after that tree names the comps or layers that matter.

## Route

| Need | Command |
| --- | --- |
| Overview tree | `aep-visualize file.aep` |
| JSON | `aep-visualize file.aep --format json` |
| Item summary / one item | `aep-inspect file.aep` or `--item N` |
| Chunk tree / hex | `aep-compare file.aep --list` or `--dump PATH` |
| Diff two files | `aep-compare a.aep b.aep` |
| Python mutations | `uv run --with py-aep python` and `import py_aep; py_aep.parse("file.aep")` |

Do not guess CLI flags. Read `--help` or the docs page for the command in use.

## Limits

No expression evaluation, no rendering, no image sampling. Coverage is unofficial reverse-engineering, not Adobe's API.
