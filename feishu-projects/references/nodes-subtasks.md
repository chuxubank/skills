# Nodes & Subtasks Reference

Tools for inspecting flow nodes (节点), managing subtasks (子任务), and driving state/node transitions.

## Tool Map

| Intent | Tool | Key Params |
|--------|------|------------|
| 查看节点详情 | `get_node_detail` | `work_item_id`, `node_id_list`(optional), `field_key_list`(optional) |
| 查看子任务 | `get_node_detail` | `work_item_id`, `need_sub_task=true` |
| 创建子任务 | `update_node_subtask` | `node_id`, `action="create"`, `work_item_id`, `fields` |
| 修改子任务 | `update_node_subtask` | `node_id`, `action="update"`, `task_id`, `work_item_id` |
| 完成子任务 | `update_node_subtask` | `node_id`, `action="confirm"`, `task_id`, `work_item_id` |
| 回滚子任务 | `update_node_subtask` | `node_id`, `action="rollback"`, `task_id`, `work_item_id` |
| 修改节点（排期 / 负责人 / 字段） | `update_node` | `work_item_id`, `node_id`, `node_schedule`(optional), `node_owners`(optional), `fields`(optional) |
| 节点流转（完成） | `transition_node` | `work_item_id`, `action="confirm"`, `node_id` or `node_ids` |
| 节点回滚 | `transition_node` | `work_item_id`, `action="rollback"`, `node_id`, `rollback_reason` |
| 查询可流转状态（状态流） | `get_transitable_states` | `project_key`, `work_item_id`, `work_item_type`, `user_key` |
| 查询流转所需必填项 | `get_transition_required` | `project_key`, `work_item_id`, `state_key` |
| 查看评审状态 / 结论 | `list_finished_info` | `project_key`, `work_item_id`, `node_ids` |
| 更新评审结论 / 意见 | `update_finished_info` | `project_key`, `work_item_id`, `node_id` |

## update_node

Do **not** mix `node_schedule`, `schedules` (differential scheduling), and `node_owners` in the same call — update them separately.

To clear a schedule, pass an empty object: `node_schedule={}`.

## update_node_subtask

The `work_item_id` parameter means different things by action:

| Action | `work_item_id` value |
|--------|----------------------|
| `create` | Parent work item ID |
| `update` / `confirm` / `rollback` | Subtask's own ID |

`task_id` is the subtask ID returned by `create` and required for all subsequent operations.

## Transition vs. State Flow

- **Node-based work items** (节点流，e.g. 需求/story): use `transition_node`.
- **State-based work items** (状态流，e.g. 缺陷/issue): use `get_transitable_states` → `transition_state`.
