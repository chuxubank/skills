# Views & Charts Reference

Tools for browsing views (视图) and inspecting embedded charts (图表).

## Tool Map

| Intent | Tool | Key Params |
|--------|------|------------|
| 按名搜索视图 | `search_view_by_title` | `project_key`, `view_scope`, `key_word` |
| 查看视图详情 / 工作项列表 | `get_view_detail` | `view_id`, `project_key`(optional), `fields`(optional) |
| 查看视图下图表列表 | `list_charts` | `project_key`, `view_id` |
| 查看图表详情 | `get_chart_detail` | `chart_id`, `project_key`(optional) |
| 创建固定视图 | `create_fixed_view` | `project_key`, `work_item_type`, `work_item_id_list`, `name` |
| 更新固定视图（添加工作项） | `update_fixed_view` | `project_key`, `view_id`, `work_item_type`, `add_work_item_ids` |
| 更新固定视图（移除工作项） | `update_fixed_view` | `project_key`, `view_id`, `work_item_type`, `remove_work_item_ids` |

## `view_scope` Values for `search_view_by_title`

| Work Item Type | view_scope |
|----------------|------------|
| 需求 (story) | `storyView` |
| 缺陷 (issue) | `issueView` |
| 版本 | `version` |
| 自定义类型 | `<work_item_type_key>` |

## Usage Notes

- `get_view_detail` returns the work item list inside the view. Pass `fields` to control which columns are returned.
- `update_fixed_view` cannot add and remove items in the same call — use separate calls.
- `create_fixed_view` has a limit of 200 work item IDs per call.
