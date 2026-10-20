# SCI逻辑叙事审查 · sci-logic-narrative-review

模拟目标期刊的第一轮审稿，按一条固定的叙事链条逐环找漏洞，**每次审查强制产出一份带证据定位的漏洞报告**，并判定这份稿子该走哪条叙事路径。

> 旧名 `pre-submit-audit`，已更名，功能不变。

## 它做什么

1. 按 **六个镜头** 审全稿：缺口真实性 → 方案对症性 → 因果闭环 → 贡献可分性 → 图表分层 → 边界自限
2. 做 **双轨比对**：稿件里的每个数字/每个声称 vs 实验台账（数字轨、声称轨、口径轨）
3. 扫 **六类致命项**（F1–F6），命中即约束路径判定
4. 打分并三选一判定路径：**P-A 方法创新型 / P-B 评估认知型 / P-C 证据不足（不可投）**
5. 输出报告：判决摘要、漏洞卡片（含审稿人原话 / 修改处方 / 复审判据）、数字核验表、声称越级清单、正面资产、下一步顺序、边界声明
6. 落盘后跑 `scripts/check_report.py` 自检，**自检不过不许交**

## 怎么用

直接说：

- 「帮我审一下这篇稿，投稿前查一遍」
- 「按审稿人视角挑漏洞」
- 「这篇会不会被拒？哪里最容易被问」
- 「三条贡献是不是同质了」
- 「控制对照够不够、能不能说是方法创新」

首轮审查只需提供：稿件 + 图表/图注 + 目标期刊。**有实验台账才能做完整双轨比对**，没有的话报告会标 `G1 部分` 并禁止给 P-A 判定。

## 文件结构

```
SKILL.md                         路由：流程总览、六个镜头、输出约定、纪律
manifest.yaml                    声明式装载表（按需读文件，不要一次读全）
core/
  stance.md                      审查立场、P0–P3 严重度、红线、七种自我失败模式
  flow.md                        七步执行序列，每步的强制产出
  report-contract.md             报告硬性契约：必填字段、八项卡片、用语禁令
  gap-checklist.md               七类漏洞清单 + 六类致命项速查（审查主体）
  rubric.md                      七维评分、硬阈值、P-A/P-B/P-C 判定、时间裁剪
references/
  judgment-paths.md              三路径逐节改写处方 + 最小补实验集
  methodology-source.md          方法论溯源、严格度三档、按文章类型调权重
  input-intake.md                取料清单、引文抽取、数字核验抽样、多轮差分追踪
assets/
  report-template.md             报告骨架（复制后填写）
  example-report.md              合格样例（自检与校准格式用，内容为虚构示例）
scripts/
  check_report.py                报告契约校验器（退出码 0 通过 / 1 不合格 / 2 读不到）
  check_manifest.py              装载表结构校验（引用是否可达、stage 字段是否齐全）
```

## 装载顺序

`core/stance.md` → `core/flow.md` → `core/report-contract.md` → `core/gap-checklist.md` → `core/rubric.md` → `assets/report-template.md` → 需要处方时读 `references/judgment-paths.md`。

溯源与加严（`references/methodology-source.md`）只在被追问或需要顶刊严度时读。

## 报告校验

```powershell
python scripts/check_report.py "<稿件目录>/审稿报告_SCI逻辑叙事审查_20261020_r1.md"
```

检查 12 类硬性项：元信息八字段、十章覆盖、占位符残留、卡片八字段、严重度合法、至少一条 P1/P2、数字核验表 ≥8 行且结论取值合法、路径与预估结果自洽（P-C 不能配"小修"）、禁用软化表述、非首轮必须有闭环差分表、边界声明三项、文件名规范。

草稿阶段可用 `--allow-placeholders` 跳过占位符检查；`--json` 输出机器可读结果；检查示例/演示报告时用 `--any-filename` 跳过文件名约定（否则会给一条 WARN，不影响通过）。

装载表自检（改了 manifest 或增删文件后跑）：

```powershell
python scripts/check_manifest.py
```

检查每个 stage 的必需字段、`always_load`/`read`/`on_demand` 指向的文件是否真实存在、values 是否有歧义行。

## 与其它 skill 的边界

本 skill **只诊断，不治疗**：

- 要重写某一节的行文 → `nature-polishing` / `nature-writing`
- 要三方协作产出 → `research-collab`
- 本 skill 交付"哪里不行、为什么不行、改成什么样才算行"，不代笔

## 不可触碰的底线

不编造实验、不虚构对照、不隐藏负面结果、不在缺证据时用文字包装替代证据。**故事好看的前提是因果对照闭环；闭环不了就诚实降级——降级后的稿子是能过的稿子，硬撑的稿子是必拒的稿子。**
