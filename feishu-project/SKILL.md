---
name: feishu-project
description: >-
  This skill should be used when the user asks to "查看飞书项目", "查看需求",
  "查看缺陷", "查看任务", "我的待办", "搜索工作项", "查看视图", "查看空间信息",
  "查看排期", "查看评论", "查看操作记录", "查看团队", "创建工作项", "修改工作项",
  or any request related to Feishu/Lark project management (飞书项目/Meego).
  Provides workflows for querying, creating, and updating work items using
  the feishu MCP tools.
version: 0.1.0
---

# Feishu Project Skill

Query, browse, and manage Feishu Project (飞书项目/Meego) workspaces, work items,
views, schedules, and team information via the `mcp__feishu__*` MCP tool suite.

## Core Workflow

### 1. Identify the Space (空间)

Before any query, determine the **project_key** (空间标识). Resolve in this order:

1. A URL the user provides (extract `project_key` from the URL path)
2. The user naming the space directly — pass the name to `search_project_info`
3. Prior conversation context
4. **Fallback:** Read `.agents/constant.md` in the current project directory and extract `feishu-project-key` from it

```markdown
# .agents/constant.md example
- feishu-project-key: my_project_key
```

When falling back to `.agents/constant.md`, read the file silently and use the value without asking the user. If the file does not exist or contains no `project_key`, then ask the user to provide one.

```
search_project_info(project_key="<name or key>")
```

### 2. Identify the Work Item Type (工作项类型)

Most tools require a `work_item_type`. Common built-in types:

| 中文名 | Key        |
|--------|------------|
| 需求   | story      |
| 缺陷   | issue      |
| 任务   | task       |
| 子任务 | sub_task   |

For custom types, call:

```
list_workitem_types(project_key="...")
```

### 3. Choose the Right Tool

| User Intent              | Primary Tool                              |
|--------------------------|-------------------------------------------|
| 查看空间信息             | `search_project_info`                     |
| 查看工作项类型列表       | `list_workitem_types`                     |
| 查看单个工作项概况       | `get_workitem_brief`                      |
| 按条件搜索工作项         | `search_by_mql`                           |
| 查看我的待办 / 已办      | `list_todo`                               |
| 查看视图下的工作项       | `get_view_detail`                         |
| 搜索视图                 | `search_view_by_title`                    |
| 查看字段配置（含枚举值） | `list_workitem_field_config`              |
| 查看角色配置             | `list_workitem_role_config`               |
| 查看节点详情 / 子任务    | `get_node_detail`                         |
| 查看评论                 | `list_workitem_comments`                  |
| 查看操作记录             | `get_workitem_op_record`                  |
| 查看排期 / 工作量        | `list_schedule`                           |
| 查看团队列表             | `list_project_team`                       |
| 查看团队成员             | `list_team_members`                       |
| 查看用户信息             | `search_user_info`                        |
| 查看图表                 | `list_charts` / `get_chart_detail`        |
| 查看工时记录             | `get_workitem_man_hour_records`           |
| 查看关联工作项           | `list_related_workitems`                  |
| 查看状态流转             | `get_transitable_states`                  |
| 创建工作项               | `create_workitem`                         |
| 修改工作项字段           | `update_field`                            |
| 修改节点                 | `update_node`                             |
| 修改子任务               | `update_node_subtask`                     |
| 节点流转 / 回滚          | `transition_node`                         |
| 添加评论                 | `add_comment`                             |
| 创建 / 更新固定视图      | `create_fixed_view` / `update_fixed_view` |

### 4. Present Results

- Render work item lists as **Markdown tables** with key columns: ID, name, status, assignee, priority.
- For single work item details, use structured sections.
- Always include the work item URL when available.
- When results are paginated, inform the user of the total count and offer to fetch more.

## Key Workflows

### Searching Work Items with MQL

For complex queries, use `search_by_mql`. **Always** call `list_workitem_field_config`
first to discover field keys and enum values before composing MQL.

Refer to **`references/mql-guide.md`** for full MQL syntax, functions, and examples.

Quick pattern:

```
SELECT `work_item_id`, `name`, `current_status_name`, `priority`
FROM `<space>`.`<work_item_type>`
WHERE <conditions>
```

### Viewing My Todo List

```
list_todo(action="todo", page_num=1)   # 待办
list_todo(action="done", page_num=1)   # 已办
list_todo(action="overdue", page_num=1) # 逾期
list_todo(action="this_week", page_num=1) # 本周待办
```

Each page returns 50 items. To get all results, iterate `page_num` until fewer than
50 items are returned.

### Viewing Work Item Details

```
get_workitem_brief(work_item_id="<id>", project_key="<key>",
                   fields=["name", "current_status_name", "priority", ...])
```

Pass specific field keys to retrieve only relevant fields. Omit `fields` to get defaults.

### Creating Work Items

Before creating, **must** call:

1. `list_workitem_field_config` with `field_keys=["template"]` to find the template ID (required).
2. `list_workitem_field_config` to discover required fields and their enum values.
3. `list_workitem_role_config` if roles are involved.

Then call `create_workitem` with all required fields including the template.

### Updating Work Items

- Use `update_field` for field value changes.
- Use `update_node` for node schedule, owners, and custom fields on nodes.
- Use `update_node_subtask` for creating / modifying / completing subtasks.
- Use role_operate in `update_field` for role membership changes (not `role_owners` field).

### Working with URLs

When the user provides a Feishu project URL, extract parameters from it:

- `project_key` — the space identifier
- `work_item_type` — the work item type key
- `work_item_id` — the specific work item ID
- `view_id` — the view identifier

Many tools accept a `url` parameter that auto-extracts these values.

## Field Type Quick Reference

| Field Type                          | Value Format                                         |
|-------------------------------------|------------------------------------------------------|
| text / number / bool / link         | Literal value                                        |
| select / radio / tree-select        | Option ID (from field config)                        |
| multi-select                        | `[{"option_id": "..."}]`                             |
| user                                | user_key string                                      |
| multi-user                          | `["user_key_1", "user_key_2"]`                       |
| date                                | Millisecond timestamp                                |
| schedule                            | `[start_ms, end_ms]`                                 |
| precise_date                        | `{"start_time": ms, "end_time": ms}`                 |
| workitem_related_select             | Work item ID (number)                                |
| workitem_related_multi_select       | `[id1, id2]` (number array)                          |
| multi-text                          | Markdown string                                      |
| role_owners                         | `[{"role": "RoleName", "owners": ["user_key"]}]`     |

## Pagination

Most list endpoints return paginated results (default 50/page). When the user asks
for "all" items, loop `page_num` starting from 1 until a page returns fewer items
than the page size.

## Additional Resources

### Reference Files

- **`references/mql-guide.md`** — Full MQL syntax, functions, field type mapping, and query examples.
- **`references/tool-reference.md`** — Quick lookup mapping user intents to tool names with parameter hints.
