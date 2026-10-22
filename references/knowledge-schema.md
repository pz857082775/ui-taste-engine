# 知识卡规范（Knowledge Schema）

四类卡：**P 参数 / M 手法 / A 反例 / J 判断**。
一张卡只讲一件事；能写数值就不写形容词。

---

## 通用字段（所有卡必填）

```yaml
---
id: P-003                     # 类型前缀 + 三位序号，唯一
type: P                       # P | M | A | J
title: 强调色每屏 3-5 次        # 一句话，可直接当规则读
scope: dashboard              # marketing | dashboard | creator | service | mobile | global
platform: [pc, h5]            # pc | h5 | miniapp | app | all
confidence: 3                 # 1-5，见 evolution-protocol
evidence: 3                   # 独立验证次数
sources:                      # 至少 1 条，可追溯
  - "ui-craft Top-12 规则 / 2026-10-22"
  - "任务 2026-10-22-咖啡H5"
created: 2026-10-22
last_used: 2026-10-22
status: active                # active | stale | archived
applies_to: "信息密度中高的后台与落地页首屏"
---
```

正文用三段：**规则 / 为什么 / 怎么用**。可选第四段：**反例**。

---

## P 卡 · 参数（给具体数值）

```markdown
---
id: P-003
type: P
title: 强调色每屏 3-5 次
scope: dashboard
platform: [pc]
confidence: 4
evidence: 4
sources: ["ui-craft Top-12 #10", "任务 2026-10-21-云商后台"]
created: 2026-10-22
last_used: 2026-10-22
status: active
applies_to: "后台单屏（不含弹层），强调色=主色实心按钮+激活态+关键数字"
---

## 规则
单屏强调色出现 3-5 次；超过 5 次焦点被稀释，少于 3 次找不到重点。

## 为什么
Hick 定律：每次强调都在争夺注意力预算。第 6 处出现时，前 5 处全部贬值。

## 怎么用
数一遍：主按钮 1 + 激活导航 1 + 关键数字 1 + 链接 1 = 4，合格。
若超了，把次要动作降级为描边或文字按钮。
```

---

## M 卡 · 手法（给可复现的结构/动作）

```markdown
---
id: M-002
type: M
title: KPI 卡四段结构
scope: dashboard
platform: [pc]
confidence: 4
evidence: 5
sources: ["医疗工作台截图拆解 2026-10-22", "电商工作台截图 2026-10-21"]
created: 2026-10-22
last_used: 2026-10-22
status: active
applies_to: "所有后台首页的数据概览行"
---

## 规则
图标软底方块 40px(radius 12) → 标签 13px 灰 → 数字 26-28px/750 tabular → 趋势 12px（箭头+百分比+对比期）。

## 为什么
先给"这是什么"（图标+标签），再给"多少"（数字），最后给"变好还是变坏"（趋势）——符合阅读的因果顺序。

## 怎么用
四张卡等宽、gap 16、数字右对齐；趋势色全站统一（金融红涨/通用绿涨二选一）。
```

---

## A 卡 · 反例（错误示范 + 替代方案）

```markdown
---
id: A-001
type: A
title: CSS 预隐藏内容导致 CDN 失败时整页空白
scope: global
platform: [all]
confidence: 4
evidence: 1
sources: ["实测 2026-10-22 test8 医疗页预览空白"]
created: 2026-10-22
last_used: 2026-10-22
status: active
applies_to: "任何用 GSAP 做入场的页面"
---

## 错误长这样
```css
.js-anim .anim{opacity:0}
```
```js
document.documentElement.classList.add('js-anim');
if(!window.gsap) return;
```

## 为什么错
CDN 不可达时脚本提前 return，隐藏类永远不移除 → 内容全在 DOM 里但全透明，用户看到的是空白壳。

## 改成
不写预隐藏；初始态交给 `gsap.from()`；守卫 `if(!window.gsap || reduced) return;`。
```

---

## J 卡 · 判断（什么时候用哪个）

```markdown
---
id: J-002
type: J
title: 趋势色按领域定，全站只能一种
scope: global
platform: [all]
confidence: 4
evidence: 3
sources: ["电商工作台（红涨）vs 自媒体/医疗工作台（绿涨）截图对比 2026-10-21~22"]
created: 2026-10-22
last_used: 2026-10-22
status: active
applies_to: "带同比/环比趋势的后台指标卡"
---

## 规则
金融/证券场景：涨红跌绿；通用数据产品：涨绿跌红。全站只允许一种，不许混用。

## 为什么
用户对"红/绿=好/坏"有强预期，混用会造成误读；而不同领域预期本身相反。

## 怎么用
在 DESIGN.md 里显式写一行 `trend: red-up | green-up`，之后所有图表、KPI、徽章都遵守。
```

---

## 命名与索引

| 前缀 | 目录 | 示例 |
|---|---|---|
| P | `knowledge/params/` | `P-003-accent-budget.md` |
| M | `knowledge/patterns/` | `M-002-kpi-card.md` |
| A | `knowledge/anti-patterns/` | `A-001-prehide-blank.md` |
| J | `knowledge/judgments/` | `J-002-trend-color.md` |

文件名 = `{ID}-{kebab英文短名}.md`，保证可 grep、可排序。
`knowledge/INDEX.md` 由 `kb.py` 汇总（不要手写）。

## 拒收规则（`kb.py add` 会拦）

1. 缺 `sources` / `evidence` / `applies_to`
2. `title` 含形容词而无具体对象（如"更好看的配色"）
3. 一张卡写了 3 条以上规则（拆分）
4. 与已有卡 `title` 高度重复（提示合并，而非新增）
5. `confidence ≥3` 但 `evidence <3`（自相矛盾）
