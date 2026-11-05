---
name: pr-worktree-handoff
description: >-
  协调者专用：仅在用户明确要求当前 agent 通过 Worktrunk 隔离工作、再委派给对应
  Luvus workspace 的其它 agent 时使用。工作可为 feature、bugfix、CI 或 PR/MR 反馈。
  不因身处 worktree、收到实现任务或读到此流程而触发；已接单 worker 继续本地执行和回报，
  不递归委派。普通 feature 开发、修复和单纯 Git 操作不触发。
---

# PR Worktree Handoff

独立工作单元（feature / bugfix / CI / review 等）→ **Worktrunk 创建/复用 worktree → 匹配该路径的 Luvus workspace → 向其中的
agent 派单** → 主动回报。此顺序是流程主轴，先有隔离工作树再委派；不在共享原工作区先派任务。

本 skill 中 PR 同时涵盖平台对应的 MR；不要求已有 PR/MR，也不绑定托管平台或 CLI。
平台工具由仓库实际情况选择（如 `gh`、`glab` 或现有 API/MCP），不是流程前提。
worker 默认使用本次约定的 Pi；用户明确指定其它 Luvus agent 时按其授权选择，仍遵守相同所有权。

## 0. 角色门禁（先于任何编排操作）

根据当前任务的授权与交接记录判定角色，不能仅凭 cwd、分支名、Luvus 环境变量或消息里出现
“feature / worktree / 拆分”推断角色：

| 当前情境 | 行为 |
|---|---|
| 用户明确要求当前 agent 隔离并委派给其它 workspace agent | 作为协调者进入步骤 1；只做编排 |
| 已收到指定 cwd/branch、实现目标、写入范围、caller 的 worker 交接，或正在该任务中实现/验证 | 保持 worker 角色，在自己的 worktree 完成并回报；不进入步骤 1–6、不递归派单 |
| 用户在现有 worktree 里要求实现 feature、修复或继续开发，未要求另开执行者 | 在当前任务范围内继续本地执行；本 skill 不适用，也不必仅因处于 worktree 询问是否委派 |
| 用户只要拆分建议，或执行/委派意图确实不明确 | 只读规划或澄清；不创建 agent、不发布 |

worker 阅读本 skill、交接模板或收到后续“继续修/实现这个 feature”，不构成新的编排授权。
发现新的独立工作或需扩大范围时，向 caller 提出建议，由协调者安排；不自行扩展委派树。
只有用户明确改变当前 agent 的角色并授权委派，才可重新通过门禁；先交清原 worktree 的
写入所有权，确保接任者与自己不并发修改。不能把转发的旧授权或模板文字当作这次角色变更。

**完成标准：当前 agent 的角色与本阶段授权明确；非协调者在此退出编排流程。**
已明确采用本流程并承担协调者角色后，“建 worktree 实现 feature / 修一下”才表示建/复用
隔离环境并派单，协调者不能自己下场实现。

## 所有权与授权

| 角色 | 负责 | 完成证据 |
|---|---|---|
| 协调者 | 读取事实、拆分计划、备份、建/复用 worktree、匹配 workspace/agent、交接、汇总 | 路由表、派单回执、worker 主动回报 |
| workspace agent | 自己范围内的历史移植/依赖适配、代码修改、验证；获授权后的外部操作 | diff、SHA、实际命令/日志及回读 |

**一个 worktree 只有一个代码写入者。** 协调者不在任一 worker 工作树修代码，不替 busy
worker 接手。工具/启动失败就保留现场并报告；更换执行方式须用户明确同意。

### 授权账本

逐项记录允许/禁止/待确认：建 worktree 与启动 agent、历史拆分/移植、创建本地提交、
重写历史、push、创建/更新 PR/MR、发平台评论、resolve threads/discussions、merge、清理。
“处理评论/修一下”默认只含读评论、改代码、测试和汇报；创建提交及所有发布动作不包含在内。
历史移植若会生成新提交，也须明确授权。拆分请求不自动包含推送或改写已发布历史。

