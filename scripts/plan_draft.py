#!/usr/bin/env python3
"""
douyue-mcd-coach · 方案生成逻辑草案 (plan_draft.py)
-------------------------------------------------
草案：演示如何基于"窦月减肥法"结构 + 麦当劳真实菜单（此处用内置示例数据模拟 MCP 返回）
生成一餐/全天方案，并计算热量缺口、触发健康护栏。

真实部署时：
  - 用麦当劳 MCP 工具 (list-nutrition-foods / query-meal-detail / calculate-price) 替换 SAMPLE 数据；
  - "去酱"通过 query-meal-detail 的 modification 参数实现；
  - 价格用 calculate-price 返回的 price 字段（单位：分）。

仅依赖 Python 标准库。运行：python scripts/plan_draft.py [female|male]
"""
from __future__ import annotations

import json
import sys

# ---- 示例数据：模拟麦当劳 MCP 返回（真实场景由 MCP 工具提供）----
SAMPLE = {
    "double_cheese_burger": {"name": "双层吉士汉堡", "kcal": 440, "protein_g": 25, "price_fen": 2200},
    "grilled_chicken":     {"name": "板烧鸡腿堡",   "kcal": 400, "protein_g": 28, "price_fen": 2100},
    "veg_cup":             {"name": "蔬菜杯",       "kcal": 35,  "protein_g": 2,  "price_fen": 900},
    "steamed_bun":         {"name": "白馒头(100g)",  "kcal": 223, "protein_g": 7,  "price_fen": 300},
    "egg":                 {"name": "水煮蛋",       "kcal": 70,  "protein_g": 6,  "price_fen": 0},
}

# 基础代谢下限（护栏）
BMR_FLOOR = {"female": 1200, "male": 1500}
HEALTHY_DEFICIT_MIN, HEALTHY_DEFICIT_MAX = 300, 500


def build_day(sex: str, lunch_burgers: int = 2, add_veg: bool = True,
              dinner_buns: int = 2, dinner_whole_grain: bool = False) -> dict:
    """按窦月法结构拼出一天方案（草案）。"""
    items = []
    # 早餐：2 水煮蛋
    items.append(("早餐", SAMPLE["egg"], 2))
    # 午餐：去酱汉堡 x N + 蔬菜杯
    burger = SAMPLE["grilled_chicken"]
    items.append((f"午餐·去酱{burger['name']}", burger, lunch_burgers))
    if add_veg:
        items.append(("午餐·蔬菜杯", SAMPLE["veg_cup"], 1))
    # 晚餐：白馒头/粗粮馒头 x N
    bun = SAMPLE["steamed_bun"]
    bun_label = "晚餐·粗粮馒头" if dinner_whole_grain else "晚餐·白馒头"
    items.append((bun_label, bun, dinner_buns))

    total_kcal = sum(s["kcal"] * q for _, s, q in items)
    total_protein = sum(s["protein_g"] * q for _, s, q in items)
    total_price = sum(s["price_fen"] * q for _, s, q in items)

    # 缺口（假设目标 = 基础代谢下限 + 健康缺口中值）
    floor = BMR_FLOOR.get(sex, 1500)
    target = floor + (HEALTHY_DEFICIT_MIN + HEALTHY_DEFICIT_MAX) // 2
    deficit = target - total_kcal

    # 健康护栏
    warnings = []
    if total_kcal < floor:
        warnings.append(f"⚠️ 全天 {total_kcal} 大卡低于基础代谢下限 {floor}，已上调目标/建议加餐。")
    if not dinner_whole_grain:
        warnings.append("⚠️ 晚餐为纯白馒头（精制碳水，缺蛋白/纤维），建议换粗粮馒头+蔬菜/豆腐（改良版）。")
    if deficit > 800:
        warnings.append("⚠️ 热量缺口 >800 大卡/天，属极低碳水，易反弹，请放缓。")

    return {
        "items": [{"meal": m, "name": s["name"], "qty": q,
                   "kcal": s["kcal"] * q, "protein_g": s["protein_g"] * q,
                   "price_yuan": s["price_fen"] * q / 100} for m, s, q in items],
        "total_kcal": total_kcal,
        "total_protein_g": total_protein,
        "total_price_yuan": total_price / 100,
        "deficit_vs_target": deficit,
        "warnings": warnings,
    }


def bansha_units(kcal: float, unit_kcal: float = 400.0) -> float:
    """把任意热量换算成'1 板烧'(板烧鸡腿堡去酱≈400kcal)单位数。"""
    return round(kcal / unit_kcal, 2)


def main() -> None:
    sex = sys.argv[1] if len(sys.argv) > 1 else "female"
    plan = build_day(sex)
    print(json.dumps(plan, ensure_ascii=False, indent=2))
    if plan["warnings"]:
        print("\n" + "\n".join(plan["warnings"]))
    print("\n（草案）输出仅供参考，不构成医疗/营养建议。")

    # 1 板烧单位演示（跨场景热量锚点，基准≈400kcal）
    print("\n[1 板烧单位] 鸡胸沙拉 250kcal ≈", bansha_units(250), "板烧")
    print("[1 板烧单位] 黄焖鸡(去皮+半拳米) 523kcal ≈", bansha_units(523), "板烧")
    print("替代餐指导: 0.9≈360 / 1.0≈400 / 1.2≈480 kcal（详见 references/unit.md）")


if __name__ == "__main__":
    main()
