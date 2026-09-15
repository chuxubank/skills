# Teams, Users, and Workload

| Intent | Tool |
|---|---|
| List/filter teams | `feishu_list_project_team` |
| List team members | `feishu_list_team_members` |
| Resolve names/emails/user keys | `feishu_search_user_info` |
| Read personal schedule/workload | `feishu_list_schedule` |

Resolve a team name by paging `feishu_list_project_team` and matching the result; the member API
requires a team ID. Continue `feishu_list_team_members` with its returned `page_token`.

`feishu_search_user_info` accepts at most 20 names, emails, or keys. Use
`current_login_user()` to resolve the current user. Request all statuses only when inactive people
are relevant. Use returned `user_key` for work-item operations and `lark_user_id` for comment
mentions.

`feishu_list_schedule` requires `YYYY-MM-DD` start/end dates, supports at most a three-month range
and 20 users, and accepts `work_item_type_keys=["_all"]`. It returns per-user details and totals;
summarize overload/idle conclusions from the returned estimates rather than inferring from item
counts alone.
