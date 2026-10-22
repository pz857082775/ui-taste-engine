---
name: ui-taste-engine
version: 1.1.0
updated: 2026-10-22
description: UI 审美进化引擎。把每次生成、评审、用户反馈转化为可复用的 UI 知识卡，并按置信度晋升/衰减，持续降低 AI 味、提升界面判断力。当需要"积累 UI 经验"、"让界面越做越好"、"消除 AI 模板感"、"把自然语言需求翻译成设计参数"、"评估界面专业度"时使用。配合 website-ui-designer 使用。触发词：UI知识库、审美积累、自我进化、AI味、模板感、界面评审、设计Token沉淀。
---

# UI Taste Engine — UI 审美进化引擎

> **版本 1.1.0** · 2026-10-22 · 变更见 [CHANGELOG.md](./CHANGELOG.md)
> 新用户先看 [README.md](./README.md) 的「三分钟上手」；本文件是机制规范。

## 定位

**它不是生成器，是判断力的积累器。**
`website-ui-designer` 负责"把需求变成提示词"，本引擎负责"让这些提示词一次比一次准"。

一句话：**把每一次生成、每一次返工、每一次用户皱眉，变成下一条可执行的规则。**

## 要解决的四个核心问题

| 问题 | 现状 | 本引擎的解法 |
|---|---|---|
| **① 千篇一律的 AI 味** | 模型默认给出"所有页面的平均值" | 反例库（A 卡）+ 生成前强制过反例清单 + 同质化检测 |
| **② 不懂术语的人写不出好提示词** | 用户只会说"高级点""干净点" | 意图翻译层（`intent-translator.md`）：自然语言 → 旋钮值 + 令牌 + 硬约束 |
| **③ 模板风格单一** | 每次都长一个样 | 风格基因库 + 强制组合（主风格 × 辅助 × 骨架 × 动效档位）+ 每页一个签名细节 |
| **④ 缺"好看/专业/交互"的判断** | 只能生成，不能判断 | 判断卡（J 卡）+ 评分卡 + 盲评对照 + 回归集 |

## 能力边界（明确不做什么）

**做**：积累参数/手法/反例/判断四类知识；把知识晋升为默认规则；评估生成结果的相对优劣；把自然语言转成设计参数。

**不做**：
1. **不做品牌策略**：命名、定位、传播口号不在范围内
2. **不做合规认证**：只做 WCAG AA 自查，不出具无障碍合规结论
3. **不碰后端**：接口、数据、权限、性能压测不涉及
4. **不替代人的最终审美决策**：只提供"可解释的依据"，不宣布"这就是美"
5. **不无来源地学习**：每条知识必须有来源标签（任务场景/参考 URL/日期/证据数），无来源不入库
6. **不自我修改宪章**：`boundaries` 与评分权重属于宪章条款，只有人工批准才能改（防模型自我漂移）

## 四个工作模式

### 模式 1 · 生成前（Pre-flight Knowledge）
1. 判断页面类型与平台（营销页/数据工作台/创作工作台/服务型工作台 × PC/H5/小程序/APP）
2. 从知识库检索：`scope` 命中 + 置信度 ≥3 的 P/M/J 卡
3. 从反例库取出该类型的 A 卡，转成"硬性禁止项"写进提示词
4. 产出提示词骨架 → 交给 `website-ui-designer` 的九段框架

### 模式 2 · 生成后（Capture）
每次任务结束，强制产出 0-3 条经验条目：
```
场景：{页面类型}/{平台}
用了什么：{参数或手法，具体到数值}
结果：{一次通过 / 改了 N 轮 / 用户反馈}
可复用结论：{若有}
证据：{本次任务 id 或截图}
```
无结论就不写——**宁可不记，不要记垃圾**。

### 模式 3 · 评审（Judge）
用 `website-ui-designer/references/review-rubric.md` 打分，输出：
Distinction / Craft / Usability 三轴分 + 业务影响标签 + 前三条问题与具体改法。
评审结论本身也是知识来源：反复出现的问题 → 升级为 A 卡。

### 模式 4 · 进化（Evolve）
按 `references/evolution-protocol.md` 执行：
采集 → 规范化 → 验证 → 晋升 / 衰减 / 冲突裁决。
晋升到 confidence 4 的规则，回写进 `website-ui-designer` 的对应规范文件。

## 知识库结构

```
ui-taste-engine/
├── knowledge/
│   ├── INDEX.md              # 知识索引（自动/半自动维护）
│   ├── params/               # P 卡：具体数值（字号、间距、阴影、圆角）
│   ├── patterns/             # M 卡：手法（构图、动效、组件结构）
│   ├── anti-patterns/        # A 卡：反例 + 替代方案
│   └── judgments/            # J 卡：可操作的判断规则（什么时候用哪个）
├── evals/
│   ├── cases.yaml            # 10 个固定回归用例
│   └── baseline.md           # 基线分数（晋升闸门用）
├── references/
│   ├── evolution-protocol.md # 生命周期、置信度、晋升/衰减/冲突
│   ├── knowledge-schema.md   # 四类卡的字段规范
│   ├── intent-translator.md  # 自然语言 → 参数
│   └── evaluation.md         # 指标、盲评、专业度阶梯
└── scripts/kb.py             # 知识库 CLI：add/list/check/promote/decay/use/stats
```

## 常用命令

```bash
python scripts/kb.py list --type A            # 看反例库
python scripts/kb.py add card.md              # 新增知识卡（会校验字段）
python scripts/kb.py check                    # 健康检查：过期/低证据/冲突
python scripts/kb.py use P-003                # 记录一次复用（复用率指标）
python scripts/kb.py promote P-003            # 晋升（需 evidence≥3）
python scripts/kb.py decay                    # 衰减（90 天未用降置信）
python scripts/kb.py stats                    # 输出评估指标
```

## 硬规则（防止知识库腐烂）

1. **无来源不入库**：缺 `sources` 或 `evidence` 的卡直接拒收
2. **一卡一事**：一张卡只讲一条规则，禁止"综合建议"
3. **数值优先**：能写数值就不写形容词；写不出数值说明还没拆到底
4. **可复现才算数**：只有 1 次证据的卡置信度上限 2，不得进默认规则
5. **晋升必须过回归**：confidence 4 之前必须跑 `evals/cases.yaml`，均分不得下降 >2 分
6. **衰减是义务**：90 天未复用的卡自动降级，180 天标记 stale
7. **冲突必须显性化**：同一场景两条规则矛盾时，记录裁决理由，不许静默覆盖

## 与 website-ui-designer 的关系

```
需求 → [ui-taste-engine 检索知识] → [website-ui-designer 写提示词/生成]
                                              ↓
                     [评审 + 用户反馈] → [ui-taste-engine 采集/晋升/衰减]
                                              ↓
                                    回写规范文件（confidence 4）
```

**分工纪律**：本引擎不直接生成界面；`website-ui-designer` 不自己攒经验。
两者通过 `knowledge/` 与规范文件单向流动（引擎 → 设计器）。
