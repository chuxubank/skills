---
name: feishu-projects
description: >-
  This skill should be used when the user asks to "查看飞书项目", "查看需求",
  "查看缺陷", "查看任务", "我的待办", "搜索工作项", "查看视图", "查看空间信息",
  "查看排期", "查看评论", "查看操作记录", "查看团队", "创建工作项", "修改工作项",
  "资源库", "交付物", "上传附件", "下载附件",
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

Route to the appropriate reference document by category:

| Category | Covers | Reference |
|----------|--------|-----------|
| Space & Metadata | 空间信息、工作项类型、字段/角色配置、关联关系定义 | `references/space-metadata.md` |
| Work Items | 查询、创建、修改、状态流转（状态流工作项） | `references/work-items.md` |
| Views & Charts | 视图搜索/详情、图表、固定视图管理 | `references/views-charts.md` |
| Nodes & Subtasks | 节点详情、子任务 CRUD、节点流转/回滚（节点流工作项） | `references/nodes-subtasks.md` |
| Teams & Users | 团队列表/成员、用户信息查询、排期/工作量 | `references/teams-users.md` |
| Activity | 评论列表/添加、操作记录、工时登记 | `references/activity.md` |
| Resource Work Items | 资源库配置、资源实例创建、从资源创建工作项、交付物查询 | `references/resource-work-items.md` |
| Attachments | 附件上传/下载、分片上传、富文本图片 | `references/attachments.md` |
| MQL Queries | 复杂条件搜索语法（含节点/关联/状态时间高级函数） | `references/mql-guide.md` |

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

Pass specific field keys to retrieve only relevant fields. See **`references/work-items.md`** for querying patterns including MQL and todo list.

### Creating Work Items

See **`references/work-items.md`** for the required preparation steps and field format reference.

### Updating Work Items

See **`references/work-items.md`** for field update patterns and **`references/nodes-subtasks.md`** for node/subtask updates.

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

- **`references/space-metadata.md`** — Space info, work item types, field/role configs, relation definitions.
- **`references/work-items.md`** — Querying, creating, and updating work items; field type reference; todo list.
- **`references/views-charts.md`** — Views search/detail, chart listing, fixed view management.
- **`references/nodes-subtasks.md`** — Node detail, subtask CRUD, node/state transitions.
- **`references/teams-users.md`** — Team lists, team members, user info lookup, schedule/workload.
- **`references/activity.md`** — Comments, operation records, man-hour logs.
- **`references/resource-work-items.md`** — Resource library config, resource instance CRUD, deliverables.
- **`references/attachments.md`** — File upload/download, multipart upload, rich text images.
- **`references/mql-guide.md`** — Full MQL syntax, functions, field type mapping, and query examples.
