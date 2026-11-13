# Workspace agent 任务与回报模板

协调者发送前填写全部字段。unknown 要说明由谁核实；阻塞核心身份/授权时先停，不盲派单。
模板中的评审、评论、CI 字段仅在相关任务中填写；没有对象时写“不适用/未创建”，
不可虚构 URL，也不为派单先创建平台对象。
worker 开始前读取目标项目的 AGENTS.md / CLAUDE.md，核实 cwd/branch/tip 和已有改动；
身份或写入所有权与交接不一致时停止回报，不自行切分支、覆盖目录或接手其它 writer。

## 任务正文

```text
角色：worker（执行者），不是协调者。你是此 worktree 的唯一代码写入者。
在指定 Luvus workspace 内实现、验证并回报；本交接不授权再建 worktree/agent 或递归委派。
即使加载 worktree-handoff，也只按 worker 角色执行，不重跑其协调者流程。
发现其它独立 feature/问题时先向 caller 建议拆分；后续“继续实现/修复”不改变你的角色。

对象与路由
- 工作单元标识与类型（feature/bugfix/CI/review 等）；评审 URL/编号（如有）、平台/host、仓库及 source/head 仓库：
- 已由 Worktrunk 创建/复用的绝对 cwd、branch、对应 workspace_id、pane_id、agent 名称/kind：
- 已核实基线 ref/SHA、原 tip/当前 tip、平台 source/head SHA（如适用，含查询时间）：
- 项目现有平台读取工具/认证 host（如需，不含凭据；不预设 CLI）：
- caller pane/name（同一会话，不能写成你自己的 pane）：
- 本阶段用户原话与授权：

上下文
- feature 需求/设计与预期行为、非目标；若为故障则附原始症状与复现：
- 已核实评论/CI 事实；已执行命令、结果及日志路径：
- 当前 staged/unstaged/untracked 用户改动、必须保留的文件：
- 历史拆分时：备份位置、按序移植 commit SHA、commit→问题映射：
- 已拆出的兄弟评审或分支及排除文件/提交：禁止顺手带回；依赖不清先报告。
- 项目规范与相关实现入口：

执行边界
- 本次目标与可观察验收标准（feature 列行为/兼容性/测试；故障列复现与回归）：
- 独占写入 cwd、文件/模块范围；不跨其它 worktree/ref；不改用户无关改动：
- 允许的本地操作及验证命令：
- 是否允许本地提交、历史移植生成提交、历史改写（逐项）：
- 是否允许 push、创建/更新评审、发平台评论、resolve、merge、清理（逐项）：
- 未明确允许的外部动作一律停止。默认只读评论、改代码、测试、汇报，不 commit/push。
- 评论任务：读取 references/evidence.md 的对应平台分支，全部适用反馈通道分页读完，
  逐条判断有效/已修/不适用/通知/未知；无有效技术评论则不造改动。
- CI 任务：读取 references/evidence.md 的 CI 分支，读实际失败 run/pipeline/job/log，区分基线与 feature；
  不 skip 测试/忽略 advisory/关 audit/无限重试。旧 CI 不等于当前 tip 已验证。
- Rust/live tests：遵守本模板下方的隔离约束；不停止预览或生产服务器。

完成或阻塞
- 按“回报正文”逐项反馈；无改动也是有效结果，缺权限/平台明确写未验证。
- 使用继承客户端向上面的 caller 主动回报：
  "$LUVUS_BIN_PATH" agent send "<CALLER_PANE_OR_NAME>" "done|blocked: <证据和下一步>"
- 回报失败保留结果并说明投递阻塞，不切会话、不报已送达。
```

把所需 reference 的实际可读路径/正文一起提供给 worker；不要让独立 agent 猜协调者上下文。
发送前扫描凭据、私人日志等敏感内容；只交接与任务有关的最小必要信息。

## 并行 Rust / live tests 隔离（有此类验证时必读并附入任务）

- 每个 worktree 用自己的 target；核查继承的 `CARGO_TARGET_DIR`。若指向共享目录，
  在本次验证命令里覆盖为该 worktree 内的绝对路径，不改用户全局配置。
  可限制 `CARGO_BUILD_JOBS=2`；不得把不同分支二进制安装/复制到同一共享路径。
- live tests 使用本 worktree 刚构建的精确绝对 binary，记录实际路径和 SHA；
  不调用 PATH 中可能被别的 worker 覆盖的 binary。
- 测试子进程用独立临时 `LUVUS_HOME` 和唯一 session，清除继承的 socket/session
  selectors 及 pane/caller 身份；按项目测试 harness 和已安装 CLI 的实际变量清单核实，
  包括 `LUVUS_SOCKET_PATH`、`LUVUS_API_ADDRESS`、`LUVUS_SESSION`、`LUVUS_PANE_ID`、
  `LUVUS_ENV` 等。先证明测试命令不会落到用户会话，再运行。
- 只对子进程清除/覆盖测试环境；worker 回报仍用原来继承的 `LUVUS_BIN_PATH` 和会话。
- 只清理自己创建的临时目录、session、PID/测试进程；不用全局 pkill/killall 或默认
  `server stop`。不得控制生产服务器生命周期，普通编译测试不停止用户预览。
- 无法保证隔离则停止 live tests，报告未验证和所需条件，不静默连接生产环境。

## 回报正文

```text
done|blocked: <工作单元 / 评审编号（如有） / 阶段>
- 身份：绝对 cwd、branch、workspace/agent、base/tip、平台 head（如适用）；备份/日志路径
- 逐条反馈：feature 验收项或问题/comment/thread/discussion ID、CI run/pipeline/job → 结论 → 证据/实现位置
- 改动文件及行为：无改动 / 有未提交修复 / 已获授权提交发布（列精确 SHA、回读）
- 验证：实际命令、exit code、测试数/结果、日志；本地结果与远端 CI 分开
- 未验证平台与剩余风险：含人工视觉验收边界、旧 CI、API/ref 不一致、未 resolve
- 外部操作：实际执行/未授权未执行；线程状态不能用“代码已修”替代
- Conventional Commit 建议：<只建议，不据此执行 commit>
- 下一步与所需授权：
```

长回报可存目标项目允许的报告目录并发路径/摘要，正文仍须可供协调者核对结论。
`agent send` 返回 queued 只说明报告入队，不证明对方已消费或后续发布已完成。
