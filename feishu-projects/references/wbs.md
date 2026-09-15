# WBS Plans

WBS has a published instance and an editable draft. Read from the state the user names; mutations
always target the draft.

## Tool map

| Intent | Tool |
|---|---|
| Create draft | `feishu_create_wbs_draft` |
| Read draft rows | `feishu_list_wbs_draft_rows` |
| Read published rows | `feishu_list_wbs_instance_rows` |
| Edit one draft operation | `feishu_edit_wbs_draft` |
| Publish draft | `feishu_publish_wbs_draft` |
| Reset draft | `feishu_reset_wbs_draft` |
| Follow create/edit/publish/reset | `feishu_get_wbs_draft_operation_progress` |

## Create and read

Create a draft from the target work item, then poll its returned operation ID with `op_type="create"`
until status `2` (complete). For row queries, prefer server-side `condition_query`; request only the
needed modules (`meta.*`, `base.*`, `node_extra.*`, `sub_instance_extra.*`, `custom_fields.*`). Use
`need_structure=true` when editing or traversing child rows.

For “all descendants,” first find the target row, then repeatedly query direct children using
`wbs_parent_id In <parent UUIDs>` until no children remain. Stay in the same state throughout:
draft traversal uses only draft rows; published traversal uses only instance rows. Continue pages
while `has_more` is true.

## Edit

`feishu_edit_wbs_draft` performs one atomic operation. Choose the operation from the user's noun:

- named work-item type (需求、项目活动等): `AddSubInstanceRows`; resolve its type first.
- resource node: `AddNodeRows`; get `element_key` from `feishu_list_element_template`.
- existing resource instance: `AddResourceSubInstanceRows`; query its resource ID first.
- explicit task/subtask: `AddTaskRows`.
- ambiguous “add/create”: ask which row type is intended.

Other operations cover delete/restore, order, dependencies, phase, name, owners, deliverables,
schedules, estimates, and actual time. Read the target row first to obtain exact UUIDs, parent UUID,
roles, and values to preserve. Resolve users and configured fields before writing.

After every edit, poll the returned operation ID with `op_type="edit"` until `success` or `failed`.
Use the same pattern for reset (`op_type="reset"`) and publication (`op_type="publish"`). Poll at
about three-second intervals for at most 120 seconds. If still incomplete, say: “正在执行中，请稍后在计划表草稿中查看结果”.

## Publish

Partial publication passes the requested row UUIDs and needs no extra confirmation.

Before full publication, ask exactly:

> 本人及协同者的全部编辑内容均会被发布，请确认是否全量发布？

Only after confirmation call `feishu_publish_wbs_draft` without `uuid_strings_list`. Do not pass
`["_all"]`. If full publication fails, do not retry as partial publication. If the request is blocked,
report: “变更触发了审批规则，发布被拦截，请前往计划表自行发布并创建审批”.

## Reset

Pass UUIDs for partial reset; omit `uuids` for full reset. Report rows returned as not reset as
unchanged rather than failed.
