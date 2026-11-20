# 决策记录（Decision Records）

## DR-003 2026-11-21 M4 站点形态采用混合站（上游全量 + zh/ 覆盖） [状态: 生效]
- 背景: M4 里程碑需以 Hugo 构建中文站；zh/ 仅覆盖 232/242 个 md（10 个 skip 功能页无译文），content 的组装方式决定链接完整性与未译页表现。
- 选项与权衡: 方案A 混合站（content=上游全量 242 md + 631 非 md，zh/ 232 个同路径覆盖，未译页显示英文，全站链接零 404，代价是构建目录略大、英文兜底页已加未翻译提示）；方案B 纯中文站（仅 zh/ 232 个 md，站内相对链接改写为指向 protobuf.dev 绝对链接，代价是改写逻辑复杂脆弱、侧栏/交叉引用 404 风险高、未来持续同步维护成本高）
  ← 方案B 因改写脆弱性与维护成本弃用。
- 结论: 采用方案A 混合站；英文兜底页在页脚标注"本页为英文原文，尚未翻译"。构建对齐 Hugo 0.148.2（详见 tools/build_site.py 内注释）。
- 理由: 翻译项目持续增量更新，混合站保证任何时刻全站可导航、无死链，与"永不追平全量"的同步机制天然契合。
- 影响: tools/build_site.py 组装逻辑、页脚模板 override、README 发布说明。
- 记录时间 / 会话: 2026-11-21 / M4 会话

## DR-004 2026-11-21 M4 发布渠道采用同仓库 GitHub Actions 发布 Pages [状态: 生效]
- 背景: 本仓库当前无 git remote，需选定 GitHub Pages 的发布方式。
- 选项与权衡: 方案a 同仓库 Actions 发布（推送 main 即自动构建发布，产物不入库，GitHub 官方推荐，代价是新增 workflow 文件）；方案b gh-pages 分支（本地构建推产物，代价是产物入库、每次发布手动重建）；方案c 暂不发布（仅本地预览，不满足 M4 目标）
  ← 方案b 因产物入库与手动重建弃用；方案c 由用户确认发布意图后排除。
- 结论: 采用方案a：新增 .github/workflows/deploy.yml，Pages source = GitHub Actions。
- 理由: 与月度 sync 工作流衔接最顺（push 即上线），产物不入库符合"构建产物目录不入库"约束。
- 影响: .github/workflows/deploy.yml、GitHub Pages 仓库设置、tools/build_site.py 的 CI 适配。
- 记录时间 / 会话: 2026-11-21 / M4 会话

## DR-005 2026-11-21 M4 站点域名使用默认 GitHub Pages 域名 [状态: 生效]
- 背景: 发布地址决定 baseURL 与 CNAME 上游排除处理。
- 选项与权衡: 方案A 默认 Pages 域名（https://jxsword.github.io/protobuf-docs-zh/，零配置零成本，代价是 URL 带仓库路径）；方案B 自定义域名（需购买域名 + DNS 配置 + 构建保留 CNAME）
  ← 方案B 因额外成本与配置负担暂弃用，未来可随时追加（可逆项）。
- 结论: 采用方案A；构建脚本排除上游 CNAME（避免误绑 protobuf.dev），baseURL 默认为项目 Pages 地址。
- 理由: 先零成本上线，自定义域名属可随时追加的可逆项。
- 影响: tools/build_site.py 的 --base-url 参数默认值与 CNAME 排除逻辑。
- 记录时间 / 会话: 2026-11-21 / M4 会话

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
