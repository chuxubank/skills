# 按平台取证（仅涉及评审、评论或 CI 时读取）

本文件定义要取得的事实，不指定平台 CLI。工作流始终先经 Worktrunk 建立/复用 worktree，
再向对应 Luvus workspace 的 agent 派单；平台取证不能变成委派流程的工具绑定。

## 选择实际平台与读取工具

1. 从 remote、用户 URL 和项目规范确定 host、项目及 source/head 与 target/base 仓库身份；
   区分云服务、自托管实例和 fork，不凭口头对评审的叫法猜平台。
2. 复用项目现有且已认证的读取工具。不为此安装工具或切换全局默认 host/账号。
3. 查对应 skill/实际版本帮助，确认只读命令、分页和字段覆盖。能力不足时补用同平台 API，
   不把不同 CLI 的参数互换；认证/权限/分页失败明确报告阻塞。
4. 输出任务实际需要的事实，不要求协调者或 worker 机械调用某个固定命令。
   没有相关评审或 CI 的独立任务跳过本文件，不为满足模板制造平台对象。

## 评审身份与复用（协调者）

取得 URL/编号、host/项目、open/closed/merged、Draft、target/base 与 source/head 分支、
两侧仓库及 SHA、commits/follow-up、更新时间。查询相关分支所有状态的现有评审，
完整分页查重；不能只看 open 项或截断列表。

核对实际 fork/source ref、平台返回的 source/head SHA、本地 tip。已有独立评审或
follow-up 已覆盖反馈时复用；merged/closed 不是重开/新建授权。记录查询时间，
后续 CI 绑定具体 SHA。对象不存在或平台不可读时如实标记，不能虚构 URL 或“已更新”。

## 完整评论与讨论（评论 worker）

先列出该平台实际有哪些反馈通道，再全部分页读取、关联和去重。CLI 的摘要或普通评论
命令通常不含完整行内讨论；“命令成功”不代表覆盖全部反馈。

| 平台分支 | 必须覆盖的反馈 |
|---|---|
| GitHub | 普通 issue comments、reviews、REST inline review comments、GraphQL reviewThreads（含 resolved/outdated） |
| GitLab | 评审上的普通 notes、discussions 及其中全部 notes/replies；覆盖行内 diff 位置、resolved/resolvable 状态与 review/approval 反馈（如有） |
| 其它平台 | 普通评论、review/评审反馈、行内讨论及回复、解决/过期状态的对应资源 |

GitHub 的 reviewThreads 与嵌套 comments、GitLab 的 discussions 与嵌套 notes，以及
其它平台的嵌套回复均核实是否完整；顶层分页不等于嵌套数据完整。不适用的通道说明原因，
工具未暴露/无权限的通道标为未读取，不能当作空数据。

每条保存 URL/ID、作者、路径/行、commit、解决/过期状态及上下文，逐条核实：

| 结论 | 所需证据 | 动作 |
|---|---|---|
| 有效 | 当前 tip 可定位的技术问题/复现或明确推理 | 最小修复、针对性测试 |
| 已修 | 覆盖它的 commit SHA、当前代码及验证 | 报告并复用，无重复补丁 |
| 不适用 | 与设计/实际语义冲突的具体理由 | 记录理由，不盲从机器人 |
| 通知/无有效技术评论 | 全部适用通道完整读取后只有通知等内容 | 无改动也正常完成 |
| 尚不能判定 | 缺复现、权限或上下文 | 报告阻塞，不造改动 |

outdated/resolved 不自动等于已修，机器人建议也不自动等于正确。
逐条输出结论与证据；视觉边界需人工/平台验收时明确列出。默认只做内部回报，
不自动发平台评论或 resolve；获得授权后执行对应操作并回读真实状态。

## 实际 CI 故障（CI worker）

1. 用实际平台工具读取失败的 run/pipeline、attempt、job、step 与原始日志；保存 URL/ID、
   source/head SHA、merge-result SHA（如有）、workflow/event 或 pipeline source。
   区分分支 CI 与合并结果 CI；summary/红叉不是根因证据。
2. 对比已核实上游基线的相同 job/log，必要时在独立基线环境复现。
   证据不足只能说“疑似公共问题”，不能归咎 feature 或宣称基线已坏。
3. 公共故障单独路由到 CI 分支/worktree；feature 引入的故障归 feature owner。
   路由改变交协调者按 Worktrunk → Luvus workspace → agent 顺序派单，worker 不跨树修兄弟问题。
4. 保留 advisory ID、受影响版本、测试失败输出与修复验证。
   不靠 skip 测试、忽略 advisory、关 audit 或无限重试变绿。
5. 本地验证与平台 CI 分开报告。旧 SHA、尚未重跑或平台 head 未更新的 CI 不冒充新 tip 验证。
   新 run/pipeline、重跑或 retry job 也是外部操作，先核实授权，不循环等待或自动重跑。
