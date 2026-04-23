# MQL Query Guide for Feishu Project

MQL (Meego Query Language) is used with `search_by_mql` to perform complex queries
against Feishu Project workspaces.

## Prerequisites

**Always** call `list_workitem_field_config` before writing MQL to:
- Discover actual field keys (e.g. `field_xxx` or built-in names like `name`, `priority`)
- Get enum option IDs for select/radio fields
- Understand field types to use correct MQL syntax

If the query involves roles, also call `list_workitem_role_config`.

## Basic Syntax

```sql
SELECT fieldList
FROM `空间名`.`工作项类型名`
WHERE conditionExpression
[ORDER BY fieldOrderByList [{ASC|DESC}]]
[LIMIT [offset,] row_count]
```

- Identifiers (field names, space names, type names) are wrapped in backticks.
- String values use single quotes.
- Prefer field keys over field display names for reliability.

## Field Type Mapping (MQL types)

| MQL Type          | Corresponding Field Types                                                      |
|-------------------|-------------------------------------------------------------------------------|
| `long`            | `number` (only `work_item_id` and `auto_number`)                              |
| `double`          | All other `number` fields                                                      |
| `bool`            | `bool`                                                                         |
| `varchar`         | `text`, `multi-pure-text`, `select`, `tree-select`, `radio`, `user`, `link`, `signal`, `workitem_related_select` |
| `array(varchar)`  | `multi-select`, `tree-multi-select`, `multi-user`, `link_cloud_doc`, `workitem_related_multi_select`, `multi-file` |
| `array(struct)`   | `compound_field`                                                               |
| `datetime`        | `schedule()`, `precise_date()`                                                 |
| `date`            | `date`                                                                         |

## Array Functions

### array_contains — Direct array membership

```sql
-- Single value
array_contains(`优先级`, 'P0')

-- Multiple values (OR logic)
array_contains(`优先级`, 'P0', 'P1')
```

### array_cardinality — Array length

```sql
array_cardinality(`负责人`)   -- returns count of assignees
```

### any_match / all_match / none_match — Lambda expressions

```sql
-- Any assignee is 张三
any_match(`处理人`, x -> x = '张三')

-- All assignees are NOT 张三
none_match(`负责人`, x -> x = '张三')
```

### array_filter — Filter array elements

```sql
array_filter(`某数组字段`, x -> x > 100)
```

## Date / Time Functions

### RELATIVE_DATETIME series

Available functions:
- `RELATIVE_DATETIME_EQ`
- `RELATIVE_DATETIME_GT`
- `RELATIVE_DATETIME_LT`
- `RELATIVE_DATETIME_LE`
- `RELATIVE_DATETIME_BETWEEN`

Available relative keywords:
`today`, `tomorrow`, `yesterday`, `current_week`, `next_week`, `last_week`,
`current_month`, `next_month`, `last_month`, `future`, `past`

```sql
-- Created today
RELATIVE_DATETIME_EQ(`创建时间`, 'today')

-- Created after today
RELATIVE_DATETIME_GT(`创建时间`, 'today')

-- Created within the last 30 days
RELATIVE_DATETIME_BETWEEN(`创建时间`, 'past', '30d')

-- Scheduled start in the next 3 days
RELATIVE_DATETIME_BETWEEN(`__需求排期_开始时间`, 'future', '3d')
```

### Date-range fields (schedule / precise_date)

For date-range fields, query sub-fields directly:

```sql
-- 需求排期 is a schedule field → use sub-fields
WHERE `__需求排期_开始时间` > '2024-01-01'
WHERE `__需求排期_结束时间` < '2024-06-30'
```

Pattern: `` `__<field_name>_开始时间` `` and `` `__<field_name>_结束时间` ``.

## Person / Role Functions

### current_login_user — Current user

```sql
WHERE `创建人` = current_login_user()
```

### team — Team members

```sql
-- Team members including managers
WHERE any_match(`处理人`, x -> x in (team(true, '开放平台团队')))

-- Excluding managers
WHERE any_match(`处理人`, x -> x in (team(false, '开放平台团队')))
```

### all_participate_persons — All participants

```sql
WHERE array_contains(all_participate_persons(), '李四')
```

### Roles as query fields

Roles can be queried using the `__<RoleName>` syntax:

```sql
WHERE `__RD` = '张三'
WHERE `__QA` = '李四'
```

## Pagination

`search_by_mql` returns paginated results (50 per page by default).

- First call: omit `group_pagination_list`; response includes `session_id` and `count`.
- Subsequent pages: pass the `session_id` from the first response and set `page_num`.

```python
# Page 2
search_by_mql(
    project_key="...",
    session_id="<session_id from first call>",
    group_pagination_list=[{"group_id": "<group_id>", "page_num": 2}]
)
```

## Node Functions (控件/节点)

### all_nodes_name — All node names

```sql
SELECT all_nodes_name() FROM ...
WHERE array_contains(all_nodes_name(), '开始')
```

### in_progress_nodes_name — Currently active nodes

```sql
SELECT in_progress_nodes_name() FROM ...
WHERE in_progress_nodes_name() is not null
```

### risk_label — Node delay status

Returns delay labels like `["延期/开始","今日到期/结束"]`.

```sql
WHERE risk_label() = '["延期/开始","今日到期/结束"]'
```

### get_node_attribute — Node properties

```sql
get_node_attribute('<node_name>|__ALL|__BELONGING', '<attribute_name>')
```

- `__ALL` — all nodes
- `__BELONGING` — the node the current work item belongs to (所属节点)

Available attributes: 排期, 估分, 节点时间, 节点完成结论, 节点完成意见, 负责人, 当前负责人, 状态

