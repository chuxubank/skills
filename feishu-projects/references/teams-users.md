# Teams & Users Reference

Tools for looking up team information, team members, user details, and personal schedules.

## Tool Map

| Intent | Tool | Key Params |
|--------|------|------------|
| 查看空间团队列表 | `list_project_team` | `project_key`, `query`(optional) |
| 查看团队成员 | `list_team_members` | `project_key`, `team_id` |
| 查看用户信息（名称/邮箱/key 转换） | `search_user_info` | `user_keys` (name, email, or user_key; max 20) |
| 查看排期 / 工作量 | `list_schedule` | `project_key`, `user_keys`, `start_time`, `end_time`, `work_item_type_keys`(optional) |

## Usage Notes

### search_user_info

Use this to convert a display name or email to a `user_key` before passing it to create/update tools.

```
search_user_info(user_keys=["张三", "zhangsan@example.com"])
```

Pass `user_keys=["current_login_user()"]` to look up the currently logged-in user.

### list_project_team

`list_project_team` does not support direct name lookup — use `query` as a keyword filter, then match by name from the returned list.

### list_schedule

- `start_time` and `end_time` must be in `YYYY-MM-DD` format.
- Maximum range: 3 months.
- Pass `work_item_type_keys=["_all"]` to include all work item types.
- Returns per-user workload detail including node schedules, subtask times, and unscheduled task counts.