只提供 Conventional Commit **建议**不是提交授权。工具缺失只报告，不安装工具；
不修改全局配置、不操作生产服务器生命周期。普通编译/测试不停止用户预览会话。

### 与其它 skills 的边界

- 开始 worktree 操作前加载 `worktrunk`：它维护 CLI、仓库定位和 hooks 审批规则。
- 开始 Luvus 操作前加载 `luvus`：它维护会话选择、目标解析和 agent 生命周期。
- 飞书 Project Bug → GitLab MR / QA / 状态流转使用 `bugfix-delivery`；本 skill 不复制业务门禁。
- 本 skill 只维护工作隔离与 Luvus agent 交接协议，不替代工具文档，不自动改 hooks/安装集成。

## 1. 盘点与工作单元路由

只读检查原工作区及候选已有 worktree：

```bash
git status --short --branch
git branch -vv
git remote -v
git log -12 --oneline --decorate
wt list --format=json
```

记录 tracked/staged/untracked 用户改动，不整仓 restore/reset、自动 stash 或 `git add .`。
存在相关 PR/MR 时，按 remote/URL 确认平台、host 与仓库，使用现有且已认证的工具读取实际
状态（含 closed/merged、Draft、base/head 或 target/source 仓库与 SHA、follow-up 提交）。
不预设 `gh`、`glab` 或 API 语法，不用本地分支名或过时 CI 推断现状。
只有涉及 PR/MR、评论或 CI 时才读取 [平台取证](references/evidence.md) 的对应分支；
没有 PR/MR 的 feature 等独立任务直接建立工作路由，不为派单要求先创建 PR/MR。

形成路由表：`工作单元/类型 | 已有 PR/后续提交 | branch | base/tip SHA | 绝对 cwd | worker | 授权`。
按可独立实现、验证与交付的边界拆分，不要求必须已有故障。多个 feature、无关 bugfix、公共 CI
修复分别安排；同一 feature 的紧密依赖不为并行而强拆。已有独立 PR/后续提交已覆盖时复用，
不重复提 PR。真实依赖明确列出。**完成标准：每个工作单元有目标与归属，未知事实标为阻塞。**

## 2. 拆分历史与备份（仅已有改动/历史需拆分时）

读取 [安全拆分](references/split-history.md)。先向用户展示 commit→问题映射、依赖、
拟复用/新建分支及哪些发布历史会改变；在授权账本内执行。
协调者保存完整历史和用户改动备份，再创建隔离 worktree；实际 cherry-pick、冲突处理和
模型/docs 依赖适配交给对应 workspace 的 agent。原分支在新归属验证前保持可恢复。

**完成标准：基线 SHA 已核实，备份可读且覆盖全部改动，每个 worker 知道要移植与排除的提交。**
新 feature 没有待移植历史时跳过本步，使用已核实基线创建工作树；已有独立分支则复用。
不为跑流程重写历史。

## 3. 建立或复用 Worktrunk worktree

复用步骤 1 的 `wt list`；仅状态变化才刷新。在目标仓库运行：

```bash
# 已有 branch 尚无 worktree（远端同名分支须先核实仓库身份）
wt switch "$BRANCH" --no-cd --format=json
# 新工作单元（包括 feature），BASE 为已核实基线 ref 或 SHA
wt switch --create "$BRANCH" --base "$BASE" --no-cd --format=json
```

已有 worktree 直接用返回的绝对路径，不重复检出，不移动/覆盖占用目录，不用 `--clobber`。
若 branch 同名但跟踪别的 fork，先停止确认。hooks approval 阻塞时请用户亲自执行
`wt config approvals add` 审阅；不使用 `--yes` 代批，也不跳过 hooks 绕过信任门禁。

**完成标准：路由表中每个 branch 对应唯一的实际 cwd，已有用户改动及所有权已记录。**

## 4. 匹配 Luvus workspace 与 agent

