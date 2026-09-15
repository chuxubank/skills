# Feishu Projects Tool Inventory

Use the live `feishu_*` schema for exact parameters. This file is a routing inventory, not a cached
schema.

| Area | Current tools |
|---|---|
| Space/schema | `feishu_search_project_info`, `feishu_list_workitem_types`, `feishu_list_workitem_field_config`, `feishu_list_workitem_role_config`, `feishu_list_node_field_config`, `feishu_list_workitem_relations`, `feishu_get_workitem_field_meta` |
| Work items | `feishu_get_workitem_brief`, `feishu_search_by_mql`, `feishu_list_todo`, `feishu_list_related_workitem`, `feishu_create_workitem`, `feishu_update_field`, `feishu_get_transitable_states`, `feishu_transition_state` |
| Views/charts | `feishu_search_view_by_title`, `feishu_get_view_detail`, `feishu_list_multi_project_view_workitems`, `feishu_list_charts`, `feishu_get_chart_detail`, `feishu_create_fixed_view`, `feishu_update_fixed_view` |
| Nodes/subtasks | `feishu_get_node_detail`, `feishu_update_node`, `feishu_update_node_subtask`, `feishu_get_transition_required`, `feishu_transition_node` |
| WBS | `feishu_create_wbs_draft`, `feishu_list_wbs_draft_rows`, `feishu_list_wbs_instance_rows`, `feishu_edit_wbs_draft`, `feishu_publish_wbs_draft`, `feishu_reset_wbs_draft`, `feishu_get_wbs_draft_operation_progress` |
| People/workload | `feishu_search_user_info`, `feishu_list_project_team`, `feishu_list_team_members`, `feishu_list_schedule` |
| Activity | `feishu_list_workitem_comments`, `feishu_add_comment`, `feishu_get_workitem_op_record`, `feishu_get_workitem_man_hour_records` |
| Resources | `feishu_get_resource_work_item_type_conf`, `feishu_create_resource_work_item`, `feishu_list_element_template`, `feishu_list_deliverables` |
| Files | `feishu_upload_file`, `feishu_get_download_url` |

Removed assumptions from the previous revision: there is no current
`create_work_item_from_resource`, `list_finished_info`, or `update_finished_info` tool.
