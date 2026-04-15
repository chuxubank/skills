# Feishu Project Tool Quick Reference

Mapping of common user intents to the correct `mcp__feishu__*` tool, with key parameters.

## Space & Metadata

| Intent | Tool | Key Params |
|--------|------|------------|
| 查看空间基础信息 | `search_project_info` | `project_key` |
| 查看工作项类型列表 | `list_workitem_types` | `project_key` |
| 查看字段配置 / 枚举值 | `list_workitem_field_config` | `project_key`, `work_item_type`, `field_keys`(optional), `field_query`(optional) |
| 查看角色配置 | `list_workitem_role_config` | `project_key`, `work_item_type` |
| 查看工作项关联关系 | `list_workitem_relations` | `project_key` |
| 查看节点字段配置 | `list_node_field_config` | `project_key`, `work_item_type` |
| 查看创建工作项元信息 | `get_workitem_field_meta` | `project_key`, `work_item_type` |

## Querying Work Items

| Intent | Tool | Key Params |
|--------|------|------------|
| 查看单个工作项详情 | `get_workitem_brief` | `work_item_id`, `project_key`(optional), `fields`(optional) |
| 按条件搜索工作项 (MQL) | `search_by_mql` | `project_key`, `mql` |
| 查看我的待办 | `list_todo` | `action="todo"`, `page_num` |
| 查看我的已办 | `list_todo` | `action="done"`, `page_num` |
| 查看逾期工作项 | `list_todo` | `action="overdue"`, `page_num` |
| 查看本周待办 | `list_todo` | `action="this_week"`, `page_num` |

## Views & Charts

| Intent | Tool | Key Params |
|--------|------|------------|
| 按名搜索视图 | `search_view_by_title` | `project_key`, `view_scope`, `key_word` |
| 查看视图详情 / 工作项列表 | `get_view_detail` | `view_id`, `project_key`(optional), `fields`(optional) |
| 查看视图下图表列表 | `list_charts` | `project_key`, `view_id` |
| 查看图表详情 | `get_chart_detail` | `chart_id`, `project_key`(optional) |

## Nodes & Subtasks

| Intent | Tool | Key Params |
|--------|------|------------|
| 查看节点详情 / 子任务 | `get_node_detail` | `work_item_id`, `node_id_list`(optional), `need_sub_task` |
| 查看可流转状态 | `get_transitable_states` | `project_key`, `work_item_id`, `work_item_type`, `user_key` |
| 查看流转所需必填项 | `get_transition_required` | `project_key`, `work_item_id`, `state_key` |

## Activity & Comments

| Intent | Tool | Key Params |
|--------|------|------------|
| 查看评论列表 | `list_workitem_comments` | `project_key`, `work_item_id` |
| 查看操作记录 | `get_workitem_op_record` | `project_key`, `work_item_id` |
| 查看工时记录 | `get_workitem_man_hour_records` | `project_key`, `work_item_type`, `work_item_id` |

## Team & Users

| Intent | Tool | Key Params |
|--------|------|------------|
| 查看团队列表 | `list_project_team` | `project_key` |
| 查看团队成员 | `list_team_members` | `team_id`, `project_key` |
| 查看用户信息 | `search_user_info` | `user_keys` (name/email/key, max 20) |
| 查看排期 / 工作量 | `list_schedule` | `user_keys`, `start_time`, `end_time`, `project_key` |

## Write Operations

| Intent | Tool | Key Params |
|--------|------|------------|
| 创建工作项 | `create_workitem` | `work_item_type`, `project_key`, `fields` (must include template) |
| 修改工作项字段 | `update_field` | `work_item_id`, `project_key`(optional), `fields`, `role_operate`(optional) |
| 修改节点 / 排期 | `update_node` | `work_item_id`, `node_id`, `node_schedule`(optional), `fields`(optional) |
| 创建 / 修改 / 完成子任务 | `update_node_subtask` | `node_id`, `action`, `work_item_id`, `fields`(optional) |
| 节点流转 | `transition_node` | `work_item_id`, `action="confirm"` |
| 节点回滚 | `transition_node` | `work_item_id`, `action="rollback"`, `rollback_reason` |
| 添加评论 | `add_comment` | `work_item_id`, `comment_content`, `project_key`(optional) |
| 创建固定视图 | `create_fixed_view` | `project_key`, `work_item_type`, `work_item_id_list`, `name` |
| 更新固定视图 | `update_fixed_view` | `project_key`, `view_id`, `work_item_type`, `add_work_item_ids` / `remove_work_item_ids` |

## Related Work Items

| Intent | Tool | Key Params |
|--------|------|------------|
| 查看关联工作项 | `list_related_workitems` | `project_key`, `work_item_type`, `work_item_id`, `relation_work_item_type_key`, `relation_key` |
| 查看关联关系定义 | `list_workitem_relations` | `project_key` |

## URL Parameter Extraction

Many tools accept a `url` parameter. From a Feishu project URL, the following can be extracted:

- `project_key` — space identifier (from URL path)
- `work_item_type` — work item type key
- `work_item_id` — specific work item ID
- `view_id` — view identifier

When the user provides a URL, prefer passing it via the `url` parameter to let the
tool auto-extract these values.
