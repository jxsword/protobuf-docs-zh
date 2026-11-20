# 决策记录（Decision Records）

## DR-003 2026-11-21 M4 站点形态采用混合站（上游全量 + zh/ 覆盖） [状态: 生效]
- 背景: M4 需以 Hugo 构建中文站；zh/ 仅覆盖 232/242 个 md（10 个 skip 功能页无译文），content 的组装方式决定链接完整性与未译页表现。
- 选项与权衡: 方案A 混合站（content=上游全量 242 md + 631 非 md，zh/ 232 个同路径覆盖，未译页显示英文，全站链接零 404，代价是构建目录略大、英文兜底页需加未翻译提示）；方案B 纯中文站（仅 zh/ 232 个 md，站内相对链接改写为指向 protobuf.dev 绝对链接，代价是改写逻辑复杂脆弱、侧栏/交叉引用 404 风险高、长期维护成本高）
  ← 方案B 因改写脆弱性与维护成本弃用。
- 结论: 采用方案A 混合站；英文兜底页在页脚标注"本页为英文原文，尚未翻译"。
- 理由: 翻译项目持续增量更新，混合站保证任何时刻全站可导航、无死链，与"永不追平全量"的同步机制天然契合。
- 影响: tools/build_site.py 组装逻辑、页脚模板 override、README 发布说明。
- 记录时间 / 会话: 2026-11-21 / M4 Hugo 中文站构建会话

## DR-001 2026-11-18 上游官方文档采用 git clone 镜像同步 [状态: 生效]
- 背景: 翻译仓库需持续跟随 protocolbuffers/protocolbuffers.github.io 上游更新并支持增量翻译，须选定上游获取方式。
- 选项与权衡: 方案A git fork/clone 镜像（历史可追溯、blob SHA 天然支持增量检测与 diff 定位、离线可用，代价是本地维护一个上游 remote）；方案B GitHub API 按文件拉取（免 clone 整仓库，但有 API 速率限制、无本地历史、diff 需额外实现）
  ← 方案B 因历史可追溯性与速率限制弃用。
- 结论: 采用方案A：clone 官方仓库为 upstream remote，sync 脚本用 git fetch + blob SHA 对比实现增量。
- 理由: 增量翻译的核心是"精确知道每个译文对应哪个上游版本"，git blob SHA 是最可靠的锚点，且 diff 可直接定位变更段落。
- 影响: tools/sync_upstream.py、manifest.json 设计、仓库结构（docs/translation-plan.md 第三节、第四节）。
- 记录时间 / 会话: 2026-11-18 / protobuf-docs-zh 翻译计划制定会话

## DR-002 2026-11-18 译文采用 zh/ 镜像目录组织 [状态: 生效]
- 背景: 译文文件组织方式决定后续质检、增量合并与建站的复杂度。
- 选项与权衡: 方案A zh/ 镜像目录（与 upstream/content/ 路径一一对应，结构校验/增量 diff/建站均最简单，是文档翻译项目成熟做法，代价是仓库体积随上游增长）；方案B 双语对照单文件（单文件阅读方便，但结构校验复杂、上游更新合并困难）
  ← 方案B 因合并与校验成本弃用。
- 结论: 采用方案A：zh/ 目录与 upstream/content/ 完全同构，frontmatter 记录原文链接与上游 commit。
- 理由: 路径一一对应让 verify_structure.py 等质检脚本和后续 Hugo 建站都以"同名替换"方式工作，长期维护成本最低。
- 影响: 全仓库布局、tools/verify_structure.py、tools/check_terms.py 的输入约定（docs/translation-plan.md 第三节、第五节）。
- 记录时间 / 会话: 2026-11-18 / protobuf-docs-zh 翻译计划制定会话
