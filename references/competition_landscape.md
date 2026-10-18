# 竞争态势分析（references/competition_landscape.md）

> 数据快照：官方主仓库 `RANKING.md`，更新时间 **2026-10-18 17:00:48**。
> 排行榜仅展示 Star>0 的前 100 名；定榜以 2026-10-26 00:00 采集为准。
> 官方实时榜单：https://github.com/M-China/mcd-developer-innovation-challenge/blob/main/RANKING.md

## 一、头部格局（Top 12）

| 名次 | 项目 | Star | 方向（研判） |
|---:|---|---:|---|
| 1 | mcd-saver-strategist | 534 | 省钱/优惠策略（Agent） |
| 2 | mcd-coupon-strategist | 482 | 优惠券策略（Agent） |
| 3 | mcd-budget-meal | 399 | 预算套餐（Agent） |
| 4 | mccarbon | 389 | 碳足迹（差异化，非餐饮省钱） |
| 5 | maimen-certification | 343 | 麦门认证/趣味（Agent） |
| 6 | McOracle | 320 | 全能咨询（Agent） |
| 7 | McLife-Desk | 290 | 生活台/聚合（Agent/Plugin） |
| 8 | mcd-party-officer | 244 | 派对筹办（Agent） |
| 9 | mcd-wrapped | 211 | 年度回顾（Automation/趣味） |
| 10 | mcd-party-planner | 184 | 派对规划（Agent） |
| 11 | mcd-calorie-butler | 149 | **卡路里/热量（Agent）** |
| 12 | mcpet | 117 | 宠物/趣味（Agent） |

## 二、按"形态"分类（用户此前要求的梳理）

本赛事所有作品本质都是"基于麦当劳 MCP 的 Skill"，按交付/交互形态可粗分为四类：

| 形态 | 占比研判 | 典型项目 |
|---|---|---|
| **智能体 / Agent**（对话式助手，主流形态） | ≈70% | mcd-saver-strategist、McOracle、mcd-party-officer、mcd-calorie-butler |
| **插件 / Plugin**（接入某宿主的能力扩展） | ≈15% | McLife-Desk、mcd-voice-order-assistant |
| **自动化流程 / Automation**（定时/事件触发） | ≈10% | mcd-wrapped、git-to-big-mac-hedger、mcd-commit-fuel |
| **应用 / App**（带 UI 的独立小工具） | ≈5% | mcd-china-map、部分带网页演示的项目 |

**结论**：头部几乎全是"省钱/优惠/套餐推荐"类 Agent（红海）；差异化赛道（碳足迹、派对、趣味人格）已有占位。

## 三、"减肥 / 热量"赛道核查（红海确认）

确实已有多条减脂/热量线，但并非"具体网红减肥法执行器"：

| 项目 | Star | 方向 |
|---|---:|---|
| mcd-calorie-butler | 149 | 味热比 / 热量查询（最贴近，但通用） |
| mcd-order-calories | 38 | 点餐热量 |
| mcd-calorie-budget-skill | 22 | 热量预算 |
| mcd-macro-strategist | 26 | 宏量营养策略 |
| mcd-fit-planner / mcd-fit-coach | 30 / 16 | 健身规划 / 教练 |
| walk-kcal / mcd-100kcal | 42 / 16 | 步数热量 / 100kcal 单位 |

**蓝海确认**：**没有任何项目**锚定"窦月减肥法 / 蒋诗萌 / 麦门减肥"这一具体爆款网红法，更没有"具体减肥法执行器 + 医生健康护栏 + 1 板烧跨场景计量单位"的组合。这正是本项目的差异化卡位。

## 四、本项目的竞争策略

1. **蹭热点不卷红海**：不去做通用"卡路里查询"（已被 mcd-calorie-butler 占坑），而是绑定 2026-10-13 热搜的"窦月法"，自带传播势能。
2. **社会责任加分**：内置健康护栏（反对极端节食），在"减肥"赛道里凸显可信度与合规性，规避"鼓励不健康减肥"的风险。
3. **品牌感知创新**："1 板烧"计量单位把非麦当劳场景也纳入麦记话语体系，强化品牌关联——评委与用户都能记住。
4. **真实数据背书**：`live_plan.py` 用官方 `list-nutrition-foods` 实测（板烧鸡腿堡 391 kcal），区别于纯模型估算的竞品。
5. **可秒验**：免 Token 离线演示页 `docs/index.html` 降低评委体验门槛。

## 五、支付/下单能力：竞品调研（2026-10-18）

**结论先说：`create-order` + `payH5Url` 支付，是多家作品的标配，不构成差异化；"显式渲染二维码"这一具体做法反而非主流。**

公开可检索到的同类实现（都用 `create-order` 拿 `payH5Url`）：
- `cwyhkyochen-a11y/mcdonalds-mcp`：18 工具点餐助手，明确写"支付链接变成了扫码页"。
- `zhutoumeme/mcd-git`：用 git 命令点麦当劳，真实下单实测，`payH5Url` 指向 m.mcd.cn、15 分钟过期。
- `openclaw-skills/mcdonalds-mcp-order-lite`：create-order 后返回 payH5Url，付款后 query-order。
- `Mcd-Nailong`：完整写清"create-order 不扣款、只返回 payH5Url/payId；2026-04 起改为扫码支付页"。
- `leizhengyang/MCD-skills`：**明确"禁止调用 generate_qrcode.py 或展示二维码"**，改用 payH5Url / scheme 唤起 App / GenUI 支付卡。

**两个关键技术事实：**
1. `payH5Url` 自 2026-04 起已变成 **scanToPay 扫码页**：`https://m.mcd.cn/mcp/scanToPay?orderId=...`——用户打开它本身就是"扫码/调起支付"体验。
2. 因此"扫码支付"这个**效果**，很多作品靠"直接给 payH5Url 链接"就能达到；把 URL **另行渲染成二维码图片**只是换了交付形态，且已有项目主动禁用二维码（改用链接/唤起 App 更顺）。

**对本项目的启示：**
- 不要把"提供二维码支付"当作核心卖点——会被评委视作"大家都有的基础能力"。
- 真正的差异化仍在**场景层**：窦月减肥法执行器 + 1 板烧跨场景单位 + 医生健康护栏 + 一键领券下单的整合体验。
- 若要保留二维码：定位为"桌面端免跳转、可用手机扫的便捷交付"，而非"独有功能"；并优先保证移动端能用 payH5Url/scheme 直接唤起支付。

**真机实测补充（2026-10-18）**：`payH5Url`（`m.mcd.cn/mcp/scanToPay` 页）在手机上打开，显示"扫码进入麦当劳 App 支付"+ 一个二维码，**同一部手机无法自扫**，需截图再用麦当劳 App 扫。这印证了"移动端二维码是伪需求"——最顺的支付路径其实是**直接进麦当劳 App「我的订单」待支付订单里付款**，`payH5Url` 只适合"电脑出码、手机 App 扫"的跨设备场景。**后续已实测确认（尾号 249953、下单 20:01:23）：MCP 下的待支付订单确实出现在 App「我的订单」，可直接付款——这条"官方渠道付款"路径闭环成立。**
