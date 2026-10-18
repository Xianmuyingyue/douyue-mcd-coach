# MCP 接入与调用说明（MCP_INTEGRATION.md）

## 一、使用的 MCP Server

- **服务名**：mcd-mcp
- **接入地址**：`https://mcp.mcd.cn`
- **协议**：Streamable HTTP
- **鉴权**：请求头 `Authorization: Bearer ${MCD_MCP_TOKEN}`（Token 经环境变量注入，不入库）

## 二、实际使用的 Tool 与用途

本项目围绕"窦月减肥法执行 + 健康护栏"编排以下麦当劳 MCP 工具：

| Tool | 用途 |
|---|---|
| `now-time-info` | 获取当前时间，确定进食窗口（8 小时）与打卡日期 |
| `list-nutrition-foods` | 获取官方营养数据（TOON 格式，需解析），作为热量/蛋白核算底表 |
| `query-meals` | 查询可售餐品与促销价，筛选用餐项 |
| `query-meal-detail` | 查询餐品详情，使用 `modification` 特制项实现"去酱/减酱"等健康改造 |
| `calculate-price` | 对生成的方案核价（官方口径，单位：分），下单前带已领券重算实付 |
| `auto-bind-coupons` | 自动领取当前可领的全部优惠券（免费、无资金风险，默认可执行），帮用户拿满优惠 |
| `create-order` | 生成真实订单；仅当用户**显式说"下单"并经二次确认**后调用 |
| `query-nearby-stores` | 定位附近门店，生成可取餐方案（下单链路必填 `storeCode`） |

> 注：执行器默认**自动领券**（零风险、帮用户省钱），但**不静默代付**——`create-order` 必须在用户明确指令 + 金额/门店/清单二次确认后才提交。

## 三、调用流程（典型一次"午餐安排 + 执行"）

1. `now-time-info` → 判断是否在进食窗口内；
2. `list-nutrition-foods` + `query-meals` → 取得板烧鸡腿堡 / 双层吉士 / 苹果片等的真实热量与价格；
3. `query-meal-detail` → 对汉堡施加 `modification`（去酱）；
4. 计算全天缺口，触发健康护栏判断（见 `references/health.md`）；
5. 输出方案卡（热量 · 蛋白 · 价格 · 门店）；
6. **领券**：`auto-bind-coupons` 自动领取可领优惠；
7. **核价**：`calculate-price` 带上已领券计算实付金额；
8. **下单**：仅当用户说"下单 / 帮我买"时，展示餐品清单 + 门店 + 实付金额并二次确认，确认后 `create-order` 生成订单，回执订单号并提示"本餐 ≈ X 板烧"。

## 四、业务价值

- **真实集成**：所有热量与价格均来自官方 MCP，非模型臆测，符合"真实使用麦当劳 MCP"的参赛要求；
- **热点 + 健康**：把爆火网红减肥法变成可执行、且守住健康底线的工具，兼具传播性与责任感；
- **可核验**：调用链路清晰，评委可一键复现真实调用证据。

## 五、已落地实现（代码）

| 文件 | 作用 |
|---|---|
| `scripts/mcp_client.py` | 麦当劳 MCP Streamable HTTP 客户端：`initialize` 握手、`list_nutrition_foods()` 解析 TOON、`call_tool()` 通用调用，并封装 `auto_bind_coupons()`（领券）/ `calculate_price()`（核价）/ `create_order()`（下单）；Token 仅从 `MCD_MCP_TOKEN` 环境变量读取，绝不入库 |
| `scripts/live_plan.py` | 用**真实**营养数据生成窦月法一天方案（对照 `plan_draft.py` 的内置示例版） |
| `scripts/plan_draft.py` | 离线草案（内置示例数据，零依赖，无需 Token，便于评委免环境秒看逻辑） |

### TOON 解析要点
`list-nutrition-foods` 的 `data` 为紧凑格式：
`[160]{productName,nutritionDescription,energyKj,energyKcal,protein,fat,carbohydrate,sodium,calcium}:` 后接逗号分隔行。
返回文本内嵌一份原始 JSON（`## Original Response` 之后），需先抽取并 `json.loads` 取出 `data`，再按字段解析（数值转 int/float，`null` 转 None）。

