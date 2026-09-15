# Comments, History, and Man-hours

| Intent | Tool |
|---|---|
| List comments | `feishu_list_workitem_comments` |
| Create/update comment | `feishu_add_comment` |
| Read operation history | `feishu_get_workitem_op_record` |
| Read man-hour records | `feishu_get_workitem_man_hour_records` |

## Comments

`feishu_add_comment` requires `project_key` and `work_item_id`. Set `action="create"` (default) with
Markdown `content`, or `action="update"` with `comment_id`. A call carries either `content` or
`file_token`, not both. Resolve mentions with `feishu_search_user_info` and use the returned
`lark_user_id` in the documented mention block. Upload comment files/images first as described in
`attachments.md`.

## Operation history

`feishu_get_workitem_op_record` supports module, operation, time, source, operator, and operator-type
filters. `start` and `end` are epoch milliseconds. Continue pagination with the returned
`start_from`; do not invent a fixed page-number rule.

## Man-hours

`feishu_get_workitem_man_hour_records` requires the space and item ID; provide the work-item type
when known. It paginates by `page_num`.
