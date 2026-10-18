# WorkBuddy 联动开发记录（workbuddy.md）

> 本文件用于在腾讯 WorkBuddy 中开发本项目的对话上下文导出，作为"真实使用 WorkBuddy"的核验凭证，关联赛事专项积分（前 100 名 + 提交本文件 = 3000 积分）。

## 开发背景

- **赛事**：2026 麦当劳程序员创意开发大赛
- **创意来源**：蒋诗萌综艺分享的"窦月减肥法 / 麦当劳减肥法"于 2026-10-13 前后冲上热搜，全网跟风；本项目将其工程化为"可执行 + 健康护栏"的麦当劳 Skill。
- **差异化**：现有参赛项目多为通用"卡路里减脂点餐"，尚无"具体网红减肥法执行器 + 健康护栏"方向（经官方主仓库 `RANKING.md` 榜单与公开仓库调研确认，详见 `references/competition_landscape.md`）。

## 开发过程（在 WorkBuddy 中的关键对话节点）

1. **竞品调研**：分析官方榜单 RANKING.md，识别红海（省钱 / 卡路里）与蓝海（具体减肥法执行）。
2. **调研头部项目**：研究 `mcd-calorie-butler`（味热比）、`mcd-calorie-architect` 等，借鉴健康边界与离线演示思路。
3. **抓取接入文档**：梳理 open.mcd.cn/mcp/doc 的 33 个 Tool 与集成要点（TOON 格式、modification 特制项等）。
4. **生成项目骨架**：5 个必需文件 + SKILL.md + 健康护栏参考 + 方案生成草案。
5. **离线演示页**：`docs/index.html` 单文件零依赖、免 Token，含「麦当劳场景 / 非麦场景·1 板烧换算」双 Tab。
6. **真·官方数据落地**：在 WorkBuddy 中用 Python 实现 `scripts/mcp_client.py`（Streamable HTTP + TOON 解析）与 `scripts/live_plan.py`，直接用官方 `list-nutrition-foods` 拉取真实营养生成窦月法方案；并创建 `install.py` 一键安装到 WorkBuddy。
7. **概念定名**：把"照烧汉堡计量单位"定名为「1 板烧」，全仓统一（unit.md / SKILL.md / 演示页 / 方案脚本）。

## 真实 MCP 调用核验

- **配置位置**：WorkBuddy 左侧【连接器】→ 自定义连接器 → mcd-mcp（已启用，Token 经环境变量注入，不入库）。
- **调用证据**：方案生成 + 执行链路 `now-time-info → list-nutrition-foods → query-meal-detail(modification 去酱) → auto-bind-coupons(领券) → calculate-price(核价) → create-order(确认后下单) → payH5Url(官方 scanToPay 扫码中间页；手机直接打开仅得扫不了的二维码；✅ 已实测：MCP 下的待支付订单确会出现在麦当劳 App「我的订单」、可直接付款，电脑端才用 payH5Url 二维码) → query-order(核对已支付并取 pickupCode)` 均为真实官方接口。
- **已验证真实数据**（2026-10-18 经 `live_plan.py` 实测）：板烧鸡腿堡 = 391 kcal / 23g 蛋白；双层吉士汉堡 = 429 / 27；吉士汉堡包 = 294 / 16；低卡蔬果侧为苹果片（32 kcal）/ 玉米杯（53 kcal）。"1 板烧 ≈ 400 kcal" 的锚定基准由此官方数据支撑。
- **核验脚本**：`python scripts/live_plan.py female`（需 `export MCD_MCP_TOKEN=你的Token`），输出 JSON 含真实热量/蛋白/板烧单位换算。

（说明：本记录由开发者在 WorkBuddy 中导出对话上下文整理而成。）