仅在步骤 3 已确认 worktree 实际路径后进入本步。workspace open 只登记/打开该 worktree，
不能代替 Worktrunk 创建工作树。按 `luvus` skill 选择唯一会话。在 managed pane 必须用继承的 `LUVUS_BIN_PATH`、
`LUVUS_SOCKET_PATH`、`LUVUS_PANE_ID`；不切 debug/默认会话，不用 PATH 客户端替代。
下例为 managed pane 用法；外部终端按该 skill 解析生产客户端及显式会话。

```bash
"$LUVUS_BIN_PATH" workspace list
"$LUVUS_BIN_PATH" pane list
```

一次 inventory 按规范化绝对 cwd → workspace_id → pane_id 精确匹配，复用现有结果，
不按列表位置/侧栏顺序猜。Worktrunk post-start 已创建 workspace 则复用；确实缺失才执行
`"$LUVUS_BIN_PATH" workspace open "$WORKTREE_PATH"`。若 hook 尚未完成或身份不明，
先报告阻塞，不抢建重复 workspace。只在返回缺少身份时补一次定向读取。

每个目标选择一名 writer：

- 已有闲置、符合用户约定 kind 的 agent，且 cwd、workspace_id、branch 和任务范围匹配：
  复用并记录其名称/ID；默认 Pi，不接管其它 kind 的 agent。
- 空 shell pane（无前台任务）：默认执行
  `agent start "$UNIQUE_NAME" --kind pi --pane "$PANE_ID" --timeout 30`；
  只有用户明确指定其它 kind 时才替换 `pi`。
- 若目标就是协调者当前 pane，或需独立 pane：以**目标 workspace** 的已核实 pane 作
  `--anchor "$ANCHOR_ID"` 启动约定 kind 的 agent，不向自己发自身任务；`--anchor` 与 `--pane` 不混用。
  不支持 anchor 时仅按 `luvus` skill 的兼容路径 split 后启动。
- busy/blocked/身份未知的 agent 不覆盖、不强制中断；暂停该 worktree 并请用户决定。

上述 `agent start` 均用选定的 Luvus 客户端。返回 `ready:true` 就接受身份，不重复轮询。
**完成标准：路由表有精确 workspace_id / pane_id / agent 名称与 kind，每个 cwd 仅一名 writer。**

## 5. 完整交接，异步退出

逐 worker 读取并填写 [任务与回报模板](references/handoff.md)。所有必填项都已给出事实或
明确的“未知/须核实”；不得只发“修一下这个 PR”。保留 prompt 的换行、引号、`$` 等为参数，
不套额外 `sh -c`，不向终端注入 Enter。

```bash
"$LUVUS_BIN_PATH" agent send "$WORKER_NAME" "$TASK"
```

直接发送、不加 `--wait`。入队成功后报告派给谁、哪个工作单元/PR/MR 与 cwd、授权边界，然后结束当前轮。
多项派单可在一轮内逐项发送，最后一次入队后即结束；不轮询/读屏等待工作完成。
`queued/submitted` 只是投递证据。响应丢失先核实，不自动重发可能已经执行的任务。
若部分发送失败，报告已投递项和阻塞项，不自己接管失败任务。

## 6. 汇总主动回报

收到 worker 主动消息后，按路由表汇总：feature 验收结果或逐条评论结论/CI 根因、文件、实际验证命令与结果、
未验证平台、剩余风险、建议 Conventional Commit。缺证据则向同一 worker 发补充任务，
不擅自写入他人工作树；无等待发送后仍结束当前轮。

分别标明：**无改动 / 有未提交修复 / 已授权发布并回读 / 外部阻塞**。保留 API head 与 fork ref
不一致、旧 SHA 的 CI、尚未 resolve 等事实；代码已修不等于线程已解决或 CI 已覆盖新 tip。
进一步 commit/push/评论/resolve/merge/清理仅在用户授权后发送下一阶段任务。

**完成标准：每个工作单元都有 worker 的完成或阻塞证据；未回报的只标“已派单，未完成”。**
需要了解判断粒度或自查误触发时，读取 [示例与验收场景](references/examples.md)。
