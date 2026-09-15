# Nodes and Subtasks

| Intent | Tool |
|---|---|
| Inspect node fields/subtasks | `feishu_get_node_detail` |
| Update node owners, fields, schedule | `feishu_update_node` |
| Create/update/complete/rollback subtask | `feishu_update_node_subtask` |
| Complete/rollback node | `feishu_transition_node` |
| Inspect transition requirements | `feishu_get_transition_required` |

## Node updates

Resolve custom node fields with `feishu_list_node_field_config`. If assigning a person-specific
schedule or changing a person-bound node field, add that person to `node_owners` first.

Every `node_schedule` or `schedules` entry must explicitly set `clear_schedule`:

- `false`: incremental merge; omitted schedule values remain unchanged. Use this by default.
- `true`: overwrite/clear semantics; omitted values may be cleared. Before using it, call
  `feishu_get_node_detail` and resend every schedule value that must be preserved. Use `null` for
  the value the user explicitly asked to clear.

Do not represent clearing as an empty schedule object. Dates are local-day epoch milliseconds.

## Subtasks

`feishu_update_node_subtask` always needs the parent work item's node ID. Creation requires a
`name` field. Update/confirm/rollback also require the `task_id` returned for the subtask.
`work_item_id` identifies the work item that owns the node; use a URL when available to avoid
manual locator mistakes. Resolve configured subtask fields from the `sub_task` field config.

## Transitions

- Node-flow item: optionally inspect requirements, then call `feishu_transition_node` with one
  `node_id` and `action="confirm"` or `action="rollback"`; rollback requires a reason.
- State-flow item: use `feishu_get_transitable_states` and `feishu_transition_state` as described
  in `work-items.md`.

The current MCP has no standalone finished-review read/update tools. Read configured completion
fields through node detail and update supported node fields through `feishu_update_node`.
