# Work Items Reference

Tools for querying, creating, and updating work items (需求/story, 缺陷/issue, 任务/task, etc.).

## Common Work Item Types

| 中文名 | Key      |
|--------|----------|
| 需求   | story    |
| 缺陷   | issue    |
| 任务   | task     |
| 子任务 | sub_task |

For custom types, call `list_workitem_types(project_key="...")`.

## Querying

| Intent | Tool | Key Params |
|--------|------|------------|
| 查看单个工作项详情 | `get_workitem_brief` | `work_item_id`, `project_key`(optional), `fields`(optional) |
| 按条件搜索工作项 (MQL) | `search_by_mql` | `project_key`, `mql` |
| 查看我的待办 | `list_todo` | `action="todo"`, `page_num` |
| 查看我的已办 | `list_todo` | `action="done"`, `page_num` |
| 查看逾期工作项 | `list_todo` | `action="overdue"`, `page_num` |
| 查看本周待办 | `list_todo` | `action="this_week"`, `page_num` |
| 查看关联工作项 | `list_related_workitem` | `project_key`, `work_item_id`, `relation_field_key`(optional) |

### get_workitem_brief

Pass specific field keys in `fields` to retrieve only what you need:

```
get_workitem_brief(
    work_item_id="<id>",
    project_key="<key>",
    fields=["name", "current_status_name", "priority", "assignee"]
)
```

### list_todo

Each page returns up to 50 items. Iterate `page_num` until a page returns fewer than 50 items.

### search_by_mql

For complex queries — see **`mql-guide.md`** for full syntax.

Quick pattern:
```sql
SELECT `work_item_id`, `name`, `current_status_name`, `priority`
FROM `<space>`.`<work_item_type>`
WHERE <conditions>
```

**Always** call `list_workitem_field_config` first to get actual field keys and enum values.

## Creating Work Items

**Required preparation:**

1. `list_workitem_field_config` with `field_keys=["template"]` → get template ID (mandatory field)
2. `list_workitem_field_config` → discover all required fields and their enum values
3. `list_workitem_role_config` → if the item involves roles

Then:
```
create_workitem(
    work_item_type="story",
    project_key="<key>",
    fields=[
        {"field_key": "template", "field_value": "<template_id>"},
        {"field_key": "name", "field_value": "My Requirement"},
        ...
    ]
)
```

## Updating Work Items

| Intent | Tool | Key Params |
|--------|------|------------|
| 修改字段值 | `update_field` | `work_item_id`, `project_key`, `fields` |
| 修改角色成员 | `update_field` with `role_operate` | `work_item_id`, `role_operate=[{op, role_key, user_keys}]` |
| 流转状态（状态流工作项） | `transition_state` | `work_item_id`, `transition_id` |
| 查询可流转状态 | `get_transitable_states` | `project_key`, `work_item_id`, `work_item_type`, `user_key` |

**Role membership changes:** Use `role_operate` in `update_field`, not the `role_owners` field directly.

## Field Type Quick Reference

| Field Type | Value Format |
|------------|--------------|
| text / number / bool / link | Literal value (as string) |
| select / radio / tree-select | Option ID from `list_workitem_field_config` |
| multi-select | `[{"option_id": "..."}]` |
| user | user_key string |
| multi-user | `["user_key_1", "user_key_2"]` |
| date | Millisecond timestamp (day precision) |
| schedule | `[start_ms, end_ms]` |
| precise_date | `{"start_time": ms, "end_time": ms}` |
| workitem_related_select | Work item ID (number) |
| workitem_related_multi_select | `[id1, id2]` (number array) |
| multi-text | Markdown string |
| role_owners | `[{"role": "RoleName", "owners": ["user_key"]}]` |
| template | Template ID (number, obtain from field config) |
