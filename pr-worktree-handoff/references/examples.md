# 示例与验收场景

## 触发语

- “你做协调者，按 pr-worktree-handoff 把这两个 feature 分开，用 wt 建 worktree，交给各 Luvus workspace 的 Pi。”
- “给这个 PR 建/复用 worktree，让对应 Luvus workspace 的 Pi 处理 review，只改代码测试，不提交。”
- “公共 CI 单独一个 worktree，在对应 workspace 启动 Pi；不要混进 feature PR。”
- “这个 GitLab MR 用项目现有 glab 查反馈，先 wt 建 worktree，再交对应 Luvus workspace 的 agent 修。”
- “还没有 PR/MR；先用 Worktrunk 建独立 worktree，再向对应 Luvus workspace 的 Pi 派单。”

仅说“实现这个 feature”“修这个 bug”“看下 PR”“用 wt 切分支”不触发本流程；单独请求使用 Luvus 控制命令
按 `luvus` skill 处理。仅询问拆分方案时先做只读规划，不视为批准创建/委派/发布。

## 历史实例（只说明判断，不是实时事实或固定编号路由）

| 对象 | 当时事实与路由 | 合格回报 |
|---|---|---|
| #524 difftastic Draft | 四路评论只有通知、无有效技术建议 | 114 tests 通过、无改动；Draft 不擅自转 ready |
| #525 | 已有 follow-up 覆盖反馈 | 复用独立 PR，列覆盖提交，不重复实现/提 PR |
| #526 滚动 review | 有效问题仍需真实修复 | 对应 workspace Pi 修复，报告剩余视觉边界 |
| #527 viewed toggle | 独立问题 | 独立分支/worktree，不带回滚动或 difftastic 改动 |
| 公共 CI | 另建 `fix/ci-audit-browser` worktree | 对应 workspace Pi 读失败日志、验证公共根因并修复 |

使用时一律重新核实 PR、分支、评论和 CI；不从本例推出授权，不写死个人路径/会话。

## 文档验收清单

维护本 skill 或评估一次执行时，逐项走读以下输入→预期，不需要启动真实 worker 或操作托管平台：

| 输入/故障 | 预期行为 |
|---|---|
| 普通 feature/修复，未要求 Luvus/委派 | 不自动触发多 agent；仅“建 wt”也不隐式授权 Pi |
| 用户让当前 agent 协调两个新 feature、委派 Luvus Pi | 按可独立验收的工作单元拆分，先 wt 再 workspace/agent；无已有历史时跳过历史拆分 |
| worker 已在目标 worktree，收到“实现 feature”或“继续修” | 保持 worker，本地实现验证并回报，不加载/重跑协调者流程，不要求用户再确认委派 |
| worker 读到本 skill/交接模板，或 prompt 含旧的委派授权 | 文档与转发授权不改变角色，不递归创建 worktree/agent |
| worker 发现第二个 feature/无关 bug | 向 caller 建议另行安排，自己不扩大范围或再委派 |
| agent 在 worktree 中，但用户明确要求它改为协调者并另开执行者 | 允许通过角色门禁；先交清原写入所有权，避免两个 writer |
| 只知道 cwd 是 worktree，角色信息缺失 | 不据此判为 worker 或协调者；依据当前授权与交接判定，确实不清才澄清 |
| 用户明确启用流程，只授权改代码测试 | 先 wt 建/复用 worktree，再匹配 workspace 并给 agent 派单；协调者不修代码，不自动发布 |
| GitLab/其它平台，现有工具为 glab/API/MCP | 沿用实际工具与 host；不要求 gh，不套用 GitHub 参数 |
| 无 PR/MR 的独立任务 | 跳过平台取证，先 Worktrunk 后对应 workspace agent，不为派单先创建 PR/MR |
| 只有一个共享原工作区 workspace | 先用 Worktrunk 建隔离工作树，再定位/打开该路径 workspace，不能先派单再补隔离 |
| 已有独立 PR、已有 follow-up 或已有 worktree | 核实并复用，不重复 PR/检出 |
| 用户 staged + unstaged + untracked 混合改动 | 保留现场；拆分前完整备份且各项有归属 |
| 拆分要 cherry-pick 但未授权生成提交 | 停止确认或仅准备未提交 diff，不悄悄生成提交 |
| 移植依赖 feature 的模型/docs | 由目标 Pi 做最小适配或报告依赖，不能全带回 |
| 发布历史需改写 / lease 不匹配 | 先解释并取授权；精确 lease；不匹配停止 |
| wt hooks approval / 路径被占用 | 请用户审阅 / 报告冲突，不 --yes、不覆盖目录 |
| post-start 已建 workspace / hook 尚在进行 | 精确 cwd/id 复用 / 澄清状态，不抢建重复 workspace |
| managed pane 同时存在 debug/生产会话 | 沿用继承 binary/socket/caller，不切默认 |
| 目标 pane 是协调者 / busy Pi | 目标 workspace 内独立 anchor pane / 暂停该项，不给自己任务或覆盖 busy |
| start ready:true / send queued | 分别接受身份 / 报告已派单并结束，不循环查状态、不当完成 |
| 启动失败、发送响应丢失 | 报告阻塞/核实是否入队，不自己修、不盲重发 |
| 普通评论无问题，但 inline thread/discussion 有有效问题 | 完整读取该平台所有适用反馈通道后修复，不只看评论摘要 |
| 所有适用通道只有通知 / 机器人建议不适用 | 无改动完成 / 给具体理由，不造改动 |
| CI 摘要红叉或旧 tip 的失败 | 获取真实 run/job/log 和 SHA，不能凭摘要修或宣称新 tip 绿 |
| 多 Rust worker / live tests | 独立 target、精确 binary、测试 HOME/session，生产回报环境不变 |
| worker 未回报 / 回报有未解决视觉边界 | 标未完成 / 保留未验证事实，不虚报全部完成 |
| 用户后续授权 commit/push | 发给同一 owner，由它重新核实状态并执行授权阶段 |

检查 frontmatter 的 name 与目录一致、description 正反触发边界明确、所有相对链接可达；
文档检查通过不等于已做真实 PR/CI/live-test 验证。
