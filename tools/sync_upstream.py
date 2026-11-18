#!/usr/bin/env python3
"""sync_upstream.py — 同步官方仓库到 upstream/ 快照并维护 manifest.json。

对应 docs/translation-plan.md 第四节「增量翻译核心机制（双锚点）」：
  1. git -C .upstream fetch origin；
  2. git diff --name-status 对比新旧 commit 的 content/ 得到 A/M/D/R 清单；
  3. 逐文件用 blob SHA 复核（兜底“改了又改回原样”的边界情况）；
  4. 更新 upstream/ 快照；状态判定 new / update / skip / removed / 改名沿用；
  5. includes/ 局部文件更新时联动标记引用页 update-needed(review)；
  6. 更新 manifest.json 的 last_synced_commit；输出 sync 报告；任务清单由
     tools/gen_tasks.py 依据 manifest 生成。

用法：
    python tools/sync_upstream.py            # 常规：增量同步（需已有 manifest）
    python tools/sync_upstream.py --init     # 首次：以 origin/main 为基准生成 manifest

依赖：Python >= 3.10（仅标准库）、git。所有文件 IO 显式 utf-8，输出 LF。
"""
from __future__ import annotations

import argparse
import datetime
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UPSTREAM_DIR = ROOT / ".upstream"
SNAPSHOT_DIR = ROOT / "upstream" / "content"
ZH_DIR = ROOT / "zh"
ARCHIVE_DIR = ZH_DIR / "_archived"
MANIFEST_PATH = ROOT / "manifest.json"
REPORT_DIR = ROOT / "tasks"
DIFF_DIR = REPORT_DIR / "diffs"

UPSTREAM_URL = "https://github.com/protocolbuffers/protocolbuffers.github.io"
MANIFEST_SCHEMA_VERSION = 1
DIFF_MAX_LINES = 500


def _setup_stdio() -> None:
    """Windows 控制台默认代码页可能不是 UTF-8，统一按 UTF-8 输出。"""
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


def resolve_rel(rel: str, base: Path) -> Path:
    """校验并构造 base 内的路径，越界即拒绝（git 输出等外部数据的入口校验）。"""
    target = (base / rel).resolve()
    if not target.is_relative_to(base.resolve()):
        raise ValueError(f"路径越界: {rel!r}")
    return target


def write_text_file(base: Path, rel: str, text: str) -> Path:
    """在 base 内写入 rel 文本文件（utf-8、LF）；越界即拒绝。"""
    target = (base / rel).resolve()
    if not target.is_relative_to(base.resolve()):
        raise ValueError(f"拒绝越界写入: {rel!r}")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8", newline="\n")
    return target


def write_bin_file(base: Path, rel: str, data: bytes) -> Path:
    """在 base 内写入 rel 二进制文件；越界即拒绝。"""
    target = (base / rel).resolve()
    if not target.is_relative_to(base.resolve()):
        raise ValueError(f"拒绝越界写入: {rel!r}")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    return target


def remove_file(base: Path, rel: str) -> bool:
    """删除 base 内的 rel 文件；越界即拒绝。返回是否实际删除。"""
    target = (base / rel).resolve()
    if not target.is_relative_to(base.resolve()):
        raise ValueError(f"拒绝越界删除: {rel!r}")
    if target.exists():
        target.unlink()
        return True
    return False


class GitError(RuntimeError):
    """git 命令执行失败。"""


def run_git(args: list[str], cwd: Path) -> subprocess.CompletedProcess[bytes]:
    proc = subprocess.run(["git", *args], cwd=str(cwd), capture_output=True)
    if proc.returncode != 0:
        err = proc.stderr.decode("utf-8", errors="replace").strip()
        raise GitError(f"git {' '.join(args)} 失败: {err}")
    return proc


def git_text(args: list[str], cwd: Path) -> str:
    return run_git(args, cwd).stdout.decode("utf-8", errors="replace")


