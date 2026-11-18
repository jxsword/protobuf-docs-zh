#!/usr/bin/env python3
"""verify_structure.py — 原文/译文结构一致性校验。

对比原文与译文的：标题层级与锚点序列、代码块数量与语言标注序列、表格行列、
图片引用、链接目标、Hugo shortcode（{{< >}} / {{% %}}）、frontmatter 键集合。
任一类别不一致即失败，退出码 1。

用法：
    python tools/verify_structure.py <原文件> <译文>
    # 路径可传相对仓库根的路径（如 overview.md），自动按原文/译文目录解析
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UPSTREAM_CONTENT = ROOT / "upstream" / "content"
ZH_DIR = ROOT / "zh"

# 译文允许新增的 frontmatter 键（翻译流水线元数据）
TRANSLATION_EXTRA_KEYS = {"source_url", "upstream_commit", "translated_at", "status", "translator"}

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
_ANCHOR_RE = re.compile(r"\{#([A-Za-z0-9_\-]+)\}")
_IMG_MD_RE = re.compile(r"!\[[^\]]*\]\(([^)\s]+)")
_LINK_MD_RE = re.compile(r"(?<!\!)\[[^\]]*\]\(([^)\s]+)")
_REFDEF_RE = re.compile(r"^\s*\[[^\]]+\]:\s*(\S+)")
_HREF_RE = re.compile(r"\bhref=\"([^\"]+)\"")
_SRC_HTML_RE = re.compile(r"\bsrc=\"([^\"]+)\"")
_SHORTCODE_RE = re.compile(r"\{\{[<%][^}]*[>%]\}\}")


def _setup_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


def resolve_input(arg: str, kind: str) -> Path:
    """把命令行参数解析为实际文件路径；kind 为 src 时优先原文目录，dst 优先 zh/。"""
    p = Path(arg)
    if p.is_absolute():
        return p
    candidates = [ROOT / arg]
    if kind == "src":
        candidates.append(UPSTREAM_CONTENT / arg)
    else:
        candidates.append(ZH_DIR / arg)
    for cand in candidates:
        if cand.exists():
            return cand
    return candidates[-1]


def read_source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def split_frontmatter(text: str) -> tuple[set[str], str, str | None]:
    """拆出 frontmatter 顶层键集合与正文；返回 (keys, body, error)。"""
    lines = text.splitlines()
    if not lines or lines[0].strip() not in ("---", "+++"):
        return set(), text, None
    delim = lines[0].strip()
    for i in range(1, len(lines)):
        if lines[i].strip() == delim:
            fm_lines = lines[1:i]
            body = "\n".join(lines[i + 1:])
            return parse_fm_keys(fm_lines, delim), body, None
    return set(), text, "frontmatter 未闭合"


def parse_fm_keys(fm_lines: list[str], delim: str) -> set[str]:
    """解析 frontmatter 顶层键（TOML +++ / YAML ---，含 TOML 节名）。"""
    keys: set[str] = set()
    if delim == "+++":
        assign = re.compile(r"^([A-Za-z_][\w-]*)\s*=")
        section = re.compile(r"^\[([A-Za-z0-9_.\-]+)\]$")
        for line in fm_lines:
            s = line.strip()
            m = section.match(s)
            if m:
                keys.add(f"[{m.group(1)}]")
                continue
            m = assign.match(s)
            if m:
                keys.add(m.group(1))
    else:
        pair = re.compile(r"^([A-Za-z_][\w-]*):")
        for line in fm_lines:
            m = pair.match(line)
            if m:
                keys.add(m.group(1))
    return keys


def iter_no_fence(body: str):
    """按行迭代正文，跳过围栏代码块内部；yields (行文本, 是否在围栏内)。"""
    in_fence = False
    for line in body.splitlines():
        s = line.strip()
        if s.startswith("```"):
            in_fence = not in_fence
            yield line, True  # 围栏行本身
            continue
        yield line, in_fence


def extract_headings(body: str) -> tuple[list[tuple[int, str | None]], list[str | None]]:
    """返回标题 (级别, 锚点) 序列与纯锚点序列（围栏内的 # 行不计）。"""
    levels: list[tuple[int, str | None]] = []
    anchors: list[str | None] = []
    for line, fenced in iter_no_fence(body):
        if fenced:
            continue
        m = _HEADING_RE.match(line)
        if m:
            am = _ANCHOR_RE.search(m.group(2))
            anchor = am.group(1) if am else None
            levels.append((len(m.group(1)), anchor))
            anchors.append(anchor)
    return levels, anchors


