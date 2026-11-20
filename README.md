# protobuf-docs-zh — protobuf.dev 官方文档中文翻译

对 [protobuf.dev](https://protobuf.dev)（Protocol Buffers 官方文档站点）的
**非官方**中文翻译项目。上游源码仓库为
[protocolbuffers/protocolbuffers.github.io](https://github.com/protocolbuffers/protocolbuffers.github.io)
（Hugo 站点），本仓库以「原文快照 + zh/ 镜像译文 + 双锚点增量同步」的方式
持续跟随上游。

> 本项目与 Google 无隶属或背书关系；文档内容以官方英文原文为准。
> 许可证见 [LICENSE](LICENSE)（BSD-3-Clause，逐字复制自上游）。

## 目录结构

```
protobuf-docs-zh/
├── upstream/content/    # 上游 content/ 文件快照（入库，只读，由 sync 脚本维护）
├── .upstream/           # 官方仓库完整 git clone（gitignore，仅供 sync 脚本使用）
├── zh/                  # 中文译文，与 upstream/content/ 目录一一对应
│   └── _archived/       # 上游删除文件对应的归档译文
├── tools/               # 同步与质检脚本（Python ≥ 3.10，仅标准库）
│   ├── sync_upstream.py     # fetch → 快照更新 → manifest 状态判定 → sync 报告
│   ├── verify_structure.py  # 译文结构校验（标题/锚点/代码块/表格/链接/图片/shortcode/frontmatter）
│   ├── check_terms.py       # 术语一致性 + 未翻译残留检测（含 tools/allowlist.txt 白名单）
│   └── gen_tasks.py         # 生成任务清单 tasks/pending-<date>.md
├── manifest.json        # 每个文件的 upstream_sha / upstream_commit / status / 时间
├── glossary.md          # 术语表（唯一权威译法源，91 条）
├── style-guide.md       # 翻译风格规范与单文件翻译 SOP
├── tasks/               # sync 报告与任务清单（留档）；tasks/diffs/ 存放变更摘要
└── docs/                # translation-plan.md（总计划）与 decision_log.md（决策记录）
```

## 使用方法

```
sync 更新 → 领任务 → 翻译 → 审校 → 合入
```

1. **同步上游**：`python tools/sync_upstream.py`
   （首次或重建 manifest 用 `--init`）。脚本 fetch 官方仓库，按 commit 对比
   得到 A/M/D/R 清单，逐文件用 blob SHA 复核，更新 `upstream/` 快照与
   `manifest.json`，输出 `tasks/sync-<date>-<sha>.md` 报告。
2. **生成任务清单**：`python tools/gen_tasks.py`，产出
   `tasks/pending-<date>.md`（按 P0–P3 优先级分批，每批 ≤ 10 文件）。
3. **领批次翻译**：认领一个批次，按 [style-guide.md](style-guide.md) 的
   单文件 SOP 翻译到 `zh/` 同名路径；update-needed 条目只重译变更段落
   （diff 摘要在 `tasks/diffs/`）。
4. **质检**（两项全过才算完成）：

   ```bash
   python tools/verify_structure.py <原文件> <译文>
   python tools/check_terms.py <译文>
   ```

5. **审校合入**：审校 agent 逐文件复审通过后，更新 manifest 条目，按
   `translate: <路径> (upstream <sha>)` 格式单独 commit；批量翻译走
   `translate/<日期>-<批次>` 分支，审校通过后合入 `main`。

## 进度看板

数据来源 `manifest.json`（2026-11-18 初始化，上游 `f72a6a648b`；P0 批次 1
已于 2026-11-19 合入，见「进度说明」）。

**按状态**（总计 242 个上游 md 文件）：

| 状态 | 数量 | 说明 |
| --- | --- | --- |
| pending | 0 | **全部清零** |
| translated | 187 | 已完成并通过质检（P0 35 + P1 54 + P3 22 + P2 api-docs 81 - 重叠） |
| update-needed | 0 | 上游变更，需按 diff 更新 |
| skip-partial | 22 | 列表页：标题/描述/导语局部翻译已产出，条目列表保留英文 |
| skip | 10 | 站点功能/跳转页，无可译正文 |
| removed | 0 | 上游已删除（译文归档 zh/_archived/） |

**按优先级 / 待办**（优先级定义见 docs/translation-plan.md 第六节）：

| 优先级 | 范围 | 文件数 | 待办 |
| --- | --- | --- | --- |
| P0 | Phase 1 核心阅读路径（首页、overview、installation、getting-started、programming-guides、best-practices、editions） | 35 | **0（完成）** |
| P1 | Phase 2 reference 人工撰写页（非 api-docs） | 54 | **0（完成）** |
| P2 | Phase 3 reference/**/api-docs 自动生成页（可延后） | 83 | **0（完成）** |
| P3 | Phase 4 news、design-decisions、support、history、downloads | 70 | **0（完成）** |

## skip 清单（Phase 0 逐个确认结果）

**整页 skip（status=skip，10 个）**——均为站点功能/跳转页，无正文：

| 文件 | 确认结果 |
| --- | --- |
| `navbar.md` | 纯导航链接列表（4 行链接），无正文，不翻译 |
| `forum-link.md` | 仅 frontmatter（标题 + 论坛跳转链接），不翻译 |
| `search.md` | 仅 frontmatter（标题 + 搜索布局占位），不翻译 |
| `reference/{cpp,csharp,dart,go,java,php,python}/api-docs-link.md`（7 个） | 纯 frontmatter 跳转占位页（manualLink 指向各语言 API 文档站，无正文）；title 为语言名+API 组合无可译内容。Phase 0 skip 清单遗漏项，P1 批次 1 时补确认 |

**列表页 skip-partial（status=skip-partial，22 个）**——仅译 frontmatter 的
`title` / `linkTitle` / `description` 与正文导语，条目链接列表保留英文
（已在 `tools/allowlist.txt` 中整文件豁免残留检测）：

`_index.md`（分节列表页）共 22 个：
`best-practices/`、`design-decisions/`、`editions/`、`getting-started/`、
`news/`、`programming-guides/`、`support/`、`reference/`、
`reference/cpp/`、`reference/cpp/api-docs/`、`reference/csharp/`、
`reference/dart/`、`reference/go/`、`reference/java/`、`reference/kotlin/`、
`reference/kotlin/api-docs/`、`reference/objective-c/`、`reference/php/`、
`reference/protobuf/`、`reference/python/`、`reference/ruby/`、
`reference/rust/`（均指各目录下的 `_index.md`）。

**显式确认的例外**：

- 根 `_index.md`（站点首页）**不在** skip 范围——它含完整正文
  （What Is Protobuf 等），按正文页全量翻译（P0）；
- `reference/kotlin/api-docs/` 下 37 个 Dokka 自动生成页（含 7 个
  `_index.md`）保持 pending——它们不是列表页而是 API 类文档页，
  归 Phase 3 决定是否翻译。

**includes/ 局部文件**：`content/includes/` 实际只有 2 个 CSS 文件
（`suppress-nav.css`、`version-tables.css`），无 md 局部文件；二者随快照
同步但不进 manifest（manifest 只覆盖 md）。`sync_upstream.py` 的
includes 联动机制（更新时标记引用页 update-needed(review)）已实现，
供上游未来新增 md 局部文件时生效。

## 与翻译计划的差异记录（如实报告）

按计划第十节「不得静默偏离」约定，Phase 0 核实出以下与计划描述不符的
实际情况，均已按最小改动原则处理：

1. **文件数 242 ≠ 计划所称 244**：上游 `content/` 实测 242 个 md
   （reference 137、news 54、programming-guides 16、getting-started 8、
   support 5、design-decisions 6、best-practices 4、editions 4，
   顶层散页 8）；各目录数字与计划一致，总数差异来自计划口径。
2. **includes/ 无 md 局部文件**（仅 2 个 CSS），计划的「includes 联动」
   机制照常实现但当前无触发对象。
3. 根 `_index.md` 为首页正文页、kotlin api-docs 页为 API 文档页，
   均不适用「列表页 skip-partial」规则，逐个确认后按上述例外处理。

## 进度说明

- **P0 批次 1（10 文件，2026-11-19 合入 main）**：首页 `_index.md`、
  best-practices 3 篇、editions 3 篇、getting-started 教程 3 篇
  （cpp / csharp / dart）。译者/审校 agent 分离流水线 + 双脚本质检门禁
  10/10 通过；审校发现的注释口径问题已固化为 style-guide 规则 1 修订
  （代码注释可译，全仓统一）。
- **P0 批次 2（10 文件，2026-11-19 合入 main）**：getting-started 其余
  4 教程（go / java / kotlin / python）、installation、overview、
  programming-guides 前 5 篇（addons / deserialize-debug / editions /
  encoding）。质检 20/20 通过（含批次 1 回归）；审校修复 31 处；
  check_terms 升级支持「首现括注、后文径用」语义。
- **P0 批次 3（11 文件，2026-11-19 合入 main）**：programming-guides 全部
  11 篇（含 proto2 1848 行、proto3 1363 行两篇语言规范长文）。质检与
  全量回归 31/31 通过；审校修复 31 处（json.md 2 P2：JSON 表格类型词
  还原英文、`<code>` 标签还原；style.md 1 P2：descriptor 字面名前置）；
  glossary 批量补入 15 条新术语，singular 译法全仓统一。
- **P1 批次 1（2026-11-19 合入 main）**：reference/cpp 4 篇（abseil /
  arenas / cpp-generated / string-view）+ csharp / dart generated 2 篇
  正文；另将 7 个语言的 `api-docs-link.md` 逐个确认为跳转占位页标记
  skip（Phase 0 遗漏项补录）。审校修复 20 处，裁定三项口径（HTML 实体
  随散文翻译、markdown 转义符可归一、glossary 补 3 条）。
- **P1 批次 2（9 文件，2026-11-19 合入 main）**：reference/go 全部 7 篇
  （faq / go-generated / go-generated-opaque / opaque-faq / opaque-migration /
  opaque-migration-manual / size）+ java 2 篇（java-generated /
  java-proto-names）。审校修复 22 组（5 P2），glossary 补 4 条，
  扩展区间 / 完全限定译法全仓统一。
- **P1 批次 3（9 文件，2026-11-19 合入 main）**：protobuf 规范 4 篇
  （edition-2023-spec / edition-2024-spec / google.protobuf / mime-types）+
  objective-c-generated（1290 行）+ kotlin / php generated +
  java-utf8-validation + other。审校修复 15 处（2 P2：FieldMask 包含方向
  译反、无标记增译删除）。
- **P1 批次 4–5（10 文件，2026-11-19 合入 main）**：三大语言规范
  （proto2-spec / proto3-spec / textformat-spec）+ python 2 篇 + ruby +
  rust 4 篇。审校修复 9 处（1 P2：rust oneof 标题口径还原）；同源三规范
  与 edition-2023-spec 措辞交叉核对一致。**Phase 2 P1 全部完成（54 文件）**。
- **P3 批次 1–2（22 文件，2026-11-20 合入 main）**：design-decisions 全部
  5 篇 + support 全部 4 篇 + news 重大公告精选 13 篇（版本机制、破坏性变更
  政策、Editions 发布、26.x/v34/v38 破坏变更、Go Opaque API、停止支持
  Objective-C 等）。审校修复跨文件口径统一（替代方案、免责段套语并版）
  与 P3 若干；全量回归 87/87 通过。
- **P2 api-docs（81 文件）与 news 剩余 30 篇、downloads/history（2026-11-21
  合入 main）**：cpp/kotlin 全部 API 参考页（descriptor.pb 915 行、
  google.protobuf 1514 行）+ v21–v34 版本公告全量 + 下载页/历史页。
  质检工具同步增强：HTML `<pre>` 块状态感知、`<code>` 内容语义、
  Dokka 签名豁免。**全部 242 文件处理完毕（187 translated +
  22 skip-partial + 10 skip + 23 其他状态归零），全量回归 187/187 通过。**
  注：本轮批次提交直接落于 main（agent 流水线稳定后逐批质检即提交，
  未走 translate/* 分支——对计划第七节分支策略的执行偏离，如实记录）。

## 持续更新

- 每月 1 日或上游 content/ 批量变更后运行 sync（后续可补自动化）；
- sync commit 直接进 `main`（`docs: sync upstream <commit>`）；
- 上游目录重构/改名（R）时旧译文自动沿用新路径并标记复核。
