#!/usr/bin/env python3
"""
douyue-mcd-coach · 真实数据方案生成 (live_plan.py)
-------------------------------------------------
用麦当劳官方 MCP（list-nutrition-foods）拉取真实营养，生成窦月法一天方案。
与 plan_draft.py（内置示例数据）的区别：这里的麦当劳餐品热量/蛋白来自官方实时数据。

依赖环境变量 MCD_MCP_TOKEN。运行：
    export MCD_MCP_TOKEN=你的Token
    python scripts/live_plan.py [female|male]

说明：
  - 午餐汉堡＝板烧鸡腿堡（真实 391 kcal；"去酱"按 -25 kcal 估算，标注"估算"）；
  - 蔬果杯＝麦当劳真实「苹果片」(32 kcal) 作为低卡蔬果侧；
  - 晚餐白馒头为非麦当劳家庭食物，沿用估算值并明确标注"估算/非麦记"；
  - 价格为估算（真实价需 calculate-price + 用户门店，由 Skill 在线调用）。
"""

from __future__ import annotations

import json
import sys

from mcp_client import McdMcpClient
from plan_draft import (
    BMR_FLOOR, HEALTHY_DEFICIT_MIN, HEALTHY_DEFICIT_MAX, bansha_units,
)

UNIT_KCAL = 400.0          # 1 板烧 锚定值（定义见 references/unit.md）
SAUCE_REDUCE_KCAL = 25     # 去酱估算扣减（酱料热量，标注"估算"）


def main() -> int:
    sex = sys.argv[1] if len(sys.argv) > 1 else "female"
    try:
        client = McdMcpClient()
    except RuntimeError as e:
        print("❌ MCP 连接失败：", e, file=sys.stderr)
        print("   请先 export MCD_MCP_TOKEN=你的Token", file=sys.stderr)
        return 2

    burger = client.find_food("板烧鸡腿堡")
    side = client.find_food("苹果片") or client.find_food("玉米杯")
    if not burger:
        print("❌ 未找到板烧鸡腿堡营养数据", file=sys.stderr)
        return 2

    burger_kcal = burger["energyKcal"] - SAUCE_REDUCE_KCAL  # 去酱估算
    burger_protein = burger["protein"]
    side_kcal = side["energyKcal"] if side else 32
    side_protein = side["protein"] if side else 0
    side_name = side["productName"] if side else "苹果片(估算)"

    # 窦月法结构（麦当劳部分用真实数据；白馒头为非麦记估算）
    items = [
        ("早餐·水煮蛋×2",
         {"name": "水煮蛋", "kcal": 70, "protein": 6, "price_yuan": 0.0}, 2),
        (f"午餐·去酱{burger['productName']}×2（去酱-25kcal估算）",
         {"name": f"去酱{burger['productName']}", "kcal": burger_kcal,
          "protein": burger_protein, "price_yuan": 21.0}, 2),
        (f"午餐·{side_name}",
         {"name": side_name, "kcal": side_kcal,
          "protein": side_protein, "price_yuan": 9.0}, 1),
        ("晚餐·白馒头×2（估算/非麦记）",
         {"name": "白馒头(100g)", "kcal": 223,
          "protein": 7, "price_yuan": 3.0}, 2),
    ]

    total_kcal = sum(s["kcal"] * q for _, s, q in items)
    total_protein = sum(s["protein"] * q for _, s, q in items)
    total_price = sum(s["price_yuan"] * q for _, s, q in items)

    floor = BMR_FLOOR.get(sex, 1500)
    target = floor + (HEALTHY_DEFICIT_MIN + HEALTHY_DEFICIT_MAX) // 2
    deficit = target - total_kcal

    warnings = []
    if total_kcal < floor:
        warnings.append(
            f"⚠️ 全天 {total_kcal} 大卡低于基础代谢下限 {floor}，已上调目标/建议加餐。")
    warnings.append(
        "⚠️ 晚餐为纯白馒头（精制碳水，缺蛋白/纤维），建议换粗粮馒头+蔬菜/豆腐（改良版）。")
    if deficit > 800:
        warnings.append("⚠️ 热量缺口 >800 大卡/天，属极低碳水，易反弹，请放缓。")

    plan = {
        "source": "real-mcp",
        "items": [{"meal": m, "name": s["name"], "qty": q,
                   "kcal": s["kcal"] * q, "protein_g": s["protein"] * q,
                   "price_yuan": s["price_yuan"] * q} for m, s, q in items],
        "total_kcal": total_kcal,
        "total_protein_g": total_protein,
        "total_price_yuan": total_price,
        "deficit_vs_target": deficit,
        "bansha_units_total": bansha_units(total_kcal, UNIT_KCAL),
        "warnings": warnings,
    }
    print(json.dumps(plan, ensure_ascii=False, indent=2))
    if warnings:
        print("\n" + "\n".join(warnings))
    print(f"\n[1 板烧单位] 全天 ≈ {plan['bansha_units_total']} 板烧"
          f"（基准 {UNIT_KCAL:.0f} kcal/板烧）")
    print("（真实数据版）输出仅供参考，不构成医疗/营养建议。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
