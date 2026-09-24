---
name: bugfix-delivery
description: >-
  交付飞书 Project Bug 的个人工作流。用于分析或接管已修复 Bug、用 Worktrunk
  创建独立分支/worktree，并强制通过 Luvus pane 中的 Pi 完成后续修复、验证、提交、
  GitLab MR、Bug 评论与状态流转、合并和清理。用户说“走一下 Bug 流程”“已修复但没建
  wt/分支”“QA 已验收，检查门禁后合并、补充合入记录、移除 wt”时使用。
---

# Bugfix Delivery

完成飞书 Bug 从代码到 GitLab、测试和回归的交付闭环。分支、目标分支、空间、人员、
状态和 transition ID 全部从当前事实解析；示例中的变量均为占位符。

## 所有权：主 Agent 只派单

主 Agent 只负责建立或复用安全的 Worktrunk worktree、把已有修复迁入、在该 worktree 启动或
复用一个 Luvus Pi agent，并通过一次无等待 `agent send` 下发完整阶段任务。发送成功后立即结束
当前轮次，不等待 worker、不轮询 pipeline/QA/MR，也不自行操作 GitLab、Meegle 评论或状态。

worktree Agent 是交付 owner，负责解析 Bug 管理类型、修改和验证代码、提交/push、创建或更新
MR、检查 pipeline 和 QA 门禁、合并、Meegle 评论与状态流转、回读验收以及获授权后的清理。
每次只执行用户已授权的阶段；遇到 pipeline、QA、合并授权或其它外部门禁时，向主 Agent 报告
当前成果、阻塞条件和下一条建议指令后保持现场，不用主 Agent 在线等待。用户之后推进流程时，
主 Agent 只把下一阶段任务发送给同一 worktree Agent；worker 必须重新读取实时状态再继续。

## 先按 Bug 管理类型分流

`work_item_attribute.template` 是 **Bug 管理类型**，必须从工作项回包读取其 `id` 和
`name`；不要把工作项类型 `bug` 或普通字段误当作管理类型。必要时用
`workitem meta-fields --field-query '管理类型'` 校验实时模板选项。

当前空间已确认的两类：

| 模板 ID | Bug 管理类型 | 交付路径 |
|---|---|---|
| `4901968` | `默认bug 管理类型` | 目标为 `develop` 时先合并 MR；合并验证通过后才评论 @ 测试并流转到实时返回的 `RESOLVED` |
| `10537728` | `CB3 客户端 bug 流程` | 合并前由开发侧评论 @ 测试并流转“已解决待验证”；QA 负责验收结论和“已验证待合入”流转，开发侧回读门禁后再合并 |

ID 与名称必须同时记录。若两者与实时配置冲突，以实时 `template.id` 和元数据选项为准并停止
自动流转；未识别模板不得套用任一流程，先向用户确认。

## 完成阶段

### 默认 Bug 管理类型 → develop

1. **MR 就绪**：Worktrunk worktree、Luvus Pi 修复与验证、提交、MR 和 pipeline 门禁。
   此时不在 Bug 下评论、不 @ 测试、不修改 Bug 状态。
2. **合并待验证**：取得合并授权后合并 MR，验证提交已进入 `origin/develop`；随后添加
   “已合入 develop”评论并 @ 测试，再将 Bug 流转到实时返回的 `RESOLVED`。
3. **清理**：评论和状态回读成功后，按授权移除 worktree；后续测试结论按该模板实时状态流处理。

### CB3 客户端 Bug 流程

1. **待验证**：MR 和 pipeline 就绪后，开发侧评论 @ 测试并流转“已解决待验证”；MR 暂不合并。
2. **等待 QA**：QA 记录验收结论并流转“已验证待合入”。开发侧只回读评论和状态，不代替 QA
   更新验收结论或执行该流转。
3. **待回归**：仅在已回读确认 QA 验收通过且当前状态为“已验证待合入”后，取得合并授权并
   合并 MR；验证目标分支，执行合并后的开发侧动作，再清理 worktree。

其它模板由 worktree Agent 读取其实时状态流；需要用户选择时报告阻塞并停止该阶段。每一步以
worker 的回读结果为完成标准。主 Agent 只接收 worker 主动回报，不等待或重复验收。

## 1. 派单要求：由 worktree Agent 解析 Bug

主 Agent 向 worktree Agent 传入原始 Bug URL；worker 加载 `meegle` skill，执行 URL decode、
Auth Guard 和工作项查询：

```bash
meegle url decode --url "$BUG_URL" --format json
meegle auth status --format json
meegle project search --project-key "$SIMPLE_NAME" --format json
meegle workitem get --project-key "$PROJECT_KEY" --work-item-id "$BUG_ID" \
  --fields _all --params '{"page_size":100}' --format json
```

