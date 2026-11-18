#!/usr/bin/env python3
"""check_terms.py — 译文术语一致性与未翻译英文残留检查。

职责（docs/translation-plan.md 第四节 / 第八节）：
  1. 加载 glossary.md 术语表，校验译文中术语是否按统一译法翻译：
     英文术语若裸露出现（未括注英文原文）即告警；
  2. 检测未翻译英文残留：围栏代码块、行内代码、shortcode、URL、HTML 标签
     之外，出现 6 个以上连续英文单词视为疑似漏译；
  3. allowlist 白名单（tools/allowlist.txt）：路径通配整文件豁免，
     或字面子串豁免所在行；
  4. --fix 为预留参数：当前仅输出提示，不自动改写。

用法：
    python tools/check_terms.py zh/overview.md
    python tools/check_terms.py zh/            # 目录递归
    python tools/check_terms.py zh/xxx.md --fix

退出码：0 通过；1 有告警；2 参数/文件错误。
"""
from __future__ import annotations

import argparse
import datetime
import fnmatch
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ZH_DIR = ROOT / "zh"
DEFAULT_GLOSSARY = ROOT / "glossary.md"
DEFAULT_ALLOWLIST = ROOT / "tools" / "allowlist.txt"

_MIN_RESIDUE_WORDS = 6

_FENCE_RE = re.compile(r"^\s*```")
_SHORTCODE_RE = re.compile(r"\{\{[<%][^}]*[>%]\}\}")
_ANCHOR_RE = re.compile(r"\{#[^}]+\}")
_INLINE_CODE_RE = re.compile(r"`[^`]+`")
_URL_RE = re.compile(r"\bhttps?://\S+")
_HTML_TAG_RE = re.compile(r"<[^>]+>")
_MD_LINK_RE = re.compile(r"\[([^\]]*)\]\([^)]*\)")
_RESIDUE_RE = re.compile(r"(?:[A-Za-z][A-Za-z0-9'’\-]*\s+){5,}[A-Za-z][A-Za-z0-9'’\-]*")
_WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9'’\-]*")


def _setup_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


def strip_line(line: str) -> str:
    """移除行内不该参与术语/残留判定的成分。"""
    line = _SHORTCODE_RE.sub(" ", line)
    line = _ANCHOR_RE.sub(" ", line)  # 标题锚点 {#...} 原样保留，不参与判定
    line = _INLINE_CODE_RE.sub(" ", line)
    line = _URL_RE.sub(" ", line)
    line = _HTML_TAG_RE.sub(" ", line)
    line = _MD_LINK_RE.sub(lambda m: m.group(1), line)
    return line


def load_glossary(path: Path) -> list[dict]:
    """解析 glossary.md 的 markdown 表格 → [{variants, zh, remark, keep}]。

    表格式：| 英文 | 中文 | 备注 |；英文列可用 “;” 分隔多个变体；
    中文列为 “-” 表示该术语保留英文、不参与校验。
    """
    entries: list[dict] = []
    lines = path.read_text(encoding="utf-8").splitlines()
    for line in lines:
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if len(cells) < 2:
            continue
        en, zh = cells[0], cells[1]
        remark = cells[2] if len(cells) > 2 else ""
        if not en or en in ("英文", "---") or set(en) <= {"-", " ", ":"}:
            continue
        variants = [v.strip() for v in en.split(";") if v.strip()]
        # 中文列或备注列标注“保留”的条目视为保留英文
        keep = zh in ("-", "—") or "保留" in zh or "保留" in remark
        entries.append({"variants": variants, "zh": zh, "remark": remark, "keep": keep})
    return entries


def load_allowlist(path: Path) -> list[str]:
    """读取白名单：注释行（# 开头）忽略，空行忽略。"""
    if not path.exists():
        return []
    out: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s and not s.startswith("#"):
            out.append(s)
    return out


def file_allowed(rel: str, allowlist: list[str]) -> str | None:
    """整文件豁免：白名单条目含 / 或 * 或 ? 时按通配匹配相对路径。"""
    for item in allowlist:
        if any(ch in item for ch in "*/?") and fnmatch.fnmatch(rel, item):
            return item
    return None


def line_allowed(line: str, allowlist: list[str]) -> str | None:
    """行级豁免：白名单字面子串出现在该行中。"""
    for item in allowlist:
        if not any(ch in item for ch in "*/?") and item in line:
            return item
    return None


def _paren_wrapped(line: str, start: int, end: int) -> bool:
    """判断 line[start:end] 是否被中英括号直接包裹（术语首现括注英文的合法形态）。"""
    before = line[:start].rstrip()
    after = line[end:].lstrip()
    return bool(before) and before[-1] in "（(" and bool(after) and after[0] in "）)"


def _paren_spans(line: str) -> list[tuple[int, int]]:
    """收集行内全部配对括号 (start, end) span（中英文括号均支持）。"""
    pairs = {"（": "）", "(": ")"}
    spans: list[tuple[int, int]] = []
    stack: list[tuple[str, int]] = []
    for i, ch in enumerate(line):
        if ch in pairs:
            stack.append((ch, i))
        elif ch in (")", "）") and stack:
            open_ch, start = stack.pop()
            if pairs.get(open_ch) == ch:
                spans.append((start, i))
    return spans


def _inside_parens(line: str, start: int, end: int) -> bool:
    """判断 match 是否整体落在某个括号 span 内（如「默认值（default value）」中的 value）。"""
    return any(s <= start and end <= e for s, e in _paren_spans(line))


