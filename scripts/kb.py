#!/usr/bin/env python3
"""
kb.py — UI 审美知识库 CLI（零依赖，仅标准库）

用法：
    python scripts/kb.py list [--type P|M|A|J] [--status active|stale|archived]
    python scripts/kb.py show <ID>
    python scripts/kb.py add <卡片.md>              # 校验后入库
    python scripts/kb.py use <ID>                   # 记一次复用（提升复用率指标）
    python scripts/kb.py promote <ID>               # 晋升一级（需 evidence>=3）
    python scripts/kb.py decay                      # 按 last_used 批量衰减
    python scripts/kb.py check                      # 健康检查
    python scripts/kb.py stats                      # 指标表
    python scripts/kb.py index                      # 重建 INDEX.md
"""
import argparse
import datetime as dt
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KB = ROOT / "knowledge"
TYPES = {"P": "params", "M": "patterns", "A": "anti-patterns", "J": "judgments"}
REQUIRED = ["id", "type", "title", "scope", "platform", "confidence",
            "evidence", "sources", "created", "last_used", "status", "applies_to"]
LOG = KB / "EVOLUTION.log"
TODAY = dt.date.today()


def parse_card(path: Path):
    text = path.read_text(encoding="utf-8")
    if not text.lstrip().startswith("---"):
        return {}, text
    m = re.match(r"^\s*---\s*\n(.*?)\n---\s*\n?(.*)$", text, re.S)
    if not m:
        return {}, text
    yml, body = m.group(1), m.group(2)
    meta, cur = {}, None
    for line in yml.splitlines():
        if not line.strip():
            continue
        if line.lstrip().startswith("- "):
            if cur:
                meta.setdefault(cur, []).append(line.strip()[2:].strip().strip('"').strip("'"))
            continue
        mm = re.match(r"^([A-Za-z_]+):\s*(.*)$", line)
        if not mm:
            continue
        k, v = mm.group(1), mm.group(2).strip()
        if not v:
            meta[k] = []
            cur = k
            continue
        cur = None
        v = v.strip('"').strip("'")
        if v.startswith("[") and v.endswith("]"):
            meta[k] = [x.strip().strip('"').strip("'") for x in v[1:-1].split(",") if x.strip()]
        else:
            meta[k] = v
    return meta, body


def all_cards():
    out = []
    for t, sub in TYPES.items():
        d = KB / sub
        if not d.exists():
            continue
        for p in sorted(d.glob("*.md")):
            meta, body = parse_card(p)
            out.append({"path": p, "meta": meta, "body": body})
    return out


def as_int(v, default=0):
    try:
        return int(str(v).strip())
    except Exception:
        return default


def as_date(v):
    try:
        return dt.date.fromisoformat(str(v).strip()[:10])
    except Exception:
        return None


def validate(meta):
    errs = []
    for k in REQUIRED:
        if k not in meta or meta[k] in ("", [], None):
            errs.append(f"缺少必填字段：{k}")
    t = str(meta.get("type", "")).upper()
    if t and t not in TYPES:
        errs.append(f"type 必须是 P/M/A/J，当前 {t}")
    cid = str(meta.get("id", ""))
    if cid and t and not cid.startswith(t + "-"):
        errs.append(f"id 必须以 {t}- 开头，当前 {cid}")
    conf, ev = as_int(meta.get("confidence")), as_int(meta.get("evidence"))
    if conf and not 1 <= conf <= 5:
        errs.append("confidence 必须在 1-5")
    if conf >= 3 and ev < 3:
        errs.append(f"自相矛盾：confidence {conf} 但 evidence 只有 {ev}（≥3 才允许 ≥3）")
    title = str(meta.get("title", ""))
    if 0 < len(title) < 4:
        errs.append("title 太短，无法作为规则阅读")
    if not as_date(meta.get("created")):
        errs.append("created 必须是 YYYY-MM-DD")
    return errs


def find(cid):
    for c in all_cards():
        if str(c["meta"].get("id", "")).upper() == cid.upper():
            return c
    return None


def set_fields(path: Path, updates: dict):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^(\s*---\s*\n)(.*?)(\n---\s*\n?)(.*)$", text, re.S)
    if not m:
        return False
    head, yml, fence, body = m.groups()
    lines = yml.splitlines()
    for k, v in updates.items():
        pat = re.compile(rf"^\s*{k}\s*:")
        replaced = False
        for i, line in enumerate(lines):
            if pat.match(line):
                lines[i] = f"{k}: {v}"
                replaced = True
                break
        if not replaced:
            lines.append(f"{k}: {v}")
    path.write_text(head + "\n".join(lines) + fence + body, encoding="utf-8")
    return True


def log(line):
    KB.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"{TODAY} | {line}\n")


