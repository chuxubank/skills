# Activity Reference

Tools for reading work item comments, operation logs, and time (man-hour) records.

## Tool Map

| Intent | Tool | Key Params |
|--------|------|------------|
| 查看评论列表 | `list_workitem_comments` | `project_key`, `work_item_id`, `page_num`(optional) |
| 添加评论 | `add_comment` | `work_item_id`, `comment_content`, `project_key`(optional) |
| 查看操作记录 | `get_workitem_op_record` | `project_key`, `work_item_id` |
| 查看工时登记记录 | `get_workitem_man_hour_records` | `project_key`, `work_item_type`, `work_item_id`, `page_num`(optional) |

## Usage Notes

### add_comment

`comment_content` supports Markdown. Supports `url` parameter to auto-extract `work_item_id` and `project_key`.

### get_workitem_op_record

Supports filtering by:
- `op_record_module`: `work_item_mod`, `node_mod`, `sub_task_mod`, `field_mod`, `role_and_user_mod`, `baseline_mod`
- `operation_type`: `modify`, `create`, `delete`, `terminate`, `restore`, `complete`, `rollback`, `add`, `remove`
- `operator`: user_key list
- `start` / `end`: millisecond timestamps (max 7-day range per query)

Use `start_from` for pagination (value returned by each response).