### 已验证的真实数据（2026-10-18 拉取）
- 板烧鸡腿堡 = **391 kcal / 23g 蛋白**（"1 板烧 ≈ 400 kcal" 基准的官方依据）；
- 双层吉士汉堡 = 429 kcal / 27g；吉士汉堡包 = 294 kcal / 16g；
- 低卡蔬果侧在营养接口中为 **苹果片（32 kcal）/ 玉米杯（53 kcal）**，窦月法中的"蔬菜杯"在真实方案里映射到苹果片并标注。

> 注：`query-meal-detail` / `calculate-price` / `create-order` 需门店 `storeCode` + 餐品 `productCode`（下单链路，自选门店后调用）；`auto-bind-coupons` 免费、无需门店即可领券。本骨架的离线/演示版以营养数据为核验核心；完整 Skill 在用户选定门店后走"领券 → 核价 → 下单"真实执行链路。

### 实测调用要点（2026-10-18 全链路验证）

| 环节 | 结论 |
|---|---|
| 领券 `auto-bind-coupons` | ✅ 调用成功。实测当前账号 **暂无可领取的优惠券**（`code 499`），属正常动态投放，非代码问题；有券时会真绑到账户 |
| 门店 `query-nearby-stores` | ✅ **必须同时传 `city` + `keyword`**（仅传其一会报"城市名或关键词不能为空"），`searchType=2` 按位置搜 |
| 餐品 `query-meals` | ✅ 入参 `storeCode + orderType=1 + beType=1`，返回 `data.meals` 为 `code → {name, currentPrice, canWithOrder}`；`canWithOrder=true` 的套餐/单品方可在下单链路使用 |
| 核价 `calculate-price` | ✅ `items` 字段是 **`productCode`（不是 `code`）** + `quantity`；返回 `data.price/originalPrice/discount` 单位 **分**。实测 2×板烧鸡腿堡(`1406`) = **4800 分 = ¥48**，`discount=0`（无券） |
| 下单 `create-order` | ✅ 已真实建单（待支付，不扣款）；入参同核价 + 到店 `orderType=1`。⚠️ 实测存在账号级**每日下单次数上限**，超限返回 `600039 今日下单数已经上限`（与餐品无关，勿误判为商品不可下） |

> 实测门店：麦当劳上海某门店（门店名称与 storeCode 已脱敏）；板烧鸡腿堡单品 `1406`、四件套 `9900000890`。

### 支付交付策略（已真机实测修正）

`create-order` 只生成「待支付」订单，返回 `payH5Url`（实测 `https://m.mcd.cn/mcp/scanToPay?orderId=...`）+ `payId`，**不直接扣款**。

**真机实测行为（2026-10-18，iPhone）**：在手机上直接打开 `payH5Url`，页面显示"**扫码进入麦当劳 App 支付**"并给出一个二维码；同一部手机无法扫描自己的屏幕，需截图后再用麦当劳 App 扫描才能进入支付。→ 结论：`payH5Url` 的 `scanToPay` 页是**为跨设备扫描设计的中间页**，不是"一键唤起 App/小程序"的深链。

正确交付：
1. **首选（✅ 已实测验证）**：引导用户「打开麦当劳 App → 我的订单 → 待支付 → 直接付款」——**实测 2026-10-18：MCP 下单的待支付订单确实出现在 App「我的订单」（尾号 249953、下单 20:01:23），用户可直接在 App 内付款**，无需扫码，最安全顺手。
2. **次选（跨设备）**：用户在电脑上时，打开 `payH5Url` 得二维码，用手机上的麦当劳 App 扫码支付。
3. **禁止**：让用户在手机上直接打开 `payH5Url`（只会得到扫不了的二维码）；Skill 侧二维码仅限"电脑→手机 App 扫"。
4. **支付后核对**：`query-order` 确认状态（待支付 → 已支付/配餐中）并取 `pickupCode`；未付提示倒计时，不假设成功。

> 教训：不要把"打开 payH5Url"等同于"唤起 App 支付"——实测是扫码中间页。支付最顺的路径是直接进 App「我的订单」付款。
