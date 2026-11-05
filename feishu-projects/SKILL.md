---
name: feishu-projects
description: >-
  Deprecated：旧飞书项目 MCP skill；请改用官方 Meegle CLI 及其 meegle skill。
disable-model-invocation: true
version: 0.2.0
---

# Feishu Projects — Deprecated

This skill is deprecated. Use the official
[Meegle CLI (`larksuite/meegle-cli`)](https://github.com/larksuite/meegle-cli)
and its **`meegle` skill** for Feishu Project / Meego / Meegle operations.

## Migration

- Load the official `meegle` skill and follow its authorization guard, command discovery,
  and task-specific references. Its current documentation owns setup and command syntax;
  this repository does not duplicate them.
- If the CLI or skill is unavailable, report the missing prerequisite and refer to the
  official repository. Installation and authorization remain user-controlled.
- This entry is retained for existing links and migration discovery, with model invocation
  disabled on hosts that support that setting. Explicit invocation also routes to the
  replacement; it does not authorize the old MCP workflow.
- The old `feishu_*` tools and this directory's references are historical material, not
  current operating instructions or an automatic fallback. Do not translate their schemas
  directly into CLI parameters or assume feature parity; verify the official tool's capabilities.

Only when inspecting the former MCP integration or its history, read the
[archived workflow](references/legacy-workflow.md). For live work, use `meegle` instead.
