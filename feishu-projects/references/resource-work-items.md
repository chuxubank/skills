# Resource Work Items and Deliverables

| Intent | Tool |
|---|---|
| Inspect resource-library fields/roles | `feishu_get_resource_work_item_type_conf` |
| Create resource instance/template | `feishu_create_resource_work_item` |
| Find resource instances | `feishu_search_by_mql` with `_<type_key>_resource` table |
| List node/task element templates | `feishu_list_element_template` |
| Attach an existing resource instance to WBS | `feishu_edit_wbs_draft` (`AddResourceSubInstanceRows`) |
| Trace deliverable root/source items | `feishu_list_deliverables` |

Before creating a resource instance, call `feishu_get_resource_work_item_type_conf` and use only
its exact resource field and role keys. `template_id` is optional; when omitted, the service selects
the type's first workflow template. Field value shapes differ from ordinary create for some options:
follow the live `feishu_create_resource_work_item` schema, including `{value,label}` option objects.

There is no current `create_work_item_from_resource` tool. Creating a resource instance and adding
one to a WBS are distinct operations; use the WBS operation above for the latter.

Resource MQL table:

```sql
SELECT `work_item_id`, `name`
FROM `Space`.`_<work_item_type_key>_resource`
WHERE `name` like '%keyword%'
```

For resource nodes/tasks, call `feishu_list_element_template` with `element_type="node"` or
`"task"` and pass the returned `element_key` to the corresponding WBS add operation.

`feishu_list_deliverables` accepts deliverable item IDs and returns each deliverable's root work
item and direct source work item. Resolve names to IDs first with `feishu_get_workitem_brief`.