def upstream_head() -> str:
    return run_git(["rev-parse", "origin/main"], UPSTREAM_DIR).stdout.decode("ascii").strip()


def git_ls_tree(ref: str) -> dict[str, str]:
    """返回指定 commit 的 content/ 全部文件 {相对路径: blob SHA}。"""
    out = git_text(["ls-tree", "-r", ref, "--", "content/"], UPSTREAM_DIR)
    tree: dict[str, str] = {}
    for line in out.splitlines():
        meta, _, path = line.partition("\t")
        _mode, kind, sha = meta.split()
        if kind != "blob":
            continue
        tree[path.removeprefix("content/")] = sha
    return tree


def git_name_status(last: str, new: str) -> list[tuple[str, str, str | None]]:
    """git diff --name-status 对比两个 commit，得到 content/ 的 A/M/D/R 清单。"""
    out = git_text(["diff", "--name-status", last, new, "--", "content/"], UPSTREAM_DIR)
    changes: list[tuple[str, str, str | None]] = []
    for line in out.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        code = parts[0]
        if code[0] in "RC" and len(parts) == 3:  # R100/C75：旧路径 新路径
            changes.append((code[0], parts[1], parts[2]))
        else:
            changes.append((code, parts[1], None))
    return changes


def cat_blob(spec: str) -> bytes:
    """读取 .upstream 中某个 blob（如 origin/main:content/overview.md）。"""
    return run_git(["cat-file", "blob", spec], UPSTREAM_DIR).stdout


def diff_blobs(old_sha: str, new_sha: str) -> str:
    return git_text(["diff", old_sha, new_sha, "--"], UPSTREAM_DIR)


def hash_objects(paths: list[Path]) -> list[str]:
    """批量计算 git blob SHA（git hash-object --stdin-paths）。"""
    if not paths:
        return []
    stdin_data = "".join(f"{p.as_posix()}\n" for p in paths)
    proc = subprocess.run(
        ["git", "hash-object", "--stdin-paths"],
        cwd=str(ROOT),
        input=stdin_data.encode("utf-8"),
        capture_output=True,
        check=True,
    )
    return proc.stdout.decode("ascii").split()


# ---------------------------------------------------------------- manifest


def load_manifest() -> dict:
    if not MANIFEST_PATH.exists():
        sys.exit(
            "错误：manifest.json 不存在。首次使用请先运行：\n"
            "    python tools/sync_upstream.py --init"
        )
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def save_manifest(manifest: dict) -> None:
    text = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    write_text_file(ROOT, "manifest.json", text)


# ---------------------------------------------------------------- skip 分类


def classify_skip(rel: str) -> tuple[str, str]:
    """站点功能页与列表页分类（translation-plan 第六节 skip 清单）。

    返回 (status, note)。status ∈ {"skip", "skip-partial", "pending"}。
    """
    if rel in ("navbar.md", "forum-link.md", "search.md"):
        return "skip", "站点功能页：导航/论坛链接/搜索占位页，无正文"
    if rel.startswith("includes/"):
        return "skip", "includes/ 局部引用片段（纯技术内容）"
    if rel.endswith("_index.md"):
        if rel == "_index.md":
            # 根 _index.md 是站点首页，含完整正文，按正文页全量翻译。
            return "pending", "站点首页，正文页全量翻译"
        if rel.startswith("reference/kotlin/api-docs/protobuf-kotlin/com.google.protobuf.kotlin/"):
            # Dokka 自动生成的 API 类文档页，非列表页；Phase 3 再决定是否翻译。
            return "pending", "Kotlin api-docs 自动生成页（Phase 3 范围）"
        return "skip-partial", "列表页：仅译 frontmatter 标题/描述与导语"
    return "pending", ""


# ---------------------------------------------------------------- 快照与译文归档


def snapshot_path(rel: str) -> Path:
    """由外部输入的相对路径构造快照内目标路径（校验 + 就地构造）。"""
    return resolve_rel(rel, SNAPSHOT_DIR)