def extract_code_blocks(body: str) -> list[str]:
    """返回代码块语言标注序列（无标注为空串）。

    注意：不能用 iter_no_fence——围栏起始行会被标记为“围栏内”而被跳过。
    """
    langs: list[str] = []
    in_fence = False
    for line in body.splitlines():
        s = line.strip()
        if not s.startswith("```"):
            continue
        if not in_fence:
            in_fence = True
            info = s[3:].strip()
            langs.append(info.split()[0] if info else "")
        else:
            in_fence = False
    return langs


def _table_shape(rows: list[str]) -> tuple[int, int]:
    header = rows[0]
    cells = [c for c in header.split("|") if c.strip()]
    return len(rows), len(cells)


def extract_tables(body: str) -> list[tuple[int, int]]:
    """返回 GFM 管道表 (行数, 列数) 序列。"""
    tables: list[tuple[int, int]] = []
    cur: list[str] = []
    for line, fenced in iter_no_fence(body):
        s = line.strip()
        if fenced:
            if cur:
                tables.append(_table_shape(cur))
                cur = []
            continue
        if s.startswith("|"):
            cur.append(s)
        else:
            if len(cur) >= 2:
                tables.append(_table_shape(cur))
            cur = []
    if len(cur) >= 2:
        tables.append(_table_shape(cur))
    return tables


def extract_images(body: str) -> list[str]:
    """图片引用目标：Markdown 图片 + HTML src 属性。"""
    md_imgs = _IMG_MD_RE.findall(body)
    html_srcs = _SRC_HTML_RE.findall(body)
    return md_imgs + html_srcs


def extract_links(body: str) -> list[str]:
    """链接目标：Markdown 行内链接 + 参考式定义 + HTML href 属性。"""
    no_img = _IMG_MD_RE.sub("", body)
    inline = _LINK_MD_RE.findall(no_img)
    refdefs = _REFDEF_RE.findall(no_img)
    hrefs = _HREF_RE.findall(no_img)
    return inline + refdefs + hrefs


def extract_shortcodes(body: str) -> list[str]:
    """返回归一化空白后的完整 shortcode 标签序列（参数必须原样保留）。"""
    tags = _SHORTCODE_RE.findall(body)
    return [re.sub(r"\s+", " ", t) for t in tags]


def compare(name: str, src_items, dst_items, fmt) -> list[str]:
    """比较序列/集合，返回差异描述行（空列表即通过）。"""
    if list(src_items) == list(dst_items):
        return []
    return [f"{name} 不一致:\n  原文: {fmt(src_items)}\n  译文: {fmt(dst_items)}"]


