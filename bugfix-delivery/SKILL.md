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

其它模板先读取其实时状态流并向用户确认阶段。每一步以回读结果为完成标准；外部命令成功但
未回读，不算完成。

## 1. 解析 Bug

加载 `meegle` skill，执行 URL decode 和 Auth Guard：

```bash
meegle url decode --url "$BUG_URL" --format json
meegle auth status --format json
meegle project search --project-key "$SIMPLE_NAME" --format json
meegle workitem get --project-key "$PROJECT_KEY" --work-item-id "$BUG_ID" \
  --fields _all --params '{"page_size":100}' --format json
```

保存 Bug 标题、描述、优先级、当前状态、工作项类型、报告人，以及
`work_item_attribute.template.id/name`。后者就是 **Bug 管理类型**；按上面的模板表选择流程，
不要从标题、目标分支或工作项类型猜测。默认以**报告人作为测试人员**；用户显式指定测试人员
时使用指定人员。只有流程到达 @ 测试的阶段时，才通过 `meegle user search` 将 user_key 转换成
`lark_user_id`，供评论中的真实 @ mention 使用。

## 2. 确认改动与目标分支

检查工作区、现有 worktree、分支和 MR。若多个改动混在一起，先明确哪些文件属于 Bug。
保护其它改动，不使用整仓 restore、stash 或 `git add .`。

目标分支按以下顺序确定：

1. 已有 MR：使用 MR 的 target branch。
2. 用户明确指定：复述并确认；具体 release 分支需要二次确认。
3. 未指定：fetch 后根据当前分支和 fork-point 推断，展示依据并取得确认。

目标分支不存在时停止，不回退到其它分支。源分支按 Bug 内容生成
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

## 4. Luvus 强制接管

Worktrunk 创建完成后，后续代码修改、排查、测试、提交、push 和 MR 创建必须由该 worktree
中的 Luvus Pi agent 执行。主会话负责监督、回读 GitLab/Git 结果和操作 Meegle，不继续直接
修改业务代码。

加载 `luvus` skill。位于 Luvus 中时必须使用继承的 `LUVUS_BIN_PATH`、
`LUVUS_SOCKET_PATH` 和 `LUVUS_PANE_ID`，不换用其它 session 或 PATH 中的客户端。

1. 用 `luvus workspace list` 按**完整 worktree 路径**定位 workspace。
2. Worktrunk hook 未自动打开时，执行 `luvus worktree open "$WORKTREE_PATH"`，再回读列表。
3. 聚焦该 workspace，读取 pane；在其空闲 shell pane 启动命名 Pi：

```bash
"$LUVUS_BIN_PATH" workspace focus "$WORKSPACE_INDEX"
"$LUVUS_BIN_PATH" pane list
"$LUVUS_BIN_PATH" agent start "$AGENT_NAME" --kind pi --pane "$PANE_ID" --timeout 30
```

4. 通过 `agent send` 传递完整任务，不发送原始终端按键。任务必须包含：
   - Bug URL、标题、描述、证据与验收标准；
   - worktree、源分支、动态确认的目标分支；
   - 已有改动和必须保留的文件；
   - 项目规则、相关测试与禁止的副作用；
   - MR 必须链接 Bug；默认 Bug 管理类型合入 `develop` 前不得评论、@ 测试或流转 Bug；
     CB3 流程不得在 QA 验收并流转“已验证待合入”前合并，且不得要求 Pi 代替 QA 写验收
     结论或执行该流转；其它合并和改单操作必须有当前阶段授权。
5. Agent 完成后读取其结果，并独立回读 worktree diff、commit、push、MR 和 pipeline。

Luvus 或 Pi 无法启动时停止并说明，不静默回退到主会话直接修改；只有用户明确同意才换路径。

## 5. MR 门禁

Pi 必须按目标仓库 MR 规范提交并创建或更新 MR。MR 描述必须包含原始 Bug 链接：

```markdown
## 关联 Bug
- [Bug <id>：<标题>](<BUG_URL>)
```

还需写清根因、改动和实际验证。主会话回读并确认 source/target、Bug URL、pipeline、
提交已推送且 worktree 干净；缺一项就让 Luvus agent 修正。

## 6. 按模板评论和流转

状态流转前先 `workflow list-state-transitions`，只使用实时返回的 transition ID。评论创建或更新后
先回读，再流转并回读最终状态。两种模板的时点和文案不得混用。

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

只有用户明确授权且 pipeline、MR 可合并状态和对应模板门禁均满足时才合并：

- 默认 Bug 管理类型 → `develop`：合并是 @ 测试和状态流转的前置条件。
- CB3 客户端 Bug 流程：回读确认 QA 已留下通过结论，且当前状态已经由 QA 流转为
  “已验证待合入”，才满足合并前置条件。开发侧不得自行制造这两项门禁证据。

合并后 fetch 目标分支，验证 source commit 已进入 `origin/$TARGET_BRANCH`，并取得真实 merge
commit。随后执行该模板规定的评论和状态动作；默认 Bug 管理类型不得在这项验证前提前通知测试。

清理前确认模板规定的评论与状态均已回读成功，且 worktree 无未提交改动、无未推送提交。用户
授权移除时使用 Worktrunk：

```bash
wt remove "$SOURCE_BRANCH"
```

当目标分支不是 Worktrunk 默认分支时，worktree 可被移除但本地分支可能因默认分支未包含它
而保留。先验证 MR 已合并、目标分支包含提交、远端源分支已删除；需要 `-D` 删除本地分支时
单独取得明确授权。

最终报告 MR、commit、目标分支、pipeline、Bug 状态、评论 @ 对象、worktree/分支结果和残留项。