def zh_path(rel: str) -> Path:
    return resolve_rel(rel, ZH_DIR)


def write_snapshot(rel: str, data: bytes) -> None:
    write_bin_file(SNAPSHOT_DIR, rel, data)


def remove_snapshot(rel: str) -> None:
    remove_file(SNAPSHOT_DIR, rel)


def save_diff(rel: str, old_sha: str, new_sha: str, date: str) -> Path | None:
    """保存两 blob 之间的 diff 摘要文件，供译者只重译变更段落。"""
    try:
        text = diff_blobs(old_sha, new_sha)
    except GitError:
        return None
    if not text.strip():
        return None
    lines = text.splitlines()
    if len(lines) > DIFF_MAX_LINES:
        lines = lines[:DIFF_MAX_LINES] + [
            f"（截断；完整 diff 可用 git diff {old_sha[:10]} {new_sha[:10]} 查看）"
        ]
    out_rel = f"{date}/{rel.replace('/', '__')}.diff"
    return write_text_file(DIFF_DIR, out_rel, "\n".join(lines) + "\n")


def archive_translation(rel: str) -> str | None:
    """上游删除文件时，把已有译文移入 zh/_archived/。"""
    src = zh_path(rel)
    if not src.exists():
        return None
    data = src.read_bytes()
    write_bin_file(ARCHIVE_DIR, rel, data)
    remove_file(ZH_DIR, rel)
    return f"zh/_archived/{rel}"


def move_translation(old_rel: str, new_rel: str) -> str | None:
    """上游改名/移动时，旧译文沿用到新路径。"""
    src = zh_path(old_rel)
    if not src.exists():
        return None
    data = src.read_bytes()
    write_bin_file(ZH_DIR, new_rel, data)
    remove_file(ZH_DIR, old_rel)
    return new_rel


# ---------------------------------------------------------------- includes 联动


def link_includes_changes(changed_includes: list[str], manifest: dict, actions: list[dict]) -> None:
    """includes/ 下 md 局部文件更新 → 标记所有引用它的已译页面 update-needed(review)。

    引用识别：在快照 md 正文中查找 “includes/<文件名>” 字样。
    注：当前上游 includes/ 仅有 2 个 CSS 文件、无 md 局部文件，本机制为前瞻实现。
    """
    if not changed_includes:
        return
    targets = {f"includes/{Path(p).name}" for p in changed_includes}
    pages: dict[str, str] = {}
    for rel in manifest["files"]:
        if rel.startswith("includes/") or not rel.endswith(".md"):
            continue
        path = snapshot_path(rel)
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for target in sorted(targets):
            if target in text:
                pages.setdefault(rel, target)
    for rel, target in sorted(pages.items()):
        entry = manifest["files"].get(rel)
        if entry is None or entry.get("status") not in ("translated", "update-needed"):
            continue
        entry["status"] = "update-needed"
        note = f"includes 联动：引用了 {target}，上游局部文件已更新，核对后可降级"
        entry["notes"] = note
        actions.append({"action": "update", "path": rel, "note": note + "（review）"})


# ---------------------------------------------------------------- 增量同步