```sql
-- Node schedule start/end
get_node_attribute('开始', '__排期_开始时间')
get_node_attribute('开始', '__排期_结束时间')

-- Node time start/completion
get_node_attribute('开始', '__节点时间_开始时间')
get_node_attribute('开始', '__节点时间_完成时间')

-- All nodes estimate > 10
WHERE get_node_attribute('__ALL', '估分') > 10

-- Node assignee equals 小李
WHERE get_node_attribute('调研', '负责人') = '小李'

-- Belonging node's current assignee (MUST use __BELONGING)
WHERE any_match(get_node_attribute('__BELONGING', '当前负责人'), x -> x in ('张三'))

-- Belonging node status
WHERE any_match(get_node_attribute('__BELONGING', '状态'), x -> x in ('进行中'))

-- Belonging node schedule in next 7 days
WHERE RELATIVE_DATETIME_BETWEEN(get_node_attribute('__BELONGING', '排期'), 'future', '7d')
```

## Relation Functions (关系/关联)

### relation — Get relation by name

```sql
relation('关系名')
```

### relation_field_chain — Chained relation query (max 3 hops)

```sql
-- Single hop
relation_field_chain('关联字段1')

-- Multi-hop (up to 3)
relation_field_chain('关联字段1', '关联字段2', '关联字段3')
```

**Subtask parent:** Use `'__父工作项'` (double underscore prefix) for subtask's parent:

```sql
relation_field_chain('__父工作项')
relation_field_chain('__父工作项', '需求关联软件')
```

### parent_work_item — Parent work item ID

```sql
parent_work_item(relation('关系名'))
```

### linked_work_item — Subtask source (来源控件)

```sql
linked_work_item()   -- subtask-specific
```

### association — Cross-space associated instance ID

```sql
association()
```

## Relation Judgment Functions

Use these to filter based on properties of related work items:

| User Intent | Function |
|-------------|----------|
| 每一个都满足 | `all_relation_match(relation, x -> expr)` |
| 存在一个满足 | `any_relation_match(relation, x -> expr)` |
| 每一个都不满足 | `none_relation_match(relation, x -> expr)` |
| 存在一个不满足 | `not all_relation_match(relation, x -> expr)` |

### Relation parameter forms

1. **Field reference:** `` `关联字段key` ``
2. **relation():** `relation('关系名')`
3. **relation_field_chain():** `relation_field_chain('关系1', '关系2')`

### Cross-space / multi-target field reference

Use `<target:...>` suffix for fields on the related end:

```sql
-- Universal fields (use <target:all>)
x.`创建时间<target:all>`
x.`优先级<target:all>`
x.`当前负责人<target:all>`

-- Space-specific fields
x.`字段名<target:空间key::工作项类型key>`
```

Universal fields available with `<target:all>`: 标题, 创建人, 创建时间, 业务线, 优先级,
当前负责人, 所属工作项, 所属空间, 工作项ID, 工作项类型, 状态

### Examples

```sql
-- Related work item's priority is P0
WHERE any_relation_match(`关联需求`, x -> x.`优先级` = 'P0')

-- All related items' descriptions contain '123'
WHERE all_relation_match(`多选关联字段`, x -> x.`描述<target:空间key::类型key>` like '%123%')

-- Subtask's parent work item created after a date
WHERE any_relation_match(relation_field_chain('__父工作项'), x -> x.`创建时间<target:all>` >= '2026-03-24')

-- Multi-hop: subtask → parent → related software, check node assignee
WHERE all_relation_match(
    relation_field_chain('__父工作项<target:681b228d::story>', '关联字段2'),
    x -> any_match(get_node_attribute('开始', '负责人'), y -> y in ('小李'))
)

-- Related work item's node attribute
WHERE any_relation_match(`XX关联`, x -> not array_contains(get_node_attribute('AA', '负责人'), '小李'))
```

## Status Time Functions

### status_time — Time a status was entered

```sql
-- Status entered time within a range
WHERE status_time('开始') between '2025-03-10' and '2025-04-10'
```

### Status start/end time

```sql
status_time('__状态名__开始时间')
status_time('__状态名__结束时间')
```

### Cumulative duration in a status

```sql
status_time('__结束状态__结束时间') - status_time('__开始状态__开始时间')
```

## Resource Table Queries (资源库)

To query resource instances, use the special table name `_<type_key>_resource`:

```sql
SELECT `work_item_id`, `name`
FROM `MySpace`.`_story_resource`
WHERE `name` like '%模板%'
```

## Common Query Examples

### All open P0 requirements assigned to me

```sql
SELECT `work_item_id`, `name`, `current_status_name`, `priority`
FROM `MySpace`.`需求`
WHERE `priority` = 'P0'
  AND `current_status_name` != '已完成'
  AND `创建人` = current_login_user()
```

### Defects created in the last 7 days

```sql
SELECT `work_item_id`, `name`, `current_status_name`, `priority`, `创建人`
FROM `MySpace`.`缺陷`
WHERE RELATIVE_DATETIME_BETWEEN(`created_at`, 'past', '7d')
```

### Requirements scheduled this month

```sql
SELECT `work_item_id`, `name`, `__需求排期_开始时间`, `__需求排期_结束时间`
FROM `MySpace`.`需求`
WHERE RELATIVE_DATETIME_BETWEEN(`__需求排期_开始时间`, 'current_month', '0d')
```

### Work items where team member 张三 participates

```sql
SELECT `work_item_id`, `name`, `current_status_name`
FROM `MySpace`.`需求`
WHERE array_contains(all_participate_persons(), '张三')
```
