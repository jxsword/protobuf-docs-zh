# protobuf.dev 官方文档中文翻译计划

> 版本：v2（2026-11-18 制定，同日经两轮复审修订）
> 上游：https://github.com/protocolbuffers/protocolbuffers.github.io （protobuf.dev 站点源码，Hugo）
> 许可：上游 LICENSE 为 BSD-3-Clause（Google Inc.），翻译分发须保留版权声明与免责条款。
>
> 修订记录：
> - v1：初版。
> - v1.1（第一轮复审）：拆分 upstream 职责（clone 与快照分离）；增量锚点改为 blob SHA + commit diff 双机制；补充 Hugo 特殊文件（_index.md / includes / shortcode）处理；明确站内链接策略；译者与审校 agent 分离；显式 skip 清单。
> - v2（第二轮复审）：补充 Windows 编码/换行规范；新增"风险与对策"章节；定义分支与提交策略、可选 CI；补充 style-guide.md 大纲；LICENSE 要求落实为全文；术语表来源落实。

## 一、事实基础（已核实）

| 事项 | 结论 |
| --- | --- |
| protobuf.dev 官方中文版 | **无**。站点无语言切换，仅英文。developers.google.cn 上有旧版（proto2/proto3 时代）中文页，非 protobuf.dev 内容且不完整 |
| 文档源码仓库 | **有**：`protocolbuffers/protocolbuffers.github.io`（Hugo 站点，`content/` 下 244 个 Markdown 文件）。另有少量设计文档在 `protocolbuffers/protobuf` 的 `docs/` 目录 |
| 上游规模 | content/ 共 244 个 .md：reference 137、news 54、programming-guides 16、getting-started 8、support 5、design-decisions 6、best-practices 4、editions 4，其余为单页；另有 `includes/`（局部引用文件）与 `images/`（3 张图） |
| 图片资源 | content/images 仅 3 张，量小，直接同步 |

## 二、已有翻译项目调研（GitHub 全网检索结论）

**未找到任何可复用的 protobuf.dev 新版文档中文翻译项目。** 已核查的候选：

