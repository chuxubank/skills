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
