---
title: Learning Roadmap for My Current Level
aliases:
  - CAN SLIM 学习路线
tags:
  - investing
  - can-slim
  - learning-roadmap
status: active
created: 2026-06-16
---

# Learning Roadmap for My Current Level

## 路线原则

你已经会做一些动量筛选和强势股材料收集，所以学习重点不是“股票是什么”，而是把强势股发现流程升级成完整交易系统。

这条路线遵循四个原则：

- 先防守，再进攻：先学止损、卖出和仓位，再扩大选股范围。
- 先图形训练，再下单：能看懂 base、pivot、volume 和 RS，再谈突破买入。
- 先少量手工，再自动化：CAN SLIM 的很多判断需要先肉眼训练，自动化要等规则稳定后再做。
- 先复盘过程，再复盘盈亏：初期最重要的是是否按系统执行。

## 推荐读书顺序

| 顺序 | 内容 | 目标输出 |
|---:|---|---|
| 1 | Chapter 20 | 写出自己的 15 条交易守则 |
| 2 | Chapters 10-12 | 写出亏损、止盈、仓位规则 |
| 3 | Chapters 1-2 | 建立 20 个历史图形案例卡 |
| 4 | Chapters 3-5 | 给候选股增加基本面过滤 |
| 5 | Chapters 6-9 | 把成交量、相对强度、机构和市场方向加入流程 |
| 6 | Chapters 15-17 | 建立行业主题、新闻反应和周复盘机制 |
| 7 | Chapters 14, 18, 19 | 用作补充案例和机构视角 |

## 6 周学习路线

### Week 1 - 规则和风险底座

阅读：Chapter 20, Chapter 10, Chapter 11, Chapter 12。

输出：

- [ ] 写出你的硬止损规则。
- [ ] 写出你的盈利卖出规则。
- [ ] 写出单笔风险比例和最大持仓数量。
- [ ] 建立 [[obsidian/How to Make Money in Stocks - CAN SLIM/05-trade-plan-template|05-trade-plan-template]] 的个人版本。

检查标准：看到任何候选股时，先能回答“错了怎么办”，再回答“能赚多少”。

### Week 2 - 图形训练

阅读：Chapter 1, Chapter 2。

输出：

- [ ] 选 20 个历史赢家案例，做图形卡片。
- [ ] 每张卡标出 base、pivot、breakout volume、失效位置。
- [ ] 建立 “valid setup / faulty setup” 对照表。

练习方法：

- 不急着找今天可以买的股票。
- 每天只看 5 张图，但每张图必须写出买入点、止损点和不买理由。

### Week 3 - CAN: 基本面三件事

阅读：Chapter 3, Chapter 4, Chapter 5。

输出：

- [ ] 给观察名单增加季度 EPS、销售增长、年度 EPS、ROE、新因素字段。
- [ ] 每只候选股写一句基本面 thesis。
- [ ] 区分“真增长”与“一次性反弹”。

检查标准：不能只因为 1 个月涨幅强就进入核心观察名单。

### Week 4 - SLIM: 供需、领导股、机构和市场

阅读：Chapter 6, Chapter 7, Chapter 8, Chapter 9。

输出：

- [ ] 给观察名单增加相对强度、行业强度、成交量、机构参与、市场状态字段。
- [ ] 每天记录市场状态：confirmed uptrend / pressure / correction。
- [ ] 对每只候选股标注：leader、follower、laggard。

检查标准：市场环境不好时，候选股只能观察或轻仓试错，不能重仓进攻。

### Week 5 - 接入你的现有筛选流程

阅读：Chapter 15, Chapter 16, Chapter 17。

输出：

- [ ] 把 `screen_us_momentum.py` 的结果分成 raw momentum、CAN SLIM candidate、watchlist、actionable setup 四层。
- [ ] 对 top 20 候选股做手工 CAN SLIM 审核。
- [ ] 建立每周一次的行业/主题复盘。

检查标准：你的 screener 不再直接生成“可以买”，而是生成“值得进一步研究”。

### Week 6 - 模拟交易和复盘

阅读：补读 Chapter 14；其余章节按兴趣补充。

输出：

- [ ] 每周只选 3-5 个 actionable setup。
- [ ] 每个 setup 写 [[obsidian/How to Make Money in Stocks - CAN SLIM/05-trade-plan-template|05-trade-plan-template]]。
- [ ] 不实盘或小仓位执行，重点记录执行质量。
- [ ] 周末用 [[obsidian/How to Make Money in Stocks - CAN SLIM/06-review-journal-template|06-review-journal-template]] 复盘。

检查标准：连续 10 笔交易后，你能说清楚亏损来自系统正常成本、执行错误，还是规则本身需要改。

## 每日 20 分钟训练

```text
5 分钟: 看大盘状态
5 分钟: 扫观察名单和行业强度
5 分钟: 只看接近买点的图
5 分钟: 写一句今天不该做什么
```

## 每周 60 分钟复盘

- 更新市场状态。
- 更新行业主题。
- 删除不再强势或 thesis 破坏的候选股。
- 复盘本周所有计划：是否按规则买、卖、观望。
- 只改一个规则，不要每周重写系统。

## 什么时候进入下一阶段

满足这些条件，再考虑扩大实盘规模：

- 连续 4 周按模板写交易计划。
- 至少 20 个历史图形案例能独立标注买点和失效点。
- 最近 10 笔模拟或小仓位交易中，大多数亏损都按规则切断。
- 你能区分“系统正常亏损”和“自己违反规则”。