def verify(src_path: Path, dst_path: Path) -> tuple[list[str], list[str]]:
    """执行全部结构校验，返回 (失败项, 通过项)。"""
    failures: list[str] = []
    passes: list[str] = []

    src_text = read_source(src_path)
    dst_text = read_source(dst_path)
    src_keys, src_body, src_err = split_frontmatter(src_text)
    dst_keys, dst_body, dst_err = split_frontmatter(dst_text)

    if src_err or dst_err:
        failures.append(f"frontmatter 解析失败: {src_err or dst_err}")
        return failures, passes

    # 1) frontmatter 键集合：官方键不得缺失；译文仅可追加白名单元数据键
    missing = src_keys - dst_keys
    extra = dst_keys - src_keys - TRANSLATION_EXTRA_KEYS
    if missing:
        failures.append(f"frontmatter 缺少官方键: {sorted(missing)}")
    else:
        passes.append(f"frontmatter 键集合（官方键 {len(src_keys)} 个齐全）")
    if extra:
        failures.append(f"frontmatter 出现非白名单新增键: {sorted(extra)}")

    # 2) 标题层级与锚点
    src_levels, src_anchors = extract_headings(src_body)
    dst_levels, dst_anchors = extract_headings(dst_body)
    if [lv for lv, _ in src_levels] != [lv for lv, _ in dst_levels]:
        failures.append(
            f"标题层级序列不一致:\n  原文: {[lv for lv, _ in src_levels]}\n  译文: {[lv for lv, _ in dst_levels]}"
        )
    else:
        passes.append(f"标题层级序列（{len(src_levels)} 个标题）")
    if src_anchors != dst_anchors:
        failures.append(f"标题锚点序列不一致:\n  原文: {src_anchors}\n  译文: {dst_anchors}")
    else:
        passes.append(f"标题锚点序列（{sum(1 for a in src_anchors if a)} 个锚点）")

    # 3) 代码块语言标注序列
    src_langs = extract_code_blocks(src_body)
    dst_langs = extract_code_blocks(dst_body)
    if src_langs != dst_langs:
        failures.append(f"代码块语言标注序列不一致:\n  原文: {src_langs}\n  译文: {dst_langs}")
    else:
        passes.append(f"代码块（{len(src_langs)} 个，语言标注一致）")

    # 4) 表格行列
    src_tables = extract_tables(src_body)
    dst_tables = extract_tables(dst_body)
    if src_tables != dst_tables:
        failures.append(f"表格 (行,列) 序列不一致:\n  原文: {src_tables}\n  译文: {dst_tables}")
    else:
        passes.append(f"表格（{len(src_tables)} 张，行列一致）")

    # 5) 图片引用
    src_imgs = sorted(extract_images(src_body))
    dst_imgs = sorted(extract_images(dst_body))
    if src_imgs != dst_imgs:
        failures.append(f"图片引用不一致:\n  原文: {src_imgs}\n  译文: {dst_imgs}")
    else:
        passes.append(f"图片引用（{len(src_imgs)} 处）")

    # 6) 链接目标
    src_links = sorted(extract_links(src_body))
    dst_links = sorted(extract_links(dst_body))
    if src_links != dst_links:
        failures.append(f"链接目标不一致:\n  原文: {src_links}\n  译文: {dst_links}")
    else:
        passes.append(f"链接目标（{len(src_links)} 处）")

    # 7) Hugo shortcode（完整标签含参数，必须逐字一致）
    src_sc = extract_shortcodes(src_body)
    dst_sc = extract_shortcodes(dst_body)
    if src_sc != dst_sc:
        failures.append(f"shortcode 序列不一致（参数须原样保留）:\n  原文: {src_sc}\n  译文: {dst_sc}")
    else:
        passes.append(f"shortcode（{len(src_sc)} 个，逐字一致）")

    return failures, passes


def main() -> int:
    _setup_stdio()
    parser = argparse.ArgumentParser(description="原文/译文结构一致性校验")
    parser.add_argument("source", help="原文文件路径（可传相对 content/ 的路径）")
    parser.add_argument("translated", help="译文文件路径（可传相对 zh/ 的路径）")
    args = parser.parse_args()

    src_path = resolve_input(args.source, "src")
    dst_path = resolve_input(args.translated, "dst")
    if not src_path.exists():
        print(f"错误：原文不存在: {src_path}")
        return 2
    if not dst_path.exists():
        print(f"错误：译文不存在: {dst_path}")
        return 2

    failures, passes = verify(src_path, dst_path)
    try:
        dst_display = dst_path.relative_to(ROOT).as_posix()
    except ValueError:
        dst_display = str(dst_path)
    print(f"== verify_structure: {src_path.name} vs {dst_display} ==")
    for item in passes:
        print(f"  PASS  {item}")
    for item in failures:
        print(f"  FAIL  {item}")
    total = len(passes) + len(failures)
    print(f"结果: {len(passes)}/{total} 项通过")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
