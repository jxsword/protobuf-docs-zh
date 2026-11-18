# 翻译风格规范（style guide）

> 本规范供每次会话的翻译 agent 与审校 agent 直接执行。与 docs/translation-plan.md
> 冲突时以计划文件为准；术语以 glossary.md 为唯一权威源。

## 一、单文件翻译 SOP（译者 agent 必须逐步执行）

1. 读取原文 + `glossary.md` + `style-guide.md`；
2. 翻译正文（遵守第二节硬性规则、第三节中文排版、第四节语气）；
3. 译文头部 frontmatter **追加**以下键（放在原有 frontmatter 末尾）：

   ```toml
   source_url = "https://protobuf.dev/<相对路径去掉 .md>/"
   upstream_commit = "<manifest 中该文件的 upstream_commit>"
   translated_at = "<YYYY-MM-DD>"
   status = "translated"
   translator = "agent"
   ```

   原 frontmatter 键名与结构不得增删改（`title`/`description` 等值翻译，
   键名原样保留）。frontmatter 分隔符（`+++` 或 `---`）沿用原文；
4. 提交审校：审校 agent 对照原文检查漏译、误译、术语一致性与 shortcode
   完整性（译者与审校必须分离，不得同人/同会话自审自过）；
5. 运行质检（两项全过才算完成，任一 FAIL 必须修复后重跑）：

   ```bash
   python tools/verify_structure.py <原文件> <译文>
   python tools/check_terms.py <译文>
   ```

6. 更新 `manifest.json` 对应条目（`status=translated`、`translated_at`、
   `translator`），每批完成单独 commit。

**update-needed 条目**：只重译上游变更段落（diff 摘要在
`tasks/diffs/<日期>/<文件名>.diff`），确认变更不影响译文时可降级为 skip
并在 manifest `notes` 写明结论；`includes/` 联动标记的 `update-needed(review)`
核对相关段落后同样降级。

## 二、硬性规则（违者质检必挂）

1. **不翻译**：代码块与行内代码的**本体**（命令行、API/字段签名、proto 定义、
   字符串字面量一律原样）、URL、图片路径、站内相对链接与锚点、HTML 标签与属性；
   代码块内**注释可译为中文（可双语）**（docs/translation-plan.md 第五节），
   全仓统一口径为译注释，须准确且不得改变代码结构；
2. **Hugo shortcode 原样保留**：`{{< ... >}}` / `{{% ... %}}` 整个标签
   逐字保留，参数一律不翻译（含 `title="Note"` 这类提示文案），
   只翻译成对 shortcode 之间的正文；
3. **frontmatter 键名不变**：仅翻译 `title`、`description`、`linkTitle`
   等值的键；`layout`、`type`、`weight`、`manualLink` 等保持原样；
4. **标题锚点不翻译**：`## 标题 {#anchor}` 中的 `{#anchor}` 逐字保留
   （站内交叉引用依赖它）；
5. **术语统一**：一律以 glossary.md 为准；glossary 中标 `-` 或「保留」的
   术语不翻译；其他术语首次出现写成「中文译名（英文原文）」，
   后文可直接用中文；新术语必须先补入 glossary.md 再使用；
6. 全部文件 IO 显式 `encoding='utf-8'`，输出 LF 换行。

## 三、中文排版

- 标点用全角：，。：；？！（）“”—— 省略号用……；
- 中文与西文/数字之间加一个空格：`使用 protoc 编译`、`最多 2^29 个字段`；
- 代码与中文之间不加额外空格（由上一条覆盖）；
- 列表、表格、标题层级与原文逐项对应，不合并、不拆分、不增删条目；
- 专有名词首现附英文原文，其余场合避免中英夹杂堆砌；
- 数字、版本号、字段号保持半角：`edition = "2024"`、`字段编号 1`。

## 四、语气

- 技术文档直陈风格；“你”不译为“您”；
- 避免翻译腔：不逐词直译长定语从句，可拆句重组；
- 祈使句直接译祈使句：“Run protoc …” → “运行 protoc …”；
- 原文的 “Note:”“Warning:” 多在 shortcode 内，正文按 alert 内容直译，
  不添加“注意：”前缀（shortcode 已表达）。

## 五、提交与分支约定

- sync commit 直接进 `main`：`docs: sync upstream <commit 前 10 位>`；
- 批量翻译走 `translate/<日期>-<批次>` 分支，审校通过后合入 `main`；
- 翻译 commit：`translate: <相对路径> (upstream <sha 前 8 位>)`；
- 禁止把翻译改动与 sync/工具改动混入同一 commit。

## 六、脚本编码规范（tools/ 下新增或修改脚本时）

- Python ≥ 3.10，仅标准库；
- 所有文件 IO 显式 `encoding='utf-8'`；文本输出统一 LF（`newline="\n"`）；
- 路径用 `pathlib`；来自 git 输出/manifest 等外部数据的相对路径必须经
  `resolve_rel`（或等价的越界校验）后再落盘；
- stdout 输出前按 `_setup_stdio()` 统一 UTF-8（Windows 控制台兼容）；
- 脚本退出码约定：0 成功；1 业务不合格（校验不通过/有告警）；2 参数或
  环境错误；4 数据不一致（快照校验失败）。
