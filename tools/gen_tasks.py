#!/usr/bin/env python3
"""gen_tasks.py — 依据 manifest.json 生成翻译任务清单 tasks/pending-<date>.md。

优先级按 docs/translation-plan.md 第六节：
  P0  Phase 1 核心阅读路径：首页、overview、installation、getting-started、
      programming-guides、best-practices、editions
  P1  Phase 2 reference 人工撰写页（非 api-docs）
  P2  Phase 3 reference/**/api-docs 自动生成页（可延后）
  P3  Phase 4 news、design-decisions、support、history、downloads

任务取 manifest 中 status ∈ {pending, update-needed} 的条目；每批不超过 10 个
文件；update-needed 附 diff 摘要位置（tasks/diffs/ 下同名 .diff 文件）。

用法：
    python tools/gen_tasks.py
"""
from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = ROOT / "manifest.json"
TASKS_DIR = ROOT / "tasks"
DIFFS_DIR = TASKS_DIR / "diffs"
BATCH_SIZE = 10

PRIORITY_LABELS = {
    "P0": "Phase 1 核心阅读路径",
    "P1": "Phase 2 reference 人工撰写页",
    "P2": "Phase 3 reference API 文档（自动生成，可延后）",
    "P3": "Phase 4 news / design-decisions / support",
}

STATUS_LABELS = {
    "pending": "翻译",
    "update-needed": "更新/复核",
}


def _setup_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


def write_text_file(base: Path, rel: str, text: str) -> Path:
    """在 base 内写入 rel 文本文件（utf-8、LF）；越界即拒绝。"""
    target = (base / rel).resolve()
    if not target.is_relative_to(base.resolve()):
        raise ValueError(f"拒绝越界写入: {rel!r}")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8", newline="\n")
    return target


def classify_priority(rel: str) -> str:
    top = rel.split("/")[0]
    if rel in ("_index.md", "overview.md", "installation.md"):
        return "P0"
    if top in ("getting-started", "programming-guides", "best-practices", "editions"):
        return "P0"
    if top == "reference":
        return "P2" if "/api-docs/" in rel else "P1"
    return "P3"


def find_diff_refs(rel: str) -> list[str]:
    """查找该文件在 tasks/diffs/ 下已有的 diff 摘要（相对仓库根路径）。"""
    refs: list[str] = []
    if not DIFFS_DIR.exists():
        return refs
    name = f"{rel.replace('/', '__')}.diff"
    for path in sorted(DIFFS_DIR.rglob(name)):
        refs.append(path.relative_to(ROOT).as_posix())
    return refs


def build_batches(paths: list[str]) -> list[list[str]]:
    return [paths[i:i + BATCH_SIZE] for i in range(0, len(paths), BATCH_SIZE)]


def render_task_line(rel: str, entry: dict) -> str:
    status = entry.get("status", "pending")
    label = STATUS_LABELS.get(status, status)
    parts = [f"- [ ] `{rel}` — {label}"]
    if status == "update-needed":
        refs = find_diff_refs(rel)
        if refs:
            parts.append(f"diff 摘要: {', '.join(refs)}")
        notes = entry.get("notes", "")
        if notes:
            parts.append(f"备注: {notes}")
    return "；".join(parts)


def generate(manifest: dict, date: str) -> Path:
    files: dict[str, dict] = manifest["files"]
    by_priority: dict[str, list[str]] = {"P0": [], "P1": [], "P2": [], "P3": []}
    for rel, entry in sorted(files.items()):
        if entry.get("status") in ("pending", "update-needed"):
            by_priority[classify_priority(rel)].append(rel)

    lines: list[str] = [
        f"# 翻译任务清单 {date}",
        "",
        f"- 上游 commit: `{manifest.get('last_synced_commit', '')}`",
        "- 任务来源: manifest.json（status ∈ pending / update-needed）",
        "- 领取方式: 认领一个批次，按 style-guide.md 的单文件 SOP 执行；",
        "  译文放 zh/ 同名路径，完成后跑 verify_structure.py 与 check_terms.py，",
        "  更新 manifest 条目（status=translated 等）并单独 commit。",
        "",
    ]
    for pri in ("P0", "P1", "P2", "P3"):
        paths = by_priority[pri]
        if not paths:
            continue
        batches = build_batches(paths)
        lines += [
            f"## {pri} {PRIORITY_LABELS[pri]}（{len(paths)} 文件 / {len(batches)} 批）",
            "",
        ]
        for no, batch in enumerate(batches, 1):
            lines.append(f"### 批次 {no}（{len(batch)} 文件）")
            lines.append("")
            for rel in batch:
                lines.append(render_task_line(rel, files[rel]))
            lines.append("")

    total = sum(len(v) for v in by_priority.values())
    if total == 0:
        lines += ["当前无待办任务。", ""]
    else:
        counts = "，".join(f"{pri}: {len(by_priority[pri])}" for pri in ("P0", "P1", "P2", "P3"))
        lines += [f"合计待办 {total}（{counts}）", ""]

    return write_text_file(TASKS_DIR, f"pending-{date}.md", "\n".join(lines))


def main() -> int:
    _setup_stdio()
    parser = argparse.ArgumentParser(description="生成翻译任务清单 tasks/pending-<date>.md")
    parser.add_argument("--manifest", default=str(MANIFEST_PATH), help="manifest 路径（默认 manifest.json）")
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    if not manifest_path.is_absolute():
        manifest_path = ROOT / manifest_path
    if not manifest_path.exists():
        print(f"错误：manifest 不存在: {manifest_path}（先运行 python tools/sync_upstream.py --init）")
        return 2

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    date = datetime.date.today().isoformat()
    out = generate(manifest, date)
    print(f"任务清单已生成: {out.relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
