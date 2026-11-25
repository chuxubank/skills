# 示例与验收场景

## 触发语

- “按 worktree-handoff 把这两个 feature 分开。”
- “你做协调者，用 worktree-handoff 隔离 worktree，交给各 Luvus workspace 的 Pi。”
- “点名 worktree-handoff：给这个评审建/复用隔离 worktree，让对应 Luvus workspace 的 Pi 处理反馈，只改代码测试，不提交。”

“修这个 bug。”“把这个 loading 改一下。”“实现这个 feature。”以及继续开发，都留在当前工作区写代码，不建 worktree，不派 Luvus agent。只读的“分析原因”“看下评审”“这个方案怎么样”，以及单独的“用 wt 切分支”或 Luvus 控制命令，也不进入协调者流程。仅询问拆分方案时先做只读规划，不视为批准创建/委派/发布。

## 历史实例（只说明判断，不是实时事实或固定编号路由）

| 对象 | 当时事实与路由 | 合格回报 |
|---|---|---|
| #524 difftastic Draft | 四路评论只有通知、无有效技术建议 | 114 tests 通过、无改动；Draft 不擅自转 ready |
| #525 | 已有 follow-up 覆盖反馈 | 复用已有评审，列覆盖提交，不重复实现或另开评审 |
| #526 滚动 review | 有效问题仍需真实修复 | 对应 workspace Pi 修复，报告剩余视觉边界 |
| #527 viewed toggle | 独立问题 | 独立分支/worktree，不带回滚动或 difftastic 改动 |
| 公共 CI | 另建 `fix/ci-audit-browser` worktree | 对应 workspace Pi 读失败日志、验证公共根因并修复 |

使用时一律重新核实评审、分支、评论和 CI；不从本例推出授权，不写死个人路径/会话。

## 文档验收清单

维护本 skill 或评估一次执行时，逐项走读以下输入→预期，不需要启动真实 worker 或操作托管平台：

| 输入/故障 | 预期行为 |
|---|---|
| 没有 worker 交接时用户说“修这个 bug”或“改一下”，未点名 worktree-handoff、协调者或隔离 worktree | 留在当前工作区写代码；不建 worktree，不派 Luvus agent |
| 用户点名 worktree-handoff，或明确要协调者隔离 worktree 并委派 | 进入协调者：先 Worktrunk 隔离，再派给该路径的 Pi；不在共享工作区改 |
| 只读分析、看评审、只用 wt 切分支 | 不建 worktree、不派 Pi |
| 用户让当前 agent 协调两个新 feature、委派 Luvus Pi | 按可独立验收的工作单元拆分，先按 worktrunk 建/复用 worktree，再匹配 workspace/agent；无已有历史时跳过历史拆分 |
| worker 已在目标 worktree，收到“实现 feature”或“继续修” | 保持 worker，本地实现验证并回报，不加载/重跑协调者流程，不要求用户再确认委派 |
| worker 读到本 skill/交接模板，或 prompt 含旧的委派授权 | 文档与转发授权不改变角色，不递归创建 worktree/agent |
| worker 发现第二个 feature/无关 bug | 向 caller 建议另行安排，自己不扩大范围或再委派 |
| agent 在 worktree 中，但用户明确要求它改为协调者并另开执行者 | 允许通过角色门禁；先交清原写入所有权，避免两个 writer |
| 只知道 cwd 是 worktree，角色信息缺失 | 不据此判为 worker 或协调者；依据当前授权与交接判定，确实不清才澄清 |
| 用户点名本 skill 后要求修复，只授权改代码和测试 | 先按 worktrunk 建/复用 worktree，再匹配 workspace 并给 agent 派单；协调者不修代码，不自动发布 |
| 仓库已有平台读取工具 | 沿用该工具与 host；不套用另一平台的参数 |
| 用户给出缺陷单、需求单或其它任务链接 | 先按该对象的实际类型回读身份、范围和状态，再盘点本地并决定复用或新建；解析不到就阻塞，不凭标题或编号建分支 |
| 无评审的独立任务 | 跳过平台取证，先 Worktrunk 后对应 workspace agent，不为派单先创建评审 |
| 只有一个共享原工作区 workspace | 先用 Worktrunk 建隔离工作树，再定位/打开该路径 workspace，不能先派单再补隔离 |
| 已有独立评审、已有 follow-up 或已有 worktree | 核实并复用，不重复开评审、不重复检出 |
| 新建 branch 或 pane | 名字能读出工作单元；已有 branch/pane 保持原名，不用随机串或纯编号 |
| 用户 staged + unstaged + untracked 混合改动 | 保留现场；拆分前完整备份且各项有归属 |
| 拆分要 cherry-pick 但未授权生成提交 | 停止确认或仅准备未提交 diff，不悄悄生成提交 |
| 移植依赖 feature 的模型/docs | 由目标 Pi 做最小适配或报告依赖，不能全带回 |
| 发布历史需改写 / lease 不匹配 | 先解释并取授权；精确 lease；不匹配停止 |
| hooks 待审批 / 路径被占用 | 按 worktrunk skill 交给用户审阅或报告冲突；不代批、不覆盖占用目录 |
| post-start 已建 workspace / hook 尚在进行 | 精确 cwd/id 复用 / 澄清状态，不抢建重复 workspace |
| managed pane 同时存在 debug/生产会话 | 按 luvus skill 沿用继承会话，不切默认 |
| 目标 pane 是协调者 / busy Pi | 目标 workspace 内按 luvus skill 另开 pane / 暂停该项，不给自己任务或覆盖 busy |
| Luvus 报告名字已被占用 | 按 luvus skill 处理该 pane 的别名；不当作已有 writer，不新建 pane、不改名绕过、不换 session |
| 启动已就绪 / 发送已入队 | 按 luvus skill 接受身份或投递证据，然后结束；不循环查状态、不当完成 |
| 启动失败、发送响应丢失 | 报告阻塞/核实是否入队，不自己修、不盲重发 |
| 普通评论无问题，但 inline thread/discussion 有有效问题 | 完整读取该平台所有适用反馈通道后修复，不只看评论摘要 |
| 所有适用通道只有通知 / 机器人建议不适用 | 无改动完成 / 给具体理由，不造改动 |
| CI 摘要红叉或旧 tip 的失败 | 获取真实 run/job/log 和 SHA，不能凭摘要修或宣称新 tip 绿 |
| 多 Rust worker / live tests | 独立 target、精确 binary、测试 HOME/session，生产回报环境不变 |
| worker 未回报 / 回报有未解决视觉边界 | 标未完成 / 保留未验证事实，不虚报全部完成 |
| 用户后续授权 commit/push | 发给同一 owner，由它重新核实状态并执行授权阶段 |

检查 frontmatter 的 name 与目录一致、description 正反触发边界明确、所有相对链接可达；
文档检查通过不等于已做真实评审、CI 或 live-test 验证。