worktree Agent 保存 Bug 标题、描述、优先级、当前状态、工作项类型、报告人，以及
`work_item_attribute.template.id/name`。后者就是 **Bug 管理类型**；按上面的模板表选择流程，
不要从标题、目标分支或工作项类型猜测。默认以**报告人作为测试人员**；用户显式指定测试人员
时使用指定人员。只有流程到达 @ 测试的阶段时，才通过 `meegle user search` 将 user_key 转换成
`lark_user_id`，供评论中的真实 @ mention 使用。

## 2. 主 Agent 只确认隔离边界

主 Agent 检查当前工作区、现有 worktree 和分支，只为安全迁移与派单确定目标位置。若多个改动
混在一起，先明确哪些文件属于 Bug。保护其它改动，不使用整仓 restore、stash 或 `git add .`。
GitLab MR 查询、目标分支最终校验和后续业务判断交给 worktree Agent；主 Agent 仅在创建
worktree 前按以下顺序提供候选目标分支：

1. 已有 MR：使用 MR 的 target branch。
2. 用户明确指定：复述并确认；具体 release 分支需要二次确认。
3. 未指定：fetch 后根据当前分支和 fork-point 推断，展示依据并取得确认。

目标分支不存在时停止派单，不回退到其它分支。源分支按 Bug 内容生成
`fix/<topic>-<bug-id>`，先检查本地、远端和 worktree，存在时复用。

## 3. 安全迁移已有修复

当前工作区已有未提交修复时：

1. 对该 Bug 的 tracked 文件生成 binary patch；未跟踪文件复制到临时目录。
2. 验证临时副本可读且非空。
3. 只恢复属于该 Bug 的源文件，让原工作区恢复到迁移前的其它状态。
4. 从最新目标分支创建 Worktrunk worktree：

```bash
git fetch origin "$TARGET_BRANCH" --prune
wt switch --create "$SOURCE_BRANCH" --base "origin/$TARGET_BRANCH" \
  --no-cd --format json
```

5. 在新 worktree 应用 patch/复制文件，回读 `git status` 和 `git diff --check`。

迁移失败时保留临时副本并停止，确保修复不会从两个位置同时丢失。

若尚未修复，跳过 patch 迁移；仍先创建 Worktrunk worktree，再进入 Luvus。

## 4. Luvus 异步接管

Worktrunk 创建完成后，全部交付操作必须由该 worktree 中的 Luvus Pi agent 执行，包括 Bug
解析、代码修改、排查、测试、提交、push、MR、pipeline 门禁、合并、Meegle 评论/流转/回读和
清理。主 Agent 不继续直接执行这些操作。

加载 `luvus` skill。位于 Luvus 中时必须使用继承的 `LUVUS_BIN_PATH`、
`LUVUS_SOCKET_PATH` 和 `LUVUS_PANE_ID`，不换用其它 session 或 PATH 中的客户端。

1. 用 `luvus workspace list` 按**完整 worktree 路径**定位 workspace。
2. Worktrunk hook 未自动打开时，执行 `luvus worktree open "$WORKTREE_PATH"`，再回读列表。
3. 在该 workspace 的空闲 shell pane 启动或复用命名 Pi。不要为了派单改变用户焦点：

```bash
"$LUVUS_BIN_PATH" pane list
"$LUVUS_BIN_PATH" agent start "$AGENT_NAME" --kind pi --pane "$PANE_ID" --timeout 30
```

4. 主 Agent 先给自己命名，再用**不带 `--wait`** 的 `agent send` 传递完整阶段任务，不发送原始
   终端按键：

```bash
"$LUVUS_BIN_PATH" agent name bugfix-lead
"$LUVUS_BIN_PATH" agent send "$AGENT_NAME" "$TASK"
```

   任务必须包含：
   - Bug URL、当前用户请求的阶段和已授权外部动作；
   - worktree、源分支、候选目标分支；
   - 已有改动和必须保留的文件；
   - 项目规则、相关测试与禁止的副作用；
   - 要求 worker 自行读取 Bug 标题、描述、管理类型、报告人、状态和实时 transition；
   - 要求 worker 自行执行 GitLab 与 Meegle 操作并逐项回读；
   - 要求 worker 在完成或阻塞时执行
     `luvus agent send bugfix-lead 'done|blocked: <成果、证据、下一步>'` 主动回报；
   - MR 必须链接 Bug；默认 Bug 管理类型合入 `develop` 前不得评论、@ 测试或流转 Bug；
     CB3 流程不得在 QA 验收并流转“已验证待合入”前合并，且不得代替 QA 写验收结论或执行
     该流转；其它合并和改单操作必须有当前阶段授权。
5. `agent send` 成功后，只向用户报告任务被送到哪个 agent/pane，然后结束当前轮次。不要读取
   agent 输出、等待状态、轮询外部系统或在主会话重复执行 worker 的验收。

worker 对当前阶段负责到底。可为当前步骤使用工具自带的有界等待；若 pipeline、QA 或授权尚未
满足，则报告 `blocked` 并保持 worktree/agent，不做无限轮询。后续请求通过同一 agent 的新一条
无等待 `agent send` 继续，worker 重新回读所有门禁。

