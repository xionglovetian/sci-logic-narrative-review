# DeepSeek Harness 版安装指南

> 适用：DeepSeek Harness（DSH）桌面版 / Web 版
> 技能格式：`SKILL.md` + 声明式 `manifest.yaml`（渐进披露装载表）

## 一、安装

DSH 会从这些位置发现技能（按优先级）：

| 位置 | 作用范围 |
|---|---|
| `<项目>/.dsh/skills/` | 仅该项目 |
| `<项目>/.agents/skills/` | 仅该项目 |
| `~/.agents/skills/` | 本机所有项目 |
| `~/.ds-harness-desktop/dsh-home/skills/` | 本机所有项目（DSH 家目录） |
| 内置/捆绑目录 | 安装包自带 |

### 用户级（所有项目可用，推荐）

```bash
git clone https://github.com/xionglovetian/sci-logic-narrative-review.git
mkdir -p ~/.agents/skills
cp -r sci-logic-narrative-review/skills/sci-logic-narrative-review ~/.agents/skills/
```

Windows PowerShell：

```powershell
git clone https://github.com/xionglovetian/sci-logic-narrative-review.git
New-Item -ItemType Directory -Force "$env:USERPROFILE\.agents\skills" | Out-Null
Copy-Item -Recurse -Force "sci-logic-narrative-review\skills\sci-logic-narrative-review" "$env:USERPROFILE\.agents\skills\"
```

### 项目级（只在该项目可用）

```bash
mkdir -p /你的项目/.dsh/skills
cp -r sci-logic-narrative-review/skills/sci-logic-narrative-review /你的项目/.dsh/skills/
```

装好后**不需要重启**，DSH 会监听技能目录并自动刷新目录。

## 二、验证安装

```bash
# DSH 装载表完整性
python skills/sci-logic-narrative-review/scripts/check_manifest.py

# 三端清单（顺带验证技能结构）
python skills/sci-logic-narrative-review/scripts/check_platforms.py
```

装好后技能目录里会出现 **SCI逻辑叙事审查**（`sci-logic-narrative-review`），描述里带「投稿前自审 / 模拟审稿 / 挑漏洞」等触发词。

## 三、怎么用

直接说：

- 「用 SCI逻辑叙事审查 审一下这篇稿」
- 「投稿前查一遍，审稿人会打哪里」
- 「这篇会不会被拒？哪里最容易被问」

首轮需要：**稿件 + 图表图注 + 目标期刊**；要完整双轨比对还需**实验台账**。

## 四、本平台特性

- **唯一使用 `manifest.yaml` 的平台**：DSH 读它做按阶段装载（`always_load` + `stages` + `references.on_demand`），避免一次读全。
- 其它宿主（Claude Code / Codex）会忽略 `manifest.yaml`，不影响它们。
- 报告落盘后强制跑 `scripts/check_report.py` 自检，不通过不交付。
- 与 `nature-polishing`、`research-collab` 等既有技能结构一致，可共存。

## 五、常见问题

**Q：装了但会话里看不到？**
A：确认路径是 `~/.agents/skills/sci-logic-narrative-review/SKILL.md`，且 `SKILL.md` 第一行是 `---`（frontmatter 必须存在）。DSH 的日志会写明被忽略的原因（缺 frontmatter、name 不合法等）。

**Q：和 `nature-polishing` 会冲突吗？**
A：不会。本 skill 只诊断不改写；要改行文它会把活交给 `nature-polishing`。

**Q：报告写到哪里？**
A：写到**稿件所在目录**，命名 `审稿报告_SCI逻辑叙事审查_YYYYMMDD_rN.md`，多轮并存不覆盖。
