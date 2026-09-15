# Views and Charts

| Intent | Tool | Notes |
|---|---|---|
| Find view by title | `feishu_search_view_by_title` | requires space, scope, keyword |
| Read ordinary view items | `feishu_get_view_detail` | accepts URL or view ID |
| Read panorama view items | `feishu_list_multi_project_view_workitems` | use for URLs containing `multiProjectView` |
| List charts in a view | `feishu_list_charts` | accepts URL or explicit locator |
| Read chart | `feishu_get_chart_detail` | accepts URL or chart ID |
| Create fixed view | `feishu_create_fixed_view` | at most 200 item IDs |
| Add/remove fixed-view items | `feishu_update_fixed_view` | one direction per call, at most 200 IDs |

For `feishu_search_view_by_title`, pass the actual `view_scope` required by the space/type; resolve
custom type keys with `feishu_list_workitem_types` instead of assuming a display-name mapping.

`feishu_get_view_detail` supports field selection and page numbers. Panorama views use their own
API and return 50 items per page. Continue only when the user requests complete results or the
response indicates more data is needed.