def do_sync() -> int:
    manifest = load_manifest()
    last = manifest.get("last_synced_commit")
    if not last:
        sys.exit("错误：manifest.json 缺少 last_synced_commit，请运行 --init 重新生成。")

    print(f"fetch origin ...（上游 {UPSTREAM_URL}）")
    try:
        run_git(["fetch", "origin"], UPSTREAM_DIR)
    except GitError as exc:
        print(str(exc))
        print(
            "提示：网络失败时可走代理后重试，例如在 .upstream 内执行：\n"
            "    git -c http.proxy=http://127.0.0.1:10808 fetch origin\n"
            "或为本会话导出 http_proxy / https_proxy 环境变量。"
        )
        return 2

    new_head = upstream_head()
    today = datetime.date.today().isoformat()
    print(f"commit 对比: {last[:10]} 对比 {new_head[:10]}")

    changes = git_name_status(last, new_head)
    tree = git_ls_tree(new_head)
    files = manifest["files"]
    actions: list[dict] = []
    changed_includes: list[str] = []

    counts = {"new": 0, "update": 0, "skip": 0, "removed": 0, "renamed": 0, "refresh": 0}

    for code, path, extra in changes:
        rel = path.removeprefix("content/")
        is_md = rel.endswith(".md")
        try:
            resolve_rel(rel, SNAPSHOT_DIR)
        except ValueError as exc:
            print(f"跳过可疑路径: {exc}")
            continue

        if code == "A":
            data = cat_blob(f"origin/main:content/{rel}")
            write_snapshot(rel, data)
            if is_md:
                status, note = classify_skip(rel)
                files[rel] = {
                    "status": status,
                    "upstream_sha": tree[rel],
                    "upstream_commit": new_head,
                    "translated_at": None,
                    "translator": None,
                }
                if note:
                    files[rel]["notes"] = note
                if status in ("skip", "skip-partial"):
                    counts["skip"] += 1
                    actions.append({"action": "skip", "path": rel, "note": "新文件属站点功能页/列表页，无需翻译"})
                else:
                    counts["new"] += 1
                    actions.append({"action": "new", "path": rel, "note": "新文件，全量翻译"})
                if rel.startswith("includes/"):
                    changed_includes.append(rel)
            else:
                counts["refresh"] += 1
                actions.append({"action": "refresh", "path": rel, "note": "非 md 资源更新入快照"})

        elif code == "M":
            data = cat_blob(f"origin/main:content/{rel}")
            write_snapshot(rel, data)
            entry = files.get(rel)
            if entry is None:
                if is_md:
                    status, note = classify_skip(rel)
                    files[rel] = {
                        "status": status,
                        "upstream_sha": tree.get(rel, ""),
                        "upstream_commit": new_head,
                        "translated_at": None,
                        "translator": None,
                    }
                    if note:
                        files[rel]["notes"] = note
                    actions.append({"action": "new", "path": rel, "note": "manifest 缺失条目，已补录"})
                else:
                    counts["refresh"] += 1
                    actions.append({"action": "refresh", "path": rel, "note": "非 md 资源更新入快照"})
                continue
            new_sha = tree.get(rel, "")
            if entry.get("upstream_sha") == new_sha:
                # blob SHA 复核：内容与上次一致（改了又改回），无需任务
                counts["skip"] += 1
                actions.append({"action": "skip", "path": rel, "note": "blob SHA 复核后与上次一致（改回原样）"})
                continue
            old_sha = entry.get("upstream_sha", "")
            entry["upstream_sha"] = new_sha
            entry["upstream_commit"] = new_head
            if not is_md:
                counts["refresh"] += 1
                actions.append({"action": "refresh", "path": rel, "note": "非 md 资源更新入快照"})
                continue
            if entry["status"] in ("translated", "update-needed"):
                entry["status"] = "update-needed"
                diff_ref = save_diff(rel, old_sha, new_sha, today)
                note = "上游变更，按 diff 只重译变更段落" + (
                    f"，diff 摘要见 {diff_ref.relative_to(ROOT).as_posix()}" if diff_ref else ""
                )
                entry["notes"] = note
                counts["update"] += 1
                actions.append({"action": "update", "path": rel, "note": note})
            elif entry["status"] in ("skip", "skip-partial"):
                counts["skip"] += 1
                entry["notes"] = "上游变更，站点功能页/列表页无需翻译任务"
                actions.append({"action": "skip", "path": rel, "note": "skip 页上游变更，仅更新快照"})
            else:  # pending：尚未翻译，仅刷新快照
                counts["refresh"] += 1
                entry["notes"] = "上游变更入快照（原状态 pending）"
                actions.append({"action": "refresh", "path": rel, "note": "pending 页上游变更，仅刷新快照"})

        elif code == "D":
            remove_snapshot(rel)
            if is_md and rel in files:
                archived = archive_translation(rel)
                files[rel]["status"] = "removed"
                files[rel]["removed_at"] = today
                files[rel]["notes"] = (
                    f"上游删除，译文归档至 {archived}" if archived else "上游删除，无对应译文"
                )
                counts["removed"] += 1
                actions.append({
                    "action": "removed",
                    "path": rel,
                    "note": "上游删除" + (f"，译文已归档 {archived}" if archived else ""),
                })
            else:
                counts["refresh"] += 1
                actions.append({"action": "refresh", "path": rel, "note": "资源被上游删除，已移出快照"})

        elif code == "R" and extra:
            new_rel = extra.removeprefix("content/")
            old_rel = path.removeprefix("content/")
            resolve_rel(old_rel, SNAPSHOT_DIR)
            resolve_rel(new_rel, SNAPSHOT_DIR)
            data = cat_blob(f"origin/main:content/{new_rel}")
            remove_snapshot(old_rel)
            write_snapshot(new_rel, data)
            moved = None
            if is_md:
                entry = files.pop(old_rel, None)
                if entry is None:
                    entry = {"status": "pending", "translated_at": None, "translator": None}
                status_cls, _note = classify_skip(new_rel)
                moved = move_translation(old_rel, new_rel)
                entry["upstream_sha"] = tree[new_rel]
                entry["upstream_commit"] = new_head
                entry["renamed_from"] = old_rel
                if status_cls.startswith("skip"):
                    entry["status"] = status_cls
                elif entry.get("status") == "translated":
                    entry["status"] = "update-needed"
                    entry["notes"] = f"上游改名 {old_rel} 为 {new_rel}，译文沿用，请复核"
                files[new_rel] = entry
                counts["renamed"] += 1
                actions.append({
                    "action": "renamed",
                    "path": new_rel,
                    "note": f"上游改名 {old_rel} 为 {new_rel}"
                    + (f"，旧译文沿用至 zh/{new_rel}" if moved else "，无旧译文"),
                })
            else:
                counts["refresh"] += 1
                actions.append({"action": "refresh", "path": new_rel, "note": f"资源改名 {old_rel} 为 {new_rel}"})

        else:  # T（类型变更）等
            data = cat_blob(f"origin/main:content/{rel}")
            write_snapshot(rel, data)
            counts["refresh"] += 1
            actions.append({"action": "refresh", "path": rel, "note": f"类型变更 {code}，快照已刷新"})

    link_includes_changes(changed_includes, manifest, actions)

    manifest["last_synced_commit"] = new_head
    manifest["last_synced_at"] = today
    save_manifest(manifest)

    # 快照完整性复核：upstream/ 内全部文件 hash-object 应与 origin/main 一致
    verified, mismatches = verify_snapshot(tree)
    if mismatches:
        print("警告：快照与 origin/main blob SHA 不一致（应人工检查）：")
        for rel in mismatches[:20]:
            print(f"  - {rel}")

    write_report(today, last, new_head, counts, actions, verified, len(mismatches))
    print(
        f"完成：{counts['new']} new / {counts['update']} update / {counts['skip']} skip / "
        f"{counts['removed']} removed / {counts['renamed']} renamed / {counts['refresh']} refresh；"
        f"快照校验 {verified} 文件通过，{len(mismatches)} 不一致"
    )
    print("下一步：python tools/gen_tasks.py 生成任务清单。")
    return 0


