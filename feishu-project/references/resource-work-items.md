# Resource Work Items Reference (资源库)

Tools for managing resource library instances (资源库/资源实例) and deliverables (交付物).

Resource work items are a special type of work item that act as reusable templates.
When a work item type has the resource library feature enabled, you can create resource
instances and then spawn regular work items from them.

## Tool Map

| Intent | Tool | Key Params |
|--------|------|------------|
| 查看资源库配置（字段/角色） | `get_resource_work_item_type_conf` | `project_key`, `work_item_type_key` |
| 创建资源库实例 | `create_resource_work_item` | `project_key`, `work_item_type_key`, `fields`, `template_id`(optional) |
| 从资源库创建普通工作项 | `create_work_item_from_resource` | `project_key`, `work_item_id` (resource instance ID), `name`(optional), `fields`(optional) |
| 查询交付物信息 | `list_deliverables` | `project_key`, `work_item_ids` |

## Workflow

### 1. Check Resource Library Configuration

Before creating a resource instance, call `get_resource_work_item_type_conf` to discover
available resource fields and roles:

```
get_resource_work_item_type_conf(
    project_key="<key>",
    work_item_type_key="story"
)
```

Returns configured resource field info (field key, type, name) and role info.

### 2. Create a Resource Instance

Use `create_resource_work_item`. The `template_id` is required — use
`list_workitem_field_config` with `field_keys=["template"]` to find available templates.

```
create_resource_work_item(
    project_key="<key>",
    work_item_type_key="story",
    template_id="<template_id>",
    fields=[
        {"field_key": "name", "field_value": "Resource Name"},
        ...
    ]
)
```

Field values follow the same format as `create_workitem` — see `work-items.md` for the
field type reference.

Returns a link to the created resource instance on success.
If the work item type does not have the resource library enabled, returns an error.

### 3. Create a Regular Work Item from a Resource Instance

```
create_work_item_from_resource(
    project_key="<key>",
    work_item_id="<resource_instance_id>",
    name="New Work Item Name",
    fields=[
        {"field_key": "priority", "field_value": "P0"},
        ...
    ]
)
```

- `work_item_id` is the resource instance ID (from step 2 or from a URL).
- `name` is optional; when the name is a resource field, it will be ignored.
- `fields` are additional fields to set on the new work item.

Returns a link to the newly created work item on success.

### 4. Query Deliverables

For work items that have deliverables (交付物), use `list_deliverables` to query
the root work item (所属项目) and source work item (来源工作项) info:

```
list_deliverables(
    project_key="<key>",
    work_item_ids=["<id1>", "<id2>"]
)
```

## MQL: Querying Resource Instances

To query resource instances via MQL, use the special table name format:

```sql
SELECT `work_item_id`, `name`
FROM `<space>`.`_<work_item_type_key>_resource`
WHERE <conditions>
```

Example — query all resource instances under the "story" type:

```sql
SELECT `work_item_id`, `name`
FROM `MySpace`.`_story_resource`
WHERE `name` like '%模板%'
```
