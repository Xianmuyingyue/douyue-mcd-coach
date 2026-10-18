#!/usr/bin/env python3
"""
daily_tracker.py — 每日卡路里 / 板烧累计（WorkBuddy 持久化）
----------------------------------------------------------
把每天吃的每一餐，按「板烧」为单位记录并累计。

- 存储位置：~/.workbuddy/douyue_mcd_coach/daily.json
  （在 WorkBuddy 目录下、不在公开仓库内，保护隐私）
- 1 板烧 = 400 kcal 锚定（与 references/unit.md 一致）
- 默认每日目标：3.3 板烧（≈1300 kcal，对应 300–500 合理缺口）

用法：
    python scripts/daily_tracker.py add --label "板烧经典餐" --kcal 732
    python scripts/daily_tracker.py add --label "黄焖鸡" --bansha 1.31 --source non-mcd
    python scripts/daily_tracker.py show            # 今日汇总
    python scripts/daily_tracker.py show --date 2026-10-18

仅依赖 Python 标准库。
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime

STORE_DIR = os.path.expanduser("~/.workbuddy/douyue_mcd_coach")
STORE = os.path.join(STORE_DIR, "daily.json")
UNIT = 400.0            # 1 板烧 ≈ 400 kcal
TARGET_BANSHA = 3.3     # 每日目标（≈1300 kcal）


def _today() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def _load() -> dict:
    if os.path.exists(STORE):
        try:
            with open(STORE, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def _save(d: dict) -> None:
    os.makedirs(STORE_DIR, exist_ok=True)
    with open(STORE, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)


def add_entry(label: str, kcal: float | None = None, bansha: float | None = None,
              source: str = "mcd", date: str | None = None) -> dict:
    """记录一餐，返回当日汇总。kcal / bansha 二选一。"""
    date = date or _today()
    if kcal is None and bansha is None:
        raise ValueError("需提供 kcal 或 bansha 之一")
    if kcal is None:
        kcal = bansha * UNIT
    if bansha is None:
        bansha = kcal / UNIT
    d = _load()
    day = d.setdefault(date, {"entries": [], "target_bansha": TARGET_BANSHA})
    day["entries"].append({
        "time": datetime.now().strftime("%H:%M"),
        "label": label,
        "kcal": round(float(kcal), 1),
        "bansha": round(float(bansha), 2),
        "source": source,
    })
    _save(d)
    return summary(date)


def summary(date: str | None = None) -> dict:
    """返回某日汇总：条目、总 kcal、总板烧、目标、剩余。"""
    date = date or _today()
    d = _load()
    day = d.get(date, {"entries": [], "target_bansha": TARGET_BANSHA})
    entries = day.get("entries", [])
    tot_kcal = round(sum(e["kcal"] for e in entries), 1)
    tot_ban = round(sum(e["bansha"] for e in entries), 2)
    target = day.get("target_bansha", TARGET_BANSHA)
    return {
        "date": date,
        "entries": entries,
        "total_kcal": tot_kcal,
        "total_bansha": tot_ban,
        "target_bansha": target,
        "remaining_bansha": round(target - tot_ban, 2),
    }


def human(date: str | None = None) -> str:
    """一句话中文汇报（供自动化/Agent 直接播报）。"""
    s = summary(date)
    lines = [f"【{s['date']} 今日热量】已记 {s['total_bansha']} 板烧（约 {s['total_kcal']} kcal）"
             f" / 目标 {s['target_bansha']} 板烧 / 还差 {s['remaining_bansha']} 板烧"]
    for e in s["entries"]:
        lines.append(f"  · {e['time']} {e['label']}  {e['bansha']} 板烧（{e['kcal']} kcal）")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="每日板烧 / 卡路里累计")
    sub = ap.add_subparsers(dest="cmd")
    a = sub.add_parser("add")
    a.add_argument("--label", required=True)
    a.add_argument("--kcal", type=float)
    a.add_argument("--bansha", type=float)
    a.add_argument("--source", default="mcd")
    a.add_argument("--date")
    s = sub.add_parser("show")
    s.add_argument("--date")
    s.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.cmd == "add":
        try:
            r = add_entry(args.label, args.kcal, args.bansha, args.source, args.date)
        except ValueError as e:
            print(f"错误：{e}", file=sys.stderr)
            return 2
        print(human(args.date))
        return 0
    if args.cmd == "show":
        if args.json:
            print(json.dumps(summary(args.date), ensure_ascii=False, indent=2))
        else:
            print(human(args.date))
        return 0
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
