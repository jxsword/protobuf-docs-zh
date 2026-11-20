#!/usr/bin/env python3
"""build_site.py — 组装 Hugo 中文站构建目录（M4）。

对应 docs/translation-plan.md 第七节「持续更新机制」的发布设计
（决策记录 DR-003/004/005）：

  - 方案A 混合站：content/ = .upstream/content 全量（英文兜底）+ zh/ 的
    232 个中文 md 同路径覆盖；全站链接零 404，未译页显示英文原文；
  - 构建目录以 .upstream/ 全站为底（config.toml / layouts / static /
    go.mod），中文页页脚声明通过 layout override + config 改写注入，
    **不污染 zh/ 源文件**；
  - baseURL / title / languageCode 改写为中文站信息；
  - 移除上游 CNAME（避免误绑 protobuf.dev）、Google Analytics ID 与
    GCS 自定义搜索（改用 docsy 自带离线搜索）；
  - 输出构建统计并与 manifest 交叉校验（中文页数 == translated +
    skip-partial）。

组装完成后由 Hugo 完成渲染：
    cd build_site && npm install && hugo --gc --minify -d public
本地预览：
    cd build_site && hugo server

用法：
    python tools/build_site.py                  # 完整构建（zh/ 覆盖）
    python tools/build_site.py --upstream-only  # 纯上游站（验证 docsy 环境）
    python tools/build_site.py --base-url URL --repo-url URL

依赖：Python >= 3.10（仅标准库）。所有文件 IO 显式 utf-8，输出 LF。
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import stat
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UPSTREAM_DIR = ROOT / ".upstream"
ZH_DIR = ROOT / "zh"
ARCHIVE_DIR = ZH_DIR / "_archived"
MANIFEST_PATH = ROOT / "manifest.json"

# 默认发布地址与仓库（DR-005：默认 GitHub Pages 项目域名）
DEFAULT_BASE_URL = "https://jxsword.github.io/protobuf-docs-zh/"
DEFAULT_REPO_URL = "https://github.com/jxsword/protobuf-docs-zh"

# 上游仓库文件中与站点构建无关的部分（不复制进构建目录）
SKELETON_EXCLUDES = [
    ".git",
    ".github",
    "CNAME",  # 上游绑定 protobuf.dev 的 CNAME，镜像站必须排除（DR-005）
    "README.md",
    "CONTRIBUTING.md",
    "config.toml",  # 由本脚本改写生成
    "package.json",  # 由本脚本重写（补 postcss-cli）
    "package-lock.json",
]

# 复制的构建目录相对路径（content/ 单独处理，便于统计）
SKELETON_ITEMS = ["layouts", "static", "go.mod", "go.sum", "LICENSE"]


def _setup_stdio() -> None:
    """Windows 控制台默认代码页可能不是 UTF-8，统一按 UTF-8 输出。"""
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


def resolve_rel(rel: str, base: Path) -> Path:
    """校验并构造 base 内的路径，越界即拒绝（与 sync_upstream.py 同型）。"""
    target = (base / rel).resolve()
    if not target.is_relative_to(base.resolve()):
        raise ValueError(f"拒绝越界路径: {rel!r}")
    return target


def write_text_file(base: Path, rel: str, text: str) -> Path:
    """在 base 内写入 rel 文本文件（utf-8、LF）；越界即拒绝。"""
    target = (base / rel).resolve()
    if not target.is_relative_to(base.resolve()):
        raise ValueError(f"拒绝越界写入: {rel!r}")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8", newline="\n")
    return target


# ---------------------------------------------------------------------------
# config.toml 改写：逐项定向替换，任一项匹配失败即报错（上游漂移检测）
# ---------------------------------------------------------------------------

def rewrite_config(text: str, base_url: str, repo_url: str) -> str:
    """基于上游 config.toml 做定向改写；替换失败（未找到目标）则抛错。"""

    def must_sub(pattern: str, repl: str, label: str, *, count: int = 1) -> None:
        nonlocal text
        new, n = re.subn(pattern, repl, text, count=count, flags=re.MULTILINE)
        if n < count:
            raise ValueError(
                f"config 改写失败（{label}）：未匹配到 {pattern!r}，上游可能已变更"
            )
        text = new

    # 发布地址
    must_sub(r"^baseURL = .*$", f"baseURL = '{base_url}'", "baseURL")
    # 语言与站点信息
    must_sub(r"^languageCode = 'en-us'$", "languageCode = 'zh-CN'", "languageCode")
    must_sub(r"Protocol Buffers Documentation", "Protocol Buffers 中文文档", "title", count=2)
    must_sub(r'^defaultContentLanguage = "en"$', 'defaultContentLanguage = "zh-cn"',
             "defaultContentLanguage")
    must_sub(r"^enableMissingTranslationPlaceholders = true$",
             "enableMissingTranslationPlaceholders = false", "missing-translation-placeholders")
    # [languages.en] → [languages.zh-cn]（语言键用 zh-cn 才能命中 docsy 自带的
    # i18n/zh-cn.toml 中文 UI 文案；缺的 4 个 feedback 键本站已禁用，无影响）
    must_sub(r"\[languages\.en\]", "[languages.zh-cn]", "languages.en")
    must_sub(r'languageName ="English"', 'languageName = "简体中文"', "languageName")
    # 搜索：移除上游 GCS 引擎，并将上游已有的 offlineSearch=false 切换为 true
    # （docsy 自带 Lunr 离线搜索，无外部依赖；注意上游两键都存在，不能重复插入）
    must_sub(r'^gcs_engine_id = "[0-9a-f]+"$',
             '# gcs_engine_id = "..."  # 上游 Google 自定义搜索引擎，镜像站不使用',
             "gcs_engine_id")
    must_sub(r'^offlineSearch = false$', 'offlineSearch = true', "offlineSearch")
    # 移除上游 Google Analytics（镜像站不向 Google 上报）
    must_sub(r'^id = "G-[0-9A-Z]+"$',
             '# id = "G-..."  # 上游 Google Analytics ID，镜像站不启用', "google-analytics")
    # github_repo 改指翻译仓库（页脚许可声明链接使用；页面 meta 链接由 override 重定义）
    must_sub(r"^github_repo = .*$", f'github_repo = "{repo_url}"', "github_repo")
    # docsy import 挂载覆盖：剔除 docsy 自带 hugo.yaml 里指向 ../../node_modules
    # 的 npm 兼容挂载（Hugo ≥0.148 的 mount 校验拒绝 "mount source must be a
    # local path"，且 Hugo modules 方式下用不到；Hugo 0.121–0.146 还有模块合并
    # 丢失项目 [languages] 的缺陷，0.152.0 实测亦可 → 本项目锁定 0.148.2）
    must_sub(
        r'  \[\[module\.imports\]\]\n    path = "github\.com/google/docsy"\n    disable = false\n',
        '  [[module.imports]]\n'
        '    path = "github.com/google/docsy"\n'
        '    disable = false\n'
        '    # 覆盖 docsy 自带 hugo.yaml 的 mounts：剔除指向 ../../node_modules 的\n'
        '    # npm 兼容挂载（新版 Hugo 校验拒绝，且 Hugo modules 方式下用不到）\n'
        '    [[module.imports.mounts]]\n'
        '      source = "assets"\n'
        '      target = "assets"\n'
        '    [[module.imports.mounts]]\n'
        '      source = "i18n"\n'
        '      target = "i18n"\n'
        '    [[module.imports.mounts]]\n'
        '      source = "layouts"\n'
        '      target = "layouts"\n'
        '    [[module.imports.mounts]]\n'
        '      source = "static"\n'
        '      target = "static"\n',
        "docsy-import-mounts",
    )

    return text + CASCADE_TOML


# Kotlin api-docs 子树侧栏对齐（上游对齐）：
#   reference/kotlin/api-docs/protobuf-kotlin/ 是 Dokka 生成的目录树
#   （protobuf-kotlin/ 本身无 _index.md = 隐式 section；其下多个 _index.md
#   无 frontmatter = 空 title）。上游 Hugo 0.121 不把隐式 section 列入
#   .Sections，因此线上站侧栏中 api-docs 呈 without-child、该子树不可见；
#   Hugo 0.146+ 会把它们以空标题条目渲染进侧栏（kotlin 区块大空白的根源）。
#   docsy 侧栏模板用 toc_hide 过滤条目（sidebar-tree.html:51，全模板唯一用途），
#   此处用 cascade 向该子树注入 toc_hide=true 复现上游可见性——页面照常渲染、
#   URL 与 sitemap 均不受影响（线上站 sitemap 同样包含这些页面）。
CASCADE_TOML = """
# Kotlin api-docs 子树侧栏对齐（背景见 tools/build_site.py 内注释）
[[cascade]]
  toc_hide = true
  [cascade._target]
    path = "**/api-docs/protobuf-kotlin/**"