def check_terms(rel: str, text: str, glossary: list[dict], allowlist: list[str]) -> list[str]:
    """术语一致性检查：英文术语裸露出现（未括注）即告警。

    「首现括注、后文径用」语义：同一文件内，某术语首次以括注形态出现后，
    其后的裸出现不再告警。
    """
    findings: list[str] = []
    if file_allowed(rel, allowlist):
        return findings
    compiled = []
    for entry in glossary:
        if entry["keep"]:
            continue
        for variant in entry["variants"]:
            pattern = re.compile(
                r"(?<![A-Za-z0-9_])" + re.escape(variant).replace(r"\ ", r"\s+") + r"(?![A-Za-z0-9_])",
                re.IGNORECASE,
            )
            compiled.append((pattern, variant, entry["zh"]))

    # 先按 frontmatter/围栏/白名单状态收集有效正文行
    processed: list[tuple[int, str]] = []
    in_fence = False
    in_frontmatter = False
    fm_delim = ""
    for no, raw in enumerate(text.splitlines(), 1):
        s = raw.strip()
        if no == 1 and s in ("---", "+++"):
            in_frontmatter = True
            fm_delim = s
            continue
        if in_frontmatter:
            if s == fm_delim:
                in_frontmatter = False
            continue
        if _FENCE_RE.match(raw):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if line_allowed(raw, allowlist):
            continue
        processed.append((no, strip_line(raw)))

    # 第一遍：记录每个变体首个括注形态出现的行号
    first_annotated: dict[str, int] = {}
    for no, line in processed:
        for pattern, variant, _zh in compiled:
            for m in pattern.finditer(line):
                if _paren_wrapped(line, m.start(), m.end()) or _inside_parens(line, m.start(), m.end()):
                    key = variant.lower()
                    if key not in first_annotated:
                        first_annotated[key] = no

    # 第二遍：裸出现判定（首现括注行之后的裸出现豁免）
    for no, line in processed:
        for pattern, variant, zh in compiled:
            for m in pattern.finditer(line):
                if _paren_wrapped(line, m.start(), m.end()) or _inside_parens(line, m.start(), m.end()):
                    continue
                fa = first_annotated.get(variant.lower())
                if fa is not None and no >= fa:
                    continue
                snippet = line[max(0, m.start() - 24):m.end() + 24].strip()
                findings.append(
                    f"{rel}:{no}: 术语 [{variant}] 未按译名 [{zh}] 翻译 …{snippet}…"
                )
    return findings


def check_residue(rel: str, text: str, allowlist: list[str]) -> list[str]:
    """未翻译残留检查：非代码区域出现 6 词以上连续英文即告警。"""
    findings: list[str] = []
    if file_allowed(rel, allowlist):
        return findings
    in_fence = False
    in_frontmatter = False
    fm_delim = ""
    for no, raw in enumerate(text.splitlines(), 1):
        s = raw.strip()
        if no == 1 and s in ("---", "+++"):
            in_frontmatter = True
            fm_delim = s
            continue
        if in_frontmatter:
            if s == fm_delim:
                in_frontmatter = False
            continue
        if _FENCE_RE.match(raw):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if line_allowed(raw, allowlist):
            continue
        line = strip_line(raw)
        for m in _RESIDUE_RE.finditer(line):
            words = _WORD_RE.findall(m.group(0))
            if len(words) < _MIN_RESIDUE_WORDS:
                continue
            findings.append(
                f"{rel}:{no}: 疑似未翻译英文残留（{len(words)} 词）: {m.group(0).strip()[:80]}"
            )
    return findings


def collect_targets(target: Path) -> list[Path]:
    """收集待检文件：文件或目录（递归 .md）。"""
    if target.is_file():
        return [target]
    if target.is_dir():
        return sorted(target.rglob("*.md"))
    return []


def main() -> int:
    _setup_stdio()
    parser = argparse.ArgumentParser(description="译文术语一致性与未翻译残留检查")
    parser.add_argument("target", help="译文文件或目录（如 zh/overview.md 或 zh/）")
    parser.add_argument("--glossary", default=str(DEFAULT_GLOSSARY), help="术语表路径（默认 glossary.md）")
    parser.add_argument("--allowlist", default=str(DEFAULT_ALLOWLIST), help="白名单路径（默认 tools/allowlist.txt）")
    parser.add_argument("--fix", action="store_true", help="（预留）术语自动回填，当前仅提示不改动")
    args = parser.parse_args()

    target = Path(args.target)
    if not target.is_absolute():
        target = ROOT / target
    targets = collect_targets(target)
    if not targets:
        print(f"错误：目标不存在或无 md 文件: {target}")
        return 2

    glossary_path = Path(args.glossary)
    if not glossary_path.is_absolute():
        glossary_path = ROOT / glossary_path
    allowlist_path = Path(args.allowlist)
    if not allowlist_path.is_absolute():
        allowlist_path = ROOT / allowlist_path
    if not glossary_path.exists():
        print(f"错误：术语表不存在: {glossary_path}")
        return 2

    glossary = load_glossary(glossary_path)
    allowlist = load_allowlist(allowlist_path)
    if args.fix:
        print("[--fix] 预留参数：术语自动回填将在术语表定稿后实现，本次仅执行检查。")

    term_findings: list[str] = []
    residue_findings: list[str] = []
    checked = 0
    for path in targets:
        try:
            rel = path.relative_to(ROOT).as_posix()
        except ValueError:
            rel = path.name
        text = path.read_text(encoding="utf-8")
        term_findings.extend(check_terms(rel, text, glossary, allowlist))
        residue_findings.extend(check_residue(rel, text, allowlist))
        checked += 1

    print(f"== check_terms: {checked} 个文件，术语表 {len(glossary)} 条 ==")
    for item in term_findings:
        print(f"  术语  {item}")
    for item in residue_findings:
        print(f"  残留  {item}")
    total = len(term_findings) + len(residue_findings)
    print(f"结果: {total} 条告警" if total else "结果: 通过，无告警")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