def verify_snapshot(tree: dict[str, str]) -> tuple[int, list[str]]:
    """对 upstream/ 快照逐文件 hash-object 复核，与 origin/main blob SHA 比对。"""
    existing: dict[str, Path] = {}
    for rel in tree:
        try:
            path = snapshot_path(rel)
        except ValueError:
            continue
        if path.exists():
            existing[rel] = path
    shas = hash_objects(list(existing.values()))
    mismatches = [rel for rel, sha in zip(existing.keys(), shas) if sha != tree[rel]]
    missing = [rel for rel in tree if rel not in existing]
    mismatches.extend(f"{rel}（快照缺失）" for rel in missing)
    return len(existing), mismatches


def write_report(today: str, last: str, new_head: str, counts: dict, actions: list[dict], verified: int, mismatch: int) -> Path:
    out_rel = f"sync-{today}-{new_head[:8]}.md"
    lines: list[str] = [
        f"# Upstream Sync 报告 {today}",
        "",
        f"- 上游仓库：{UPSTREAM_URL}",
        f"- commit 对比：{last} 对比 {new_head}",
        f"- 结果：{counts['new']} new / {counts['update']} update / {counts['skip']} skip / "
        f"{counts['removed']} removed / {counts['renamed']} renamed / {counts['refresh']} refresh",
        f"- 快照完整性复核：{verified} 个文件 hash-object 校验通过，{mismatch} 个不一致",
        "",
        "## 明细",
        "",
    ]
    if not actions:
        lines.append("本次无任何上游变更。")
    else:
        for item in actions:
            lines.append(f"- **{item['action']}** `{item['path']}` — {item['note']}")
    lines += [
        "",
        "## 后续步骤",
        "",
        "1. 运行 python tools/gen_tasks.py 生成或更新任务清单；",
        "2. update 条目按 diff 摘要（tasks/diffs/ 下同名 .diff 文件）只重译变更段落；",
        "3. sync 结果以本文件留档，独立于翻译 commit。",
        "",
    ]
    out = write_text_file(REPORT_DIR, out_rel, "\n".join(lines))
    print(f"sync 报告：{out.relative_to(ROOT).as_posix()}")
    return out