Luvus 或 Pi 无法启动时停止并说明，不静默回退到主会话直接操作；只有用户明确同意才换路径。

## 5. MR 门禁

worktree Agent 必须按目标仓库 MR 规范提交并创建或更新 MR。MR 描述必须包含原始 Bug 链接：

```markdown
## 关联 Bug
- [Bug <id>：<标题>](<BUG_URL>)
```

还需写清根因、改动和实际验证。worker 自行回读并确认 source/target、Bug URL、pipeline、
提交已推送且 worktree 干净；缺一项就自行修正或报告阻塞。主 Agent 不重复回读。

## 6. 按模板评论和流转

worktree Agent 在状态流转前先 `workflow list-state-transitions`，只使用实时返回的 transition ID。
评论创建或更新后先回读，再流转并回读最终状态。两种模板的时点和文案不得混用。

### 默认 Bug 管理类型合入 develop 后

MR 创建、pipeline 通过但**尚未合并**时，到此为止：不创建修复评论、不 @ 测试、不修改 Bug
状态。只有 MR 已合并且已验证 source commit 进入 `origin/develop` 后，才写入：

```markdown
## 修复已合入

@<报告人或指定测试> 修复已合入 `develop`，请回归验证。

- MR：[<MR 标题>](<MR_URL>)
- 目标分支：`develop`
- Merge Commit：`<MERGE_COMMIT>`
- 根因：<一句话>
- 修复：<改动摘要>
- 验证：<实际命令、pipeline 与合入验证摘要>
```

评论回读成功后，从实时 transition 列表选择名称为 `RESOLVED` 的目标并流转。若没有该目标、
模板不再是默认类型，或目标分支不是 `develop`，停止并报告，不用其它状态代替。

### CB3 客户端 Bug 流程合并前

MR 与 pipeline 就绪后、MR 合并前写入：

```markdown
## 修复待验收

@<报告人或指定测试> 已完成修复，请验收。

- 修复分支：`<SOURCE_BRANCH>`
- MR：[<MR 标题>](<MR_URL>)
- 目标分支：`<TARGET_BRANCH>`
- 根因：<一句话>
- 修复：<改动摘要>
- 验证：<实际命令及 pipeline 摘要>

MR 暂未合并，待验收通过后合入 `<TARGET_BRANCH>`。
```

评论回读成功后，开发侧流转到实时返回的“已解决待验证”，本阶段即完成。后续验收评论和
“已验证待合入”流转属于 QA：开发侧不得根据口头转述代写验收结论，也不得代替 QA 执行流转。
当用户之后要求合并时，重新读取 Bug 评论和当前状态；只有 QA 已记录通过结论且服务端当前状态
已是“已验证待合入”，才进入合并门禁。合并后可补充独立的开发侧合入记录和 Merge Commit，
不要覆盖或冒充 QA 的验收评论。

mention 格式使用 `meegle user search` 返回的 `lark_user_id`：

```markdown
@姓名<!-- mention:{"id":"lark_user_id_<id>","cn_name":"姓名","blockType":"AT_USER_BLOCK"} -->
```

先 `comment list` 查重。同一 MR 已有开发侧修复评论时，用 `comment add --action update` 更新原
评论；否则创建。QA 的验收评论由 QA 维护，开发侧不更新、覆盖或仿写。不得为了复用旧评论而
保留错误的 @ 时点或“尚未合并/已合入”措辞。

## 7. 合并与清理

只有任务已明确包含合并授权，且 pipeline、MR 可合并状态和对应模板门禁均满足时，worktree
Agent 才能合并：

- 默认 Bug 管理类型 → `develop`：合并是 @ 测试和状态流转的前置条件。
- CB3 客户端 Bug 流程：回读确认 QA 已留下通过结论，且当前状态已经由 QA 流转为
  “已验证待合入”，才满足合并前置条件。开发侧不得自行制造这两项门禁证据。

worktree Agent 合并后 fetch 目标分支，验证 source commit 已进入 `origin/$TARGET_BRANCH`，并
取得真实 merge commit。随后执行该模板规定的评论和状态动作；默认 Bug 管理类型不得在这项
验证前提前通知测试。

清理前由 worktree Agent 确认模板规定的评论与状态均已回读成功，且 worktree 无未提交改动、
无未推送提交。任务已授权移除时使用 Worktrunk：

```bash
wt remove "$SOURCE_BRANCH"
```

当目标分支不是 Worktrunk 默认分支时，worktree 可被移除但本地分支可能因默认分支未包含它
而保留。先验证 MR 已合并、目标分支包含提交、远端源分支已删除；需要 `-D` 删除本地分支时
单独取得明确授权。

worker 的最终回报必须包含 MR、commit、目标分支、pipeline、Bug 状态、评论 @ 对象、
worktree/分支结果和残留项。主 Agent 只转述这份主动回报并按用户下一条指令继续派单。