| 项目 | 状态 | 优点 | 缺点 | 可借鉴 |
| --- | --- | --- | --- | --- |
| [daobook/protobuf](https://github.com/daobook/protobuf) | fork 官方旧仓库，0 star，最后推送 2022-02 | "fork 上游 + 译文" 思路；有在线阅读站 | 覆盖的是旧仓库布局（proto2/proto3 时代），**不含 protobuf.dev 新内容**；与代码仓库耦合；严重过时 | 上游同步思路 |
| [ChinaBigPan/protobuf_docs_zh_cn](https://github.com/ChinaBigPan/protobuf_docs_zh_cn) | 2020 一次性，0 star，无许可证 | — | 描述与内容不符（偏 protobuf.js），非 protobuf.dev | 无 |
| [gclove/protobuf_doc_ZH_CN](https://github.com/gclove/protobuf_doc_ZH_CN) | 0 star 手册 | — | 非官方文档完整翻译 | 无 |
| tearwind/protocol-buffers-doc 等博客型翻译 | 静态、停更 | 单篇质量可参考 | 基于旧版 developers.google.com proto2/proto3 文档；无增量机制 | 术语译法参考 |

相关生态：grpc.io 有官方中文站（社区翻译 + 上游同步工作流），其「上游监控 → 翻译任务 → 审校发布」模式可借鉴，但内容不覆盖 protobuf.dev。

**结论：自建翻译仓库；借鉴 daobook 的 fork/同步思想 + grpc 中文站的工作流模式 + 既有博客翻译的术语习惯。**

## 三、仓库结构设计

```
protobuf-docs-zh/
├── upstream/                  # 上游 content/ 快照（提交入库，只读，由 sync 脚本维护）
│   └── content/               # 与 protocolbuffers.github.io/content/ 一一对应
├── .upstream/                 # 官方仓库完整 clone（gitignore，仅供 sync 脚本使用，不入库）
├── zh/                        # 中文译文，目录结构与 upstream/content/ 完全一致（含 _index.md 同名保留）
│   ├── overview.md
│   ├── getting-started/
│   └── ...
├── zh/_archived/              # 上游删除文件对应的归档译文
├── tools/                     # 同步与质检脚本（Python ≥3.10，仅标准库）
│   ├── sync_upstream.py       # fetch 官方仓库 → 更新 upstream/ 快照 → 对比 manifest → 产出任务清单
│   ├── verify_structure.py    # 结构校验：标题层级/代码块/表格/链接/图片/shortcode 数量与层级一致性
│   ├── check_terms.py         # 术语表一致性检查 + 未翻译残留检测（含 allowlist 白名单）
│   └── gen_tasks.py           # 汇总待办为 tasks/pending-<date>.md（供 agent 分批领取）
├── manifest.json              # 每个文件的上游 blob SHA、翻译时上游 commit、状态、时间
├── glossary.md                # 术语表（强制统一译法）
├── style-guide.md             # 翻译风格规范
├── LICENSE                    # BSD-3-Clause 全文 + 译文分发免责声明 + 译文说明
├── README.md                  # 项目说明、进度看板、使用方法
├── tasks/                     # sync 产出的增量翻译任务清单（历史留档）
├── .gitattributes             # 强制 LF（* text=auto eol=lf），避免 Windows CRLF 噪音
└── docs/
    ├── decision_log.md        # 重大决策记录
    └── translation-plan.md    # 本文件
```

**upstream 双层设计**（复审修正）：
- `.upstream/`：官方仓库的完整 git clone（gitignore），sync 脚本在此 `git fetch`，利用其提交历史生成 diff；
- `upstream/content/`：仅 content/ 的**文件快照**，提交入库——译文评审时可就地对照原文，且上游原文变更在 git 历史中可追溯。

## 四、增量翻译核心机制（双锚点）

**锚点一（状态锚点）：per-file blob SHA。** `manifest.json` 每文件记录翻译时用 `git hash-object` 计算的上游 blob SHA：

```json
{
  "getting-started/overview.md": {
    "status": "translated | pending | update-needed | removed | skip",
    "upstream_sha": "<git blob SHA>",
    "upstream_commit": "<翻译时上游 commit>",
    "translated_at": "2026-11-18",
    "translator": "agent | agent+human | human"
  }
}
```

**锚点二（变更定位）：commit 区间 diff。** manifest 全局记录 `last_synced_commit`；sync 时：

```
git -C .upstream fetch origin
git -C .upstream diff --name-status <last_synced_commit>..origin/main -- content/
```

增量同步流程（`tools/sync_upstream.py`）：

1. fetch 官方仓库最新 `main`；
2. `git diff --name-status` 得到 A/M/D/R 文件清单，逐文件用 blob SHA 复核（处理"某文件上次 sync 后又改回原样"的边界情况）；
3. 将变更文件更新到 `upstream/` 快照；
4. 状态判定：
   - 新文件（A）→ `new`（全量翻译任务）
   - 变更（M）→ `update`：生成该文件 `git diff <旧blob>..<新blob>` 摘要，**只重译变更段落**；由译者 agent 判断变更是否实质影响译文（格式微调/拼写修正可跳过，须在任务清单中标注结论）
   - SHA 不变且已译 → `skip`
   - 删除（D）→ `removed`：译文移入 `zh/_archived/`，manifest 保留记录
   - 改名/移动（R）→ 沿用旧译文到新路径，按 M 处理 diff
5. 特殊联动：`content/includes/` 下的局部引用文件更新时，**所有引用它的页面**任务状态标记 `update-needed(review)`，由译者 agent 核对相关段落后降级为 skip；
6. 更新 `last_synced_commit`，生成 `tasks/pending-<date>.md`（按优先级排序、附 diff 摘要、估算批量）；
7. sync 以独立 commit 入库（`docs: sync upstream <commit>`），翻译改动与 sync commit 分离，便于追溯。

## 五、Agent 翻译工作流

单文件翻译 SOP（写入 style-guide.md，供每次会话的 agent 遵循）：

1. 读取原文 + `glossary.md` + `style-guide.md`；
2. 翻译正文；**硬性规则**：
   - 代码块、命令行、API/字段签名、proto 定义不翻译；代码内注释可双语；
   - **Hugo shortcode**（`{{< ... >}}` / `{{% ... %}}`）原样保留，参数不得翻译；
   - frontmatter 中 `title`/`description` 等翻译，键名与结构不变，不得增删官方键；
   - 站内相对链接、锚点、图片引用**原样保留**（建站时由构建脚本统一改写为中文路径，见第七节）；
   - 专有名词首译时在括号内附英文原文；
   - 全部文件 IO 显式 `encoding='utf-8'`，输出 LF 换行；
3. 译文头部 YAML frontmatter 追加：`source_url`、`upstream_commit`、`translated_at`、`status`；
4. **双人流水线（复审修正）**：译者 agent 完成后，由独立的**审校 agent** 对照原文检查漏译、误译、术语一致性与 shortcode 完整性；抽查式人工复核覆盖 10%；
5. 运行 `tools/verify_structure.py <原文件> <译文>` 与 `tools/check_terms.py <译文>`，全部通过才算完成；
6. 更新 manifest 对应条目；每批完成单独 commit（`translate: <path> (upstream <sha 前 8 位>)`）。

批量执行：按任务清单分批（每批 ≤ 10 文件），并行译者 agent，审校 agent 逐文件复审。

## 六、翻译范围与优先级（244 文件分级）

| 阶段 | 范围 | 文件数 | 说明 |
| --- | --- | --- | --- |
| Phase 0 | 脚手架 | — | repo 初始化、四个脚本、`.upstream` clone、manifest 首次生成、术语表、风格规范 |
| Phase 1 | 核心阅读路径：overview、getting-started、programming-guides、best-practices、editions、installation | ~40 | 最高价值，官方推荐阅读顺序 |
| Phase 2 | reference 精选：语法参考、样式指南、options、速查等人工撰写页 | ~30 | 排除纯自动生成/纯命令参考页 |
| Phase 3 | reference 其余（API/命令参考） | ~100 | 按需、可延后 |
| Phase 4 | news（54）、design-decisions、support | ~65 | news 可选只译重大版本公告 |
| 持续 | 每月或上游显著变更后跑 sync | 增量 | 增量翻译，永不追平全量历史 |

**skip 清单（站点功能页，不翻译）**：`navbar.md`、`forum-link.md`、`search.md` 及 `content/includes/` 中纯技术片段；`_index.md` 列表页仅译标题与导语。Phase 0 时逐个确认后写入 manifest（status=skip 或 skip-partial）。

## 七、持续更新机制

- **同步节奏**：每月 1 日 + 上游 content/ 出现批量变更时运行 sync（后续可补自动化计划任务）；
- **分支与提交策略（复审补充）**：sync commit 直接进 `main`；批量翻译走 `translate/<date>-<batch>` 分支，审校通过后合入 `main`，保持 main 始终可发布；
- **发布（可选，Phase 1 后决定）**：用 Hugo 以 zh/ 为 content 构建静态站，GitHub Pages 发布；站内相对链接改写、原文链接与版权声明由构建脚本注入，不污染 md 源文件；
- **可选 CI（M3 后）**：GitHub Actions 对 PR 自动跑 `verify_structure.py` + `check_terms.py`，防增量破坏结构。

## 八、质量规范（style-guide.md 大纲，复审补充）

- 术语表（glossary.md）：以 gRPC 中文站与既有社区翻译的成熟译法为底稿拟定，Phase 0 出初版并随翻译迭代；术语变更仅对新翻译强制，历史译文由 `check_terms.py --fix` 可选批量回填；
- 代码与命令不译；shortcode / frontmatter 键 / URL / 图片引用原样保留；
- 中文排版：全角标点、CJK 与西文/数字之间加空格、专有名词首现附英文、避免翻译腔；
- 语气：技术文档直陈风格，"你"不译为"您"；
- 脚本编码规范：显式 `utf-8` 读写、LF 输出、路径用 `pathlib`。

## 九、风险与对策（复审新增）

| 风险 | 对策 |
| --- | --- |
| 上游目录重构/批量改名 | sync 按 R 状态沿用旧译文路径；manifest 保留新旧映射；大规模重构时人工评审一次 |
| agent 译文质量波动 | 译者/审校 agent 分离 + 结构/术语脚本硬门禁 + 10% 人工抽查；不合格批次整批回炉 |
| shortcode/frontmatter 损坏导致 Hugo 构建失败 | verify_structure.py 将 shortcode 与 frontmatter 键纳入校验；可选 CI 阻断 |
| 术语漂移（同一概念多种译法） | glossary.md 为唯一权威源，check_terms.py 强制校验，新词必须先入表再使用 |
| includes 局部文件变更的遗漏 | 联动机制：引用页标记 `update-needed(review)`，核对后才可降级 |
| 上游 BSD 许可合规 | LICENSE 保留 BSD-3 全文与免责声明；每个译文页 frontmatter 记录 source_url 与上游 commit |
| Windows 编码/换行差异 | `.gitattributes` 强制 LF + 脚本显式 utf-8（见第八节） |

## 十、里程碑

| 里程碑 | 交付物 |
| --- | --- |
| M0（0.5 天） | 仓库结构 + 四个脚本可运行 + `.upstream` clone + manifest 生成 + 首次 sync 报告 |
| M1（1–2 天） | 术语表 + 风格规范定稿；Phase 1 样例 5 篇经"译者+审校"流水线并通过质检 |
| M2 | Phase 1 全部 ~40 篇完成 |
| M3 | Phase 2 完成；月度 sync 惯例建立；可选 CI 上线 |
| M4（可选） | Hugo 中文站发布 |
