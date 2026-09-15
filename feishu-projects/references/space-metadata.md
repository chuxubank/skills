# Space and Metadata

| Intent | Tool |
|---|---|
| Resolve/validate space name, key, or URL | `feishu_search_project_info` |
| List work-item types | `feishu_list_workitem_types` |
| Resolve work-item fields/options/templates | `feishu_list_workitem_field_config` |
| Resolve work-item roles | `feishu_list_workitem_role_config` |
| List configured relation definitions | `feishu_list_workitem_relations` |
| Resolve node fields/options | `feishu_list_node_field_config` |
| Diagnose missing create requirements | `feishu_get_workitem_field_meta` |

Use exact `field_keys`/`role_keys` when known. Use `field_query`/`role_query` only for discovery;
when discovery returns multiple plausible matches, ask the user to choose.

Creation requires a template ID obtained from
`feishu_list_workitem_field_config(field_keys=["template"])`. Call both field and role config
before `feishu_create_workitem`. `feishu_get_workitem_field_meta` is a recovery tool after create
failure or when required keys/values remain uncertain, not a replacement for configuration lookup.

`feishu_list_workitem_relations` is for listing configured relationships. In MQL, when the user
names a relation, preserve that exact name; do not use a fuzzy relation lookup to silently replace it.