def cmd_list(args):
    cards = all_cards()
    if args.type:
        cards = [c for c in cards if str(c["meta"].get("type", "")).upper() == args.type.upper()]
    if args.status:
        cards = [c for c in cards if c["meta"].get("status") == args.status]
    if not cards:
        print("（无匹配卡片）")
        return 0
    print(f"{'ID':10} {'类型':4} {'置信':4} {'证据':4} {'用':3} {'状态':8} 标题")
    print("-" * 78)
    for c in cards:
        m = c["meta"]
        print(f"{m.get('id',''):10} {m.get('type',''):4} {str(m.get('confidence','')):4} "
              f"{str(m.get('evidence','')):4} {str(m.get('use_count',0)):3} "
              f"{str(m.get('status','')):8} {m.get('title','')}")
    print(f"\n共 {len(cards)} 张")
    return 0


def cmd_show(args):
    c = find(args.id)
    if not c:
        print(f"找不到 {args.id}")
        return 1
    print(c["path"].read_text(encoding="utf-8"))
    return 0


def cmd_add(args):
    p = Path(args.file)
    if not p.exists():
        print(f"文件不存在：{p}")
        return 1
    meta, _ = parse_card(p)
    errs = validate(meta)
    existing = {str(c["meta"].get("id", "")).upper() for c in all_cards()}
    if str(meta.get("id", "")).upper() in existing:
        errs.append(f"id {meta.get('id')} 已存在（要修改请直接编辑原文件）")
    for c in all_cards():
        if str(c["meta"].get("title", "")).strip() == str(meta.get("title", "")).strip():
            errs.append(f"与 {c['meta'].get('id')} 标题重复，考虑合并")
            break
    if errs:
        print("入库失败：")
        for e in errs:
            print("  -", e)
        return 1
    t = str(meta["type"]).upper()
    dest = KB / TYPES[t] / f"{meta['id']}.md"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(p.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"已入库：{dest.relative_to(ROOT)}")
    log(f"ADD     | {meta['id']} {meta['title']} | conf {meta['confidence']} ev {meta['evidence']}")
    return 0


def cmd_use(args):
    c = find(args.id)
    if not c:
        print(f"找不到 {args.id}")
        return 1
    n = as_int(c["meta"].get("use_count", 0)) + 1
    set_fields(c["path"], {"use_count": n, "last_used": TODAY.isoformat()})
    print(f"{args.id} 复用计数 → {n}")
    return 0


def cmd_promote(args):
    c = find(args.id)
    if not c:
        print(f"找不到 {args.id}")
        return 1
    m = c["meta"]
    conf, ev = as_int(m.get("confidence")), as_int(m.get("evidence"))
    if m.get("status") != "active":
        print(f"拒绝：状态为 {m.get('status')}，需先恢复 active")
        return 1
    if ev < 3:
        print(f"拒绝：evidence 只有 {ev}，晋升要求 ≥3（先复现）")
        return 1
    if conf >= 5:
        print("已是公理（5），不可自动晋升")
        return 1
    new = conf + 1
    set_fields(c["path"], {"confidence": new, "last_used": TODAY.isoformat()})
    log(f"PROMOTE | {args.id} {m.get('title')} | {conf}→{new}")
    print(f"{args.id} 置信度 {conf} → {new}")
    if new == 4:
        print("\n下一步（不可跳过）：")
        print("  1) 跑 evals/cases.yaml 回归，均分不降 >2、无单例降 >5")
        print("  2) 写回 website-ui-designer 对应规范文件")
        print("  3) 在 EVOLUTION.log 记一行 REGRESS 结果")
    return 0


def cmd_decay(args):
    changed = 0
    for c in all_cards():
        m = c["meta"]
        if m.get("status") != "active":
            continue
        lu = as_date(m.get("last_used"))
        if not lu:
            continue
        days = (TODAY - lu).days
        conf = as_int(m.get("confidence"))
        if days > 180:
            set_fields(c["path"], {"status": "stale"})
            log(f"DECAY   | {m.get('id')} {m.get('title')} | active→stale（{days} 天未用）")
            print(f"{m.get('id')} → stale（{days} 天未用）")
            changed += 1
        elif days > 90 and conf > 1:
            set_fields(c["path"], {"confidence": conf - 1})
            log(f"DECAY   | {m.get('id')} {m.get('title')} | {conf}→{conf-1}（{days} 天未用）")
            print(f"{m.get('id')} 置信度 {conf} → {conf-1}（{days} 天未用）")
            changed += 1
    print(f"\n衰减完成，变更 {changed} 张")
    return 0


