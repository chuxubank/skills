---
name: feishu-projects
description: >-
  飞书项目 / Meego 工作项与计划表操作。用于查看或搜索空间、需求、缺陷、任务、
  待办、视图、图表、排期、评论、操作记录、团队、资源库和交付物；创建或修改工作项、
  节点、子任务、固定视图；以及创建、编辑、发布或重置 WBS 计划表草稿和上传下载附件。
version: 0.2.0
---

# Feishu Projects

Use the current `feishu_*` tools as the source of truth for Feishu Project (Meego).
Load only the reference matching the requested branch.

## 1. Resolve the locator

Prefer a user-provided Meego URL. When a tool accepts `url`, pass the URL directly so it
extracts `project_key`, work-item type, item ID, or view ID. Otherwise resolve the space with
`feishu_search_project_info`.

If no space is present in the request or conversation, inspect only matching key lines in these
project-local files, in order: `.agents/constant.md`, `.agents/constants.md`, `local.properties`,
`.env`, `.env.local`. Recognize `feishu-project-key`, `feishu_project_key`,
`FEISHU_PROJECT_KEY`, or `project_key`. Never expose unrelated values. Ask for the space only
when no candidate is available.

Resolve uncertain or custom work-item types with `feishu_list_workitem_types`; do not guess a
key from its display name.

## 2. Route by branch

| Branch | Load |
|---|---|
| Space, types, fields, roles, relations | `references/space-metadata.md` |
| Work-item query/create/update/state | `references/work-items.md` |
| Views, charts, fixed and panorama views | `references/views-charts.md` |
| Nodes, subtasks, node transitions | `references/nodes-subtasks.md` |
| Teams, users, schedules/workload | `references/teams-users.md` |
| Comments, operation history, man-hours | `references/activity.md` |
| Resource libraries and deliverables | `references/resource-work-items.md` |
| WBS plan drafts and published rows | `references/wbs.md` |
| Upload/download and rich-text files | `references/attachments.md` |
| Complex MQL searches | `references/mql-guide.md` |

`references/tool-reference.md` is the compact inventory when the correct branch is unclear.

## 3. Apply schema-first preparation

- **Create work item:** call both `feishu_list_workitem_field_config` and
  `feishu_list_workitem_role_config`; obtain the mandatory template ID from the `template`
  field options before `feishu_create_workitem`.
- **Update field/role:** resolve the exact field or role config first. If fuzzy lookup returns
  multiple candidates, ask the user to choose instead of guessing.
- **Create resource instance:** call `feishu_get_resource_work_item_type_conf` first.
- **Node fields:** use `feishu_list_node_field_config`; node schedules and owners follow the
  preservation rules in `references/nodes-subtasks.md`.
- **MQL:** identify the target space and target work-item type. Query field config for field
  semantics, role config for roles, and use relation names exactly as the user supplied.
- **WBS:** distinguish draft rows from published instance rows. Mutations target a draft and
  must be followed through their operation status.

Treat each live tool schema and returned error as authoritative. On a schema/query error, adjust
only the failing field, relation, parameter, or clause. An empty successful query is a valid result.

## 4. Pagination and completion

Pagination is endpoint-specific:

- `feishu_list_todo`: 50 rows/page; fetch pages 1, 2, … only when the user requests all results,
  stopping when a page has fewer than 50 rows or no data.
- `feishu_search_by_mql`: reuse `session_id`; pass an empty `mql` on later pages and paginate by
  returned `group_id`.
- WBS row APIs: continue while `has_more` is true.
- Team, field/role, view, comment, and activity APIs use their returned page token/count semantics.

Do not apply one generic page-size rule to every endpoint.

## 5. Mutations and results

Execute the requested mutation once prerequisites are known. Full WBS publication is the one
operation requiring the exact confirmation in `references/wbs.md`; partial publication does not.

Present compact, relevant fields rather than a fixed table shape. Include item URLs when returned.
For failures, report the tool error and the unresolved input; do not claim success from an accepted
asynchronous operation until its progress endpoint confirms completion.