"""


# ---------------------------------------------------------------------------
# layout override：页脚注入翻译声明（DR-003），不污染 zh/ 源文件
# ---------------------------------------------------------------------------

FOOTER_HTML = """{{ $links := .Site.Params.links }}
{{ $gh_repo := .Site.Params.github_repo }}
<footer class="bg-dark py-5 row d-print-none">
  <div class="container-fluid mx-sm-5">
    <div class="row">
      <div class="col-6 col-sm-4 text-xs-center order-sm-2">
        {{ with $links }}
        {{ with index . "user"}}
        {{ template "footer-links-block"  . }}
        {{ end }}
        {{ end }}
      </div>
      <div class="col-6 col-sm-4 text-right text-xs-center order-sm-3">
        {{ with $links }}
        {{ with index . "developer"}}
        {{ template "footer-links-block"  . }}
        {{ end }}
        {{ end }}
      </div>
      <div class="col-12 col-sm-4 text-center py-2 order-sm-2">
        {{ if .Params.source_url }}
        <div class="small mb-1" style="color: #d3d3d3;">
          本文为非官方中文翻译，<a class="text-light" href="{{ .Params.source_url }}" target="_blank" rel="noopener">查看英文原文</a>，内容以英文原文为准。<br>
          译文由 <a class="text-light" href="{{ $gh_repo }}" target="_blank" rel="noopener">protobuf-docs-zh</a> 项目以
          <a class="text-light" href="{{ $gh_repo }}/blob/main/LICENSE" target="_blank" rel="noopener">BSD-3-Clause</a> 许可分发；原文版权归 Google LLC 所有。
        </div>
        {{ else }}
        <div class="small mb-1" style="color: #d3d3d3;">
          本页为英文原文，尚未翻译。已翻译页面以中文呈现，译文与原文不一致时以英文原文为准。
        </div>
        {{ end }}
        {{ with .Site.Params.copyright }}<small class="text-white">&copy; {{ now.Year}} {{ .}} {{ T "footer_all_rights_reserved" }}</small>{{ end }}
        <div class="small mt-1" style="color: #d3d3d3;">
          本站为 <a class="text-light" href="https://protobuf.dev" target="_blank" rel="noopener">protobuf.dev</a>
          的非官方中文镜像（社区翻译项目），与 Google 无隶属或背书关系。
        </div>
      </div>
    </div>
  </div>
