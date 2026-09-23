---
name: bugfix-delivery
description: >-
  交付飞书 Project Bug 的个人工作流。用于分析或接管已修复 Bug、用 Worktrunk
  创建独立分支/worktree，并强制通过 Luvus pane 中的 Pi 完成后续修复、验证、提交、
  GitLab MR、Bug 评论与状态流转、合并和清理。用户说“走一下 Bug 流程”“已修复但没建
  wt/分支”“测试通过后合并、改单、移除 wt”时使用。
---

# Bugfix Delivery

完成飞书 Bug 从代码到 GitLab、测试和回归的交付闭环。分支、目标分支、空间、人员、
状态和 transition ID 全部从当前事实解析；示例中的变量均为占位符。

## 完成阶段

按用户请求执行到对应阶段：

1. **待验证**：Worktrunk worktree、Luvus Pi 修复与验证、提交、MR、Bug 评论、
   状态“已解决待验证”。
2. **待合入**：记录测试结论，更新评论，状态“已验证待合入”。
3. **待回归**：合并 MR，验证目标分支，更新评论，状态“已合入待回归”，清理 worktree。

每一步以回读结果为完成标准。外部命令成功但未回读，不算完成。

## 1. 解析 Bug

加载 `meegle` skill，执行 URL decode 和 Auth Guard：

```bash
meegle url decode --url "$BUG_URL" --format json
meegle auth status --format json
meegle project search --project-key "$SIMPLE_NAME" --format json
meegle workitem get --project-key "$PROJECT_KEY" --work-item-id "$BUG_ID" \
  --fields _all --params '{"page_size":100}' --format json
```

保存 Bug 标题、描述、优先级、当前状态、工作项类型和报告人。默认以**报告人作为测试人员**；
用户显式指定测试人员时使用指定人员。通过 `meegle user search` 将 user_key 转换成
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
   - MR 必须链接 Bug；不合并、不改单，除非用户已授权当前阶段。
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

## 6. 评论后流转

状态流转前先 `workflow list-state-transitions`，只使用实时返回的 transition ID。
先评论，评论回读通过后再流转。评论至少包含：

```markdown
## 修复信息

@<报告人或指定测试> 请回归验证。

- 修复分支：`<SOURCE_BRANCH>`
- MR：[<MR 标题>](<MR_URL>)
- 目标分支：`<TARGET_BRANCH>`
- 根因：<一句话>
- 验证：<实际命令及结果摘要>
```

mention 格式使用 `meegle user search` 返回的 `lark_user_id`：

```markdown
@姓名<!-- mention:{"id":"lark_user_id_<id>","cn_name":"姓名","blockType":"AT_USER_BLOCK"} -->
```

先 `comment list` 查重。同一分支和 MR 已有修复评论时，以 `comment add --action update`
更新原评论；否则创建。合并后补 merge commit，并把文案改为回归验证。

按当前阶段选择服务端实际提供的目标状态，通常依次为“已解决待验证”“已验证待合入”
和“已合入待回归”。流转后再次查询并确认当前状态。

## 7. 合并与清理

只有用户明确授权且测试、pipeline、MR 合并状态均满足时才合并。合并后 fetch 目标分支，
验证 source commit 已进入 `origin/$TARGET_BRANCH`，再更新 Bug 评论和状态。

清理前确认 worktree 无未提交改动、无未推送提交。用户授权移除时使用 Worktrunk：

```bash
wt remove "$SOURCE_BRANCH"
```

当目标分支不是 Worktrunk 默认分支时，worktree 可被移除但本地分支可能因默认分支未包含它
而保留。先验证 MR 已合并、目标分支包含提交、远端源分支已删除；需要 `-D` 删除本地分支时
单独取得明确授权。

最终报告 MR、commit、目标分支、pipeline、Bug 状态、评论 @ 对象、worktree/分支结果和残留项。
