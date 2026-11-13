# 安全拆分历史

仅在用户授权拆分已有历史时读取；新独立任务无需走历史重写流程。
协调者规划/备份，先用 Worktrunk 建立/复用 worktree，再交对应 Luvus workspace 的 agent
执行移植、依赖适配和验证。

## 1. 固定事实

- 记录原分支 tip、评审的 target/base 与 source/head SHA（如有）、push remote 的仓库身份与分支 SHA。
- 核实 `upstream` 确实指向目标上游，fetch `upstream main` 后记录 `upstream/main` 的完整 SHA。
  不存在该 remote/main 时先解析真实上游默认分支并确认，不把 fork 的 `origin/main` 当成上游。
- 独立 bugfix / 公共 CI 分支基于该已核实的 `upstream/main` SHA，不基于混合 feature tip。
- 建立逐提交清单，包括后续修复、merge commits、模型字段、序列化与 docs/测试依赖。
  每项标记“留 feature / 移入独立问题 / 已被 follow-up 覆盖 / 跨问题依赖待处理”。

## 2. 完整备份先于改写

在仓库外的私有备份目录保存清单及恢复说明，避免日志/patch 中的凭据进入评审。

1. 用唯一 backup ref 固定每个待改写分支的原 tip；不覆盖已有 backup ref。
   保存 `git bundle create <backup.bundle> --all`，执行 `git bundle verify <backup.bundle>`。
   这只备份可达 Git 历史，不覆盖未提交文件、子模块工作区或 LFS 外部对象。
2. 分别保存 `git diff --binary` 与 `git diff --cached --binary`，以及 status/untracked 清单；
   复制全部未跟踪文件（含二进制、符号链接），并保存会受操作影响的 ignored 本地资产。
   子模块/LFS 如有相关改动，单独备份并列出对象/工作区。
3. 核对文件数量、大小/校验和及 bundle 可读性，给出恢复路径。备份不完整则停止。
   不把“命令成功”当作 staged/unstaged/untracked 均已覆盖。

本地 backup ref 是保护操作，不是修复提交。不得为备份自动提交用户工作区。
保留原工作区所有用户改动；如必须迁移/恢复源文件，单独说明并取得授权后才做。

## 3. 对应 workspace agent 逐分支移植

移植任务须包含原 commit SHA 列表及备份位置。需要生成提交时先取得本地提交授权；
只授权改代码时，worker 可准备未提交 diff，不自动 cherry-pick 生成提交。

- 按提交移植，逐项回读 diff；merge commit 的父线不明确时先停止确认。
- mixed commit 按问题拆出；模型/docs 是 feature 专属时剔除或在独立分支做最小适配，
  不为通过编译把整个 feature 带回来。真实依赖无法解除就报告依赖，不宣称独立。
- 每个分支独立执行针对性测试、构建与 `git diff --check`；与基线比较 changed files/commits，
  逐项对应原清单。对照备份证明每项改动仍在某一归属分支或用户原工作区中。
- 新归属及验证未完成前，不从原分支删除对应改动。原分支重建也由其唯一 writer 做。
  不跨多个 worker 同时重写同一 branch/ref。

## 4. 发布是独立授权阶段

本地拆分不等于允许 commit、push 或开评审。已有独立评审直接复用；创建新评审前再次查重。
更改已发布历史先说明受影响的评审、旧/新 tip、协作者风险及恢复办法，取得明确授权。

获得 push/历史改写授权后，仅向已核实的仓库和完整 ref 推送，例如：

```bash
# EXPECTED_OLD_SHA 来自本次核实的远端 ref，不是盲信本地 tracking ref
# NEW_TIP 是已验证的完整 SHA；只在授权阶段由 owner 执行
git push "$PUSH_REMOTE" \
   --force-with-lease="refs/heads/$BRANCH:$EXPECTED_OLD_SHA" \
   "$NEW_TIP:refs/heads/$BRANCH"
```

lease 不匹配就停止并重新审查远端新增工作，不盲 force、不通过刷新期望值直接覆盖。
push 后回读远端 ref 和平台评审的 source/head SHA。二者不一致时报告实际 SHA、时间及 API 阻塞，
保留备份和现场；不重复 force 或虚报评审或 CI 已更新。平台评论、resolve、merge 另取授权。