# ---------------------------------------------------------------- 首次初始化


def do_init() -> int:
    if not UPSTREAM_DIR.exists():
        sys.exit(
            "错误：.upstream/ 不存在，请先 clone 官方仓库：\n"
            "    git clone https://github.com/protocolbuffers/protocolbuffers.github.io .upstream"
        )
    head = upstream_head()
    tree = git_ls_tree(head)
    today = datetime.date.today().isoformat()

    files: dict[str, dict] = {}
    for rel, sha in sorted(tree.items()):
        if not rel.endswith(".md"):
            continue
        status, note = classify_skip(rel)
        entry = {
            "status": status,
            "upstream_sha": sha,
            "upstream_commit": head,
            "translated_at": None,
            "translator": None,
        }
        if note:
            entry["notes"] = note
        files[rel] = entry

    manifest = {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "upstream_url": UPSTREAM_URL,
        "last_synced_commit": head,
        "last_synced_at": today,
        "files": files,
    }
    save_manifest(manifest)

    verified, mismatches = verify_snapshot(tree)
    print(f"manifest 生成：{len(files)} 个 md 文件（origin/main = {head[:10]}）")
    by_status: dict[str, int] = {}
    for entry in files.values():
        by_status[entry["status"]] = by_status.get(entry["status"], 0) + 1
    for status, n in sorted(by_status.items()):
        print(f"  {status}: {n}")
    print(f"快照完整性复核：{verified} 个文件通过，{len(mismatches)} 不一致")
    if mismatches:
        for rel in mismatches[:20]:
            print(f"  不一致: {rel}")
        print("错误：快照与 origin/main 不一致，请重新拷贝 .upstream/content 到 upstream/content 后重试。")
        return 4
    print("下一步：python tools/gen_tasks.py 生成任务清单。")
    return 0


def main() -> int:
    _setup_stdio()
    parser = argparse.ArgumentParser(description="同步官方仓库到 upstream/ 快照并维护 manifest.json")
    parser.add_argument("--init", action="store_true", help="首次运行：以 origin/main 为基准生成 manifest")
    args = parser.parse_args()
    try:
        return do_init() if args.init else do_sync()
    except GitError as exc:
        print(f"错误：{exc}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