def cmd_check(args):
    cards = all_cards()
    print(f"知识库：{len(cards)} 张卡\n")
    bad = 0
    for c in cards:
        errs = validate(c["meta"])
        if errs:
            bad += 1
            print(f"[格式问题] {c['meta'].get('id', c['path'].name)}")
            for e in errs:
                print("   -", e)
    stale, dup = [], []
    titles = {}
    for c in cards:
        m = c["meta"]
        lu = as_date(m.get("last_used"))
        if lu and (TODAY - lu).days > 90:
            stale.append((m.get("id"), (TODAY - lu).days))
        t = str(m.get("title", "")).strip()
        if t:
            titles.setdefault(t, []).append(m.get("id"))
    for t, ids in titles.items():
        if len(ids) > 1:
            dup.append((t, ids))
    print("\n待衰减（>90 天未用）：")
    print("  " + ("、".join(f"{i}({d}天)" for i, d in stale) if stale else "无"))
    print("疑似重复标题：")
    print("  " + ("；".join(f"{t} → {ids}" for t, ids in dup) if dup else "无"))
    low = [c["meta"].get("id") for c in cards
           if as_int(c["meta"].get("confidence")) >= 4 and as_int(c["meta"].get("evidence")) < 3]
    print("高置信但低证据（应校验）：")
    print("  " + ("、".join(low) if low else "无"))
    print(f"\n结论：{bad} 张格式问题，{len(stale)} 张待衰减，{len(dup)} 组重复")
    return 1 if bad else 0


def cmd_stats(args):
    cards = all_cards()
    if not cards:
        print("知识库为空")
        return 0
    total = len(cards)
    by_type = {t: 0 for t in TYPES}
    conf_d = {i: 0 for i in range(1, 6)}
    used = 0
    for c in cards:
        m = c["meta"]
        by_type[str(m.get("type", "")).upper()] = by_type.get(str(m.get("type", "")).upper(), 0) + 1
        conf_d[as_int(m.get("confidence"), 1)] += 1
        if as_int(m.get("use_count", 0)) > 0:
            used += 1
    stale = sum(1 for c in cards if c["meta"].get("status") in ("stale", "archived"))
    hi = sum(v for k, v in conf_d.items() if k >= 4)

    def pct(a, b):
        return f"{(a / b * 100):.0f}%" if b else "—"

    print("知识库指标")
    print("-" * 40)
    print(f"总卡数            {total}")
    print("按类型            " + " / ".join(f"{k}:{v}" for k, v in by_type.items() if v))
    print("置信度分布        " + " / ".join(f"{k}级:{v}" for k, v in conf_d.items() if v))
    print(f"高置信(≥4)占比    {pct(hi, total)}   （健康 20-35%）")
    print(f"复用率            {pct(used, total)}   （健康 ≥50%）")
    print(f"衰减/归档占比     {pct(stale, total)}   （健康 5-15%）")
    return 0


def cmd_index(args):
    cards = all_cards()
    lines = ["# 知识索引", "",
             f"> 自动生成于 {TODAY}，共 {len(cards)} 张卡。不要手改。", ""]
    for t in ["P", "M", "A", "J"]:
        sub = [c for c in cards if str(c["meta"].get("type", "")).upper() == t]
        if not sub:
            continue
        name = {"P": "参数卡", "M": "手法卡", "A": "反例卡", "J": "判断卡"}[t]
        lines.append(f"## {t} · {name}（{len(sub)}）")
        lines.append("")
        lines.append("| ID | 标题 | 置信 | 复用 | 状态 | 适用 |")
        lines.append("|---|---|---|---|---|---|")
        for c in sub:
            m = c["meta"]
            lines.append(f"| {m.get('id')} | {m.get('title')} | {m.get('confidence')} | "
                         f"{m.get('use_count', 0)} | {m.get('status')} | {m.get('applies_to')} |")
        lines.append("")
    (KB / "INDEX.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"已重建 knowledge/INDEX.md（{len(cards)} 张）")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="UI 审美知识库 CLI")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("list"); p.add_argument("--type"); p.add_argument("--status"); p.set_defaults(fn=cmd_list)
    p = sub.add_parser("show"); p.add_argument("id"); p.set_defaults(fn=cmd_show)
    p = sub.add_parser("add"); p.add_argument("file"); p.set_defaults(fn=cmd_add)
    p = sub.add_parser("use"); p.add_argument("id"); p.set_defaults(fn=cmd_use)
    p = sub.add_parser("promote"); p.add_argument("id"); p.set_defaults(fn=cmd_promote)
    p = sub.add_parser("decay"); p.set_defaults(fn=cmd_decay)
    p = sub.add_parser("check"); p.set_defaults(fn=cmd_check)
    p = sub.add_parser("stats"); p.set_defaults(fn=cmd_stats)
    p = sub.add_parser("index"); p.set_defaults(fn=cmd_index)

    a = ap.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
