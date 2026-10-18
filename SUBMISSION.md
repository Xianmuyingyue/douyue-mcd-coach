# 提交说明 · SUBMISSION

> 麦当劳程序员创意开发大赛参赛项目：**窦月·麦门健康执行器（douyue-mcd-coach）**
> 本文件为提交前的汇总与校验清单，便于核对"有效提交文件"是否齐全。

## 一、项目一句话
把蒋诗萌综艺带火的「窦月减肥法 / 麦当劳减肥法」做成可执行的麦当劳 Skill：**选低卡套餐 → 用「1 板烧」看热量 → 领券核价 → 真实下单 → 麦当劳 App 安全付款 → 每日板烧累计（可选定时提醒）**，并内置医生健康护栏。

## 二、必需文件清单（官方要求，全部齐备）

| 序号 | 文件 | 说明 | 状态 |
|---|---|---|---|
| 1 | `README.md` | 项目介绍 / 安装 / 使用 / 目标用户 | ✅ |
| 2 | `CONTEST_DECLARATION.md` | 官方原文，**一字未改（已逐字比对）** | ✅ |
| 3 | `MCP_INTEGRATION.md` | 所用 Server / Tool / 调用流程 / 业务价值 | ✅ |
| 4 | 源代码 | `scripts/*.py` + `install.py` + `docs/index.html` | ✅ |
| 5 | `workbuddy.md` | WorkBuddy 开发记录（专项加分用） | ✅ |

**额外（增强/加分）**：`mcp-config.example.json`（脱敏占位符）、`SKILL.md`、`references/*`、`docs/`（演示页 + 截图 + 自动化说明）、`scripts/daily_tracker.py`。

## 三、已实测能力（2026-10-18，真实官方 MCP）
- **真实营养** `list-nutrition-foods`：板烧鸡腿堡 391 kcal / 23g 蛋白
- **门店 / 菜单** `query-nearby-stores` / `query-meals`
- **核价** `calculate-price`：2×板烧 = ¥48（上海门店 ¥47）
- **领券** `auto-bind-coupons`：接口通，当前暂无券（code 499）
- **下单** `create-order`：真实创建「待支付」单，**不扣款**；⚠️ 存在 `600039 今日下单数已达上限`（账号级每日次数限制）
- **支付**：订单出现在麦当劳 App「我的订单」，可直接付款（实测尾号 249953 / 下单 20:01:23）

## 四、本地校验（全部通过）
- `python -m py_compile scripts/*.py install.py` ✅
- `python scripts/plan_draft.py` ✅（离线草案可跑）
- `python scripts/daily_tracker.py show` ✅（每日累计可用）
- `python install.py --target .` ✅（结构齐全）
- `docs/index.html` 单文件、零依赖、免 Token ✅
- 全仓 **无 Token 泄露** ✅

## 五、报名 Issue 文案（可直接粘贴）
> 官方校验严格：**标题与正文之间不换行**；**项目地址用裸 URL（不要 Markdown）**。

**标题：**
```
窦月·麦门健康执行器——明星爆款减肥法的可执行麦当劳低卡 + 安全下单
```

**正文（单行，整段粘贴，勿断行）：**
```
【参赛申请】项目名称：窦月·麦门健康执行器（douyue-mcd-coach） 项目地址：https://github.com/Xianmuyingyue/douyue-mcd-coach 项目简介：基于麦当劳官方MCP真实菜单，把"窦月减肥法"工程化为可执行低卡方案，内置医生健康护栏，用"1板烧"计量，支持领券核价下单并在麦当劳App安全付款。
```

## 六、上线步骤
```bash
cd douyue-mcd-coach
git init && git add . && git commit -m "douyue-mcd-coach: 窦月法执行器 + 1板烧 + 真实MCP"
gh repo create douyue-mcd-coach --public --source=. --push
# 然后在官方仓库 Issues 用上面文案提交报名
```

## 七、免责
本项目为麦当劳程序员节创意开发大赛参赛作品，非麦当劳官方产品；输出仅供参考，不构成医疗或营养建议；餐品、价格与供应以麦当劳官方渠道实时结果为准。