</footer>
{{ define "footer-links-block" }}
<ul class="list-inline mb-0">
  {{ range . }}
  <li class="list-inline-item mx-2 h3" data-toggle="tooltip" data-placement="top" title="{{ .name }}" aria-label="{{ .name }}">
    <a class="text-white" target="_blank" rel="noopener" href="{{ .url }}" aria-label="{{ .name }}">
      <i class="{{ .icon }}"></i>
    </a>
  </li>
  {{ end }}
</ul>
{{ end }}
"""

# 页面 meta 链接 override：中文页提供「查看英文原文」，去掉指向上游仓库的
# Edit/View 链接（上游文件路径与译文仓库不一致，保留会产生 404 链接）
PAGE_META_LINKS_HTML = """{{ if .File }}
<div class="td-page-meta ml-2 pb-1 pt-2 mb-0">
  {{ with .Params.source_url }}
  <a href="{{ . }}" target="_blank" rel="noopener"><i class="fa-solid fa-file-lines fa-fw"></i> 查看英文原文</a>
  {{ end }}
</div>
{{ end }}
"""

# build_site/package.json：docsy 的 SCSS 构建需要 postcss-cli + autoprefixer
PACKAGE_JSON = """{
  "dependencies": {
    "autoprefixer": "^10.4.7",
    "postcss-cli": "^10.1.0"
  }
}
"""


# ---------------------------------------------------------------------------
# 组装主流程
# ---------------------------------------------------------------------------

def collect_zh_files() -> list[tuple[str, Path]]:
    """收集 zh/ 下全部 md（排除 _archived/），返回 (相对路径, 源路径) 列表。"""
    result: list[tuple[str, Path]] = []
    for path in sorted(ZH_DIR.rglob("*.md")):
        if ARCHIVE_DIR in path.parents:
            continue
        result.append((path.relative_to(ZH_DIR).as_posix(), path))
    return result


def check_manifest(zh_rels: set[str]) -> set[str]:
    """中文页集合与 manifest 的 translated + skip-partial 齐集交叉校验。"""
    if not MANIFEST_PATH.exists():
        raise FileNotFoundError(f"manifest.json 不存在: {MANIFEST_PATH}")
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    entries = manifest.get("files", manifest)
    expected: set[str] = set()
    for rel, info in entries.items():
        status = info.get("status", "") if isinstance(info, dict) else str(info)
        if status in ("translated", "skip-partial"):
            expected.add(rel)
    missing = expected - zh_rels   # manifest 记为已译但 zh/ 缺文件
    extra = zh_rels - expected     # zh/ 有但 manifest 未记为已译
    if missing or extra:
        raise ValueError(
            "manifest 交叉校验失败:\n"
            f"  manifest 记为已译但 zh/ 缺文件 ({len(missing)}): {sorted(missing)[:5]}\n"
            f"  zh/ 有文件但 manifest 未记为已译 ({len(extra)}): {sorted(extra)[:5]}"
        )
    return expected


def copy_tree(src: Path, dst: Path) -> None:
    """递归复制目录。"""
    shutil.copytree(src, dst, dirs_exist_ok=True)


def _force_remove(func, path, _exc) -> None:
    """删除回调：清除只读位后重试（Windows 杀软/索引器短暂占用文件时兜底）。"""
    try:
        os.chmod(path, stat.S_IWRITE)
    except OSError:
        pass
    func(path)


def rmtree_robust(path: Path) -> None:
    """删除目录：对 Windows 文件占用做最多 5 次重试。"""
    if not path.exists():
        return
    last_err: PermissionError | None = None
    for _ in range(5):
        try:
            if sys.version_info >= (3, 12):
                shutil.rmtree(path, onexc=_force_remove)
            else:
                shutil.rmtree(path, onerror=_force_remove)
            return
        except PermissionError as e:
            last_err = e
            time.sleep(1.0)
    raise last_err


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="组装 Hugo 中文站构建目录（M4）")
    parser.add_argument("--out", default="build_site",
                        help="构建输出目录（相对仓库根，默认 build_site/，不入库）")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL,
                        help=f"发布地址（默认 {DEFAULT_BASE_URL}）")
    parser.add_argument("--repo-url", default=DEFAULT_REPO_URL,
                        help=f"翻译仓库地址（默认 {DEFAULT_REPO_URL}）")
    parser.add_argument("--upstream-only", action="store_true",
                        help="仅组装纯上游站（不覆盖 zh/，用于验证 docsy 构建环境）")
    args = parser.parse_args(argv)

    out_dir = resolve_rel(args.out, ROOT)

    # 前置校验
    if not (UPSTREAM_DIR / "config.toml").exists() or not (UPSTREAM_DIR / "content").is_dir():
        raise FileNotFoundError(f".upstream/ 不完整（需 config.toml 与 content/）: {UPSTREAM_DIR}")

    zh_files = collect_zh_files()
    zh_rels = {rel for rel, _ in zh_files}
    expected = check_manifest(zh_rels)
    if not args.upstream_only and len(expected) != len(zh_rels):
        raise ValueError(f"中文页数 ({len(zh_rels)}) != manifest translated+skip-partial ({len(expected)})")

    # 1. 清空并重建输出目录
    rmtree_robust(out_dir)
    out_dir.mkdir(parents=True)
    print(f"[1/5] 构建目录: {out_dir}（已清空重建）")

    # 2. 复制上游骨架（SKELETON_EXCLUDES 中的条目跳过）
    copied_skeleton = 0
    for name in SKELETON_ITEMS:
        src = UPSTREAM_DIR / name
        if not src.exists():
            continue
        dst = out_dir / name
        if src.is_dir():
            copy_tree(src, dst)
        else:
            shutil.copy2(src, dst)
        copied_skeleton += 1
    print(f"[2/5] 上游骨架: {copied_skeleton} 项（CNAME、.github、上游 package.json / "
          "config.toml 已排除）")

    # 3. content/ = 上游全量（英文兜底）+ zh/ 同路径覆盖（方案A，DR-003）
    content_dir = out_dir / "content"
    copy_tree(UPSTREAM_DIR / "content", content_dir)

    # 3b. api-docs 资产树转为 static 原样提供（上游对齐）：
    #     reference/**/api-docs/ 下的 Dokka/Doxygen/Doctum HTML 及 js/css/fonts
    #     等非 md 文件，上游（Hugo 0.121）作为静态文件服务（URL 保留 .html）；
    #     Hugo 0.146+ 会把 content 中的 .html 提升为无扩展名独立页面 →
    #     侧栏出现数百个空标题条目（页脚大空白 + 截断告警），
    #     manualLink 指向的 *.html 目标 404，API 文档内部相对链接断裂。
    #     移动到 static/ 同路径后与线上站 URL 结构完全一致。
    static_dir = out_dir / "static"
    moved_assets = 0
    for f in sorted(content_dir.rglob("*")):
        if not f.is_file() or f.suffix == ".md":
            continue
        rel_parts = f.relative_to(content_dir).parts
        if "api-docs" in rel_parts or f.suffix == ".html":
            dst = static_dir / Path(*rel_parts)
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(f), str(dst))
            moved_assets += 1
    print(f"[3/5] content/ 上游全量组装；api-docs 资产树转 static: {moved_assets} 个文件")

    # 3c. 剥离 md 文件首行的 mdformat 全局注释（仅构建副本，不触碰 .upstream 与 zh/）：
    #     上游 7 个 api-docs-link.md 跳转页（2022 年 Copybara 导入起）在 frontmatter
    #     之前有 `<!-- mdformat global-off -->`；Hugo 0.121 容忍该前导注释并解析
    #     其后的 frontmatter，0.146+ 不再容忍 → 标题/weight/manualLink 全部丢失，
    #     侧栏出现空条目。剥离后与上游解析行为一致。zh/ 译文无此注释。
    stripped_md = 0
    for md in sorted(content_dir.rglob("*.md")):
        text = md.read_text(encoding="utf-8")
        if text.lstrip().startswith("<!-- mdformat"):
            lines = text.split("\n")
            i = next(i for i, line in enumerate(lines) if line.strip().startswith("<!-- mdformat"))
            del lines[i]
            if i < len(lines) and lines[i].strip() == "":
                del lines[i]
            md.write_text("\n".join(lines), encoding="utf-8", newline="\n")
            stripped_md += 1
    if stripped_md:
        print(f"      剥离前导 mdformat 注释: {stripped_md} 个 md（修复 api-docs-link 跳转页 frontmatter）")

    upstream_md = list(content_dir.rglob("*.md"))
    non_md = [p for p in content_dir.rglob("*") if p.is_file() and p.suffix != ".md"]
    print(f"      content/ 最终: {len(upstream_md)} 个 md + {len(non_md)} 个非 md 资源")

    zh_overlaid = 0
    if not args.upstream_only:
        for rel, src in zh_files:
            dst = resolve_rel(rel, content_dir)
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            zh_overlaid += 1
        print(f"      zh/ 中文覆盖: {zh_overlaid} 个 md（{len(upstream_md) - zh_overlaid} 个英文兜底页）")

    # 4. config 改写 + layout override
    upstream_config = (UPSTREAM_DIR / "config.toml").read_text(encoding="utf-8")
    write_text_file(out_dir, "config.toml", rewrite_config(upstream_config, args.base_url, args.repo_url))
    write_text_file(out_dir, "package.json", PACKAGE_JSON)
    write_text_file(out_dir, "layouts/partials/footer.html", FOOTER_HTML)
    write_text_file(out_dir, "layouts/partials/page-meta-links.html", PAGE_META_LINKS_HTML)
    print(f"[4/5] config 改写（baseURL={args.base_url}, zh 站信息, 离线搜索）+ "
          "footer / page-meta-links override 完成")

    # 5. 构建统计与下一步提示
    print("[5/5] 构建统计:")
    print(f"      中文覆盖页      : {zh_overlaid}")
    print(f"      英文兜底 md     : {len(upstream_md) - zh_overlaid}")
    print(f"      非 md 资源文件  : {len(non_md)}")
    if zh_overlaid:
        fallback = sorted({p.relative_to(content_dir).as_posix() for p in upstream_md} - zh_rels)
        print("      英文兜底页清单（应为 skip 功能页）:")
        for rel in fallback:
            print(f"        - {rel}")
    print("")
    print("下一步：")
    print(f"  cd {out_dir}")
    print("  npm install                    # postcss-cli + autoprefixer（docsy SCSS 需要）")
    print("  # 注意：docsy 的 postcss.config.js 从模块缓存目录解析插件，需设置 NODE_PATH：")
    print("  #   export NODE_PATH=$(npm root -g)   # 或指向本地 node_modules")
    print("  hugo --gc --minify -d public   # 正式构建（本项目锁定 Hugo extended 0.148.2）")
    print("  hugo server                    # 本地预览 http://127.0.0.1:1313/")
    return 0


if __name__ == "__main__":
    _setup_stdio()
    try:
        sys.exit(main())
    except (ValueError, FileNotFoundError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(2)
