# ui-taste-engine

> UI 审美进化引擎：把每次生成、评审、返工变成可复用的知识卡，按置信度晋升/衰减。
> 配合 [website-ui-designer](https://github.com/pz857082775/website-ui-designer) 使用。

## 解决什么

| 问题 | 解法 |
|---|---|
| AI 味千篇一律 | 反例库（A 卡）+ 生成前强制过反例清单 |
| 不懂术语的人写不好提示词 | 意图翻译层：自然语言 → 旋钮 + 令牌 + 硬约束 |
| 模板风格单一 | 风格组合 + 每页一个签名细节 |
| AI 缺"好看/专业/交互"的判断 | 判断卡（J 卡）+ 评分卡 + 盲评 + 回归集 |

## 核心机制

**知识生命周期**：候选(1) → 复现(2) → 稳定(3) → 默认(4) → 公理(5)，配 90/180 天衰减与冲突裁决。
**晋升闸门**：证据 ≥3（≥2 个任务）→ 过 10 例回归（均分不降 >2）→ 写回规范 → 才升到 4。
**宪章**：评分权重、验收条、置信度定义不可自我修改，防"自我讨好"。

## 目录

```
ui-taste-engine/
├── SKILL.md
├── references/
│   ├── evolution-protocol.md   # 生命周期、晋升闸门、衰减、冲突裁决、进化日志
│   ├── knowledge-schema.md     # P/M/A/J 四类卡字段规范 + 拒收规则
│   ├── intent-translator.md    # 20+ 条"用户原话 → 参数"翻译表
│   └── evaluation.md           # 盲评胜率/一次通过率/返工轮次 + 专业度 L1-L4
├── knowledge/
│   ├── params/ patterns/ anti-patterns/ judgments/
│   ├── INDEX.md                # 自动生成
│   └── EVOLUTION.log           # 审计线
├── evals/
│   ├── cases.yaml              # 10 个固定回归用例（四类页面 × 四端）
│   └── baseline.md             # 基线分数
└── scripts/kb.py               # CLI：list/show/add/use/promote/decay/check/stats/index
```

## 用法

```bash
python scripts/kb.py list --type A     # 看反例
python scripts/kb.py check             # 健康检查（格式/重复/待衰减）
python scripts/kb.py use P-001         # 记一次复用
python scripts/kb.py promote P-001     # 晋升（证据不足会被拒）
python scripts/kb.py stats             # 输出指标表
python scripts/kb.py index             # 重建 INDEX.md
```

## 评估标准（摘要）

- **盲评胜率** ≥60% 及格 / 75% 良好 / 85% 优秀
- **一次通过率** 目标 6 个月内 70%
- **平均返工轮次** 目标 ≤1.5
- **知识复用率** ≥50%，高置信占比 20-35%，衰减率 5-15%

任何一项变差，都不算"进化成功"。

## License

MIT
