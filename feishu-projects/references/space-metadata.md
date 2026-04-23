# Space & Metadata Reference

Tools for inspecting space configuration, work item types, field/role schemas, and relations.

## Tool Map

| Intent | Tool | Key Params |
|--------|------|------------|
| 查看空间基础信息 | `search_project_info` | `project_key` |
| 查看工作项类型列表 | `list_workitem_types` | `project_key` |
| 查看字段配置 / 枚举值 | `list_workitem_field_config` | `project_key`, `work_item_type`, `field_keys`(optional), `field_query`(optional) |
| 查看角色配置 | `list_workitem_role_config` | `project_key`, `work_item_type` |
| 查看工作项关联关系定义 | `list_workitem_relations` | `project_key` |
| 查看节点字段配置 | `list_node_field_config` | `project_key`, `work_item_type` |
| 查看创建工作项元信息 | `get_workitem_field_meta` | `project_key`, `work_item_type` |

## Usage Notes

- Call `list_workitem_field_config` **before** creating or updating work items to discover field keys and enum option IDs.
- Call `list_workitem_role_config` whenever a create/update operation involves roles.
- To find a template ID (required for `create_workitem`), call `list_workitem_field_config` with `field_keys=["template"]`.
