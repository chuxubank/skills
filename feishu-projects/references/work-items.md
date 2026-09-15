# Work Items

Use these tools for ordinary work items; WBS rows have a separate workflow in `wbs.md`.

## Query routing

| Intent | Tool | Required locator |
|---|---|---|
| Item by ID/name/URL | `feishu_get_workitem_brief` | ID or name, plus space unless URL |
| Conditional search | `feishu_search_by_mql` | space and MQL |
| My todo/done/overdue/this week | `feishu_list_todo` | `action` |
| Related items | `feishu_list_related_workitem` | space and item ID |

`feishu_get_workitem_brief` returns only fixed base fields unless `fields` is supplied. Use
`fields=["_all"]` for all logical fields and continue with `next_page_token`; otherwise request
only known field keys.

`feishu_list_todo` actions are `todo`, `done`, `overdue`, and `this_week`. For todo-like actions,
`todo_scope` is one of `all`, `in_progress`, `not_started`; default to `in_progress` when the user
does not specify. Each page has 50 rows. Fetch every page only for explicit complete-list intent.

For MQL syntax and its distinct session pagination, load `mql-guide.md`.

## Create

Before `feishu_create_workitem`:

1. Call `feishu_list_workitem_field_config` for the target type. Query `template` explicitly and
   resolve every user-mentioned field to one exact key and option value.
2. Call `feishu_list_workitem_role_config` for the target type.
3. Resolve people with `feishu_search_user_info`.
4. Include the mandatory `template` field in `fields`.

If creation fails because required data is missing, call `feishu_get_workitem_field_meta`, fill only
the missing requirements, and retry.

## Update

Resolve each field with `feishu_list_workitem_field_config` before
`feishu_update_field`. Use `role_operate` for role membership and resolve its exact role key with
`feishu_list_workitem_role_config`. Use `feishu_update_node` instead for node fields.

Key value shapes:

| Type | Value |
|---|---|
| text, multi-pure-text, link, bool, number | literal |
| multi-text | Markdown |
| user / multi-user | user key / user-key array |
| select, radio, tree-select, template | option/template ID |
| multi-select | option objects; free-add only when supported |
| date | epoch milliseconds at day precision |
| schedule | `[start_ms,end_ms]` |
| precise_date | `{start_time,end_time}` |
| related single / multi | numeric ID / numeric ID array (follow live schema if update differs) |
| compound fields | JSON string in the operation shape documented by the live tool |

## State-flow transition

For state-flow items such as defects:

1. `feishu_get_transitable_states`
2. If needed, `feishu_get_transition_required` with the target state key
3. Fill required values
4. `feishu_transition_state` with the returned transition ID

Node-flow transitions use `nodes-subtasks.md`.
