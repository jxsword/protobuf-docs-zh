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

数据来源 `manifest.json`（2026-11-18 初始化，上游 `f72a6a648b`）。

**按状态**（总计 242 个上游 md 文件）：

| 状态 | 数量 | 说明 |
| --- | --- | --- |
| pending | 217 | 待翻译 |
| translated | 0 | 已完成并通过质检 |
| update-needed | 0 | 上游变更，需按 diff 更新 |
| skip-partial | 22 | 列表页，仅译标题/描述与导语 |
| skip | 3 | 站点功能页，不翻译 |
| removed | 0 | 上游已删除（译文归档 zh/_archived/） |

**按优先级 / 待办**（优先级定义见 docs/translation-plan.md 第六节）：

| 优先级 | 范围 | 文件数 | 待办 |
| --- | --- | --- | --- |
| P0 | Phase 1 核心阅读路径（首页、overview、installation、getting-started、programming-guides、best-practices、editions） | 35 | 31 |
| P1 | Phase 2 reference 人工撰写页（非 api-docs） | 54 | 41 |
| P2 | Phase 3 reference/**/api-docs 自动生成页（可延后） | 83 | 81 |
| P3 | Phase 4 news、design-decisions、support、history、downloads | 70 | 64 |

## skip 清单（Phase 0 逐个确认结果）

**整页 skip（status=skip，3 个）**——均为站点功能页，无正文：

| 文件 | 确认结果 |
| --- | --- |
| `navbar.md` | 纯导航链接列表（4 行链接），无正文，不翻译 |
| `forum-link.md` | 仅 frontmatter（标题 + 论坛跳转链接），不翻译 |
| `search.md` | 仅 frontmatter（标题 + 搜索布局占位），不翻译 |

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

## 持续更新

- 每月 1 日或上游 content/ 批量变更后运行 sync（后续可补自动化）；
- sync commit 直接进 `main`（`docs: sync upstream <commit>`）；
- 上游目录重构/改名（R）时旧译文自动沿用新路径并标记复核。
