# Claude Code 版安装指南

> 适用：Claude Code（终端 CLI、VS Code 扩展、JetBrains 插件、桌面版本地会话）
> 技能格式：Agent Skills（`SKILL.md` + `name` / `description` frontmatter）

## 一、安装

### 方式 A：作为技能安装（最简单，推荐）

Claude Code 会把 `~/.claude/skills/<name>/SKILL.md` 当作全局技能，在所有项目中可用。

```bash
git clone https://github.com/xionglovetian/sci-logic-narrative-review.git
mkdir -p ~/.claude/skills
cp -r sci-logic-narrative-review/skills/sci-logic-narrative-review ~/.claude/skills/
```

Windows PowerShell：

```powershell
git clone https://github.com/xionglovetian/sci-logic-narrative-review.git
New-Item -ItemType Directory -Force "$env:USERPROFILE\.claude\skills" | Out-Null
Copy-Item -Recurse -Force "sci-logic-narrative-review\skills\sci-logic-narrative-review" "$env:USERPROFILE\.claude\skills\"
```

只想在当前项目可用，就放到 `<项目>/.claude/skills/`。

### 方式 B：作为插件安装（走 marketplace）

本仓库自带 `.claude-plugin/marketplace.json`，本身就是一个 Claude Code marketplace。在 Claude Code 会话里依次执行：

```
/plugin marketplace add xionglovetian/sci-logic-narrative-review
/plugin install sci-logic-narrative-review@sci-logic-narrative-review-marketplace
```

安装范围（user / project / local）在 `/plugin` 界面里选择。

### 方式 C：直接从本地目录加载（开发调试用）

```bash
git clone https://github.com/xionglovetian/sci-logic-narrative-review.git
claude --plugin-dir ./sci-logic-narrative-review
```

不改任何全局配置，适合先试一次。

## 二、验证安装

```bash
# 官方校验器（在仓库根目录执行）
claude plugin validate . --strict

# 看插件组件清单与 token 成本
claude plugin details sci-logic-narrative-review

# 列出已装插件
claude plugin list
```

技能方式安装的话，在会话里问一句「你有哪些技能可用？」应能看到 **SCI逻辑叙事审查 / sci-logic-narrative-review**。

## 三、怎么用

在 Claude Code 里直接说：

- 「用 SCI逻辑叙事审查 审一下这篇稿」
- 「投稿前查一遍，审稿人会打哪里」
- 「三条贡献是不是同质了」
- 「这篇会不会被拒？」

插件方式安装的，也可以显式调用：`/sci-logic-narrative-review:sci-logic-narrative-review`

首轮需要提供：**稿件 + 图表图注 + 目标期刊**。要拿到完整双轨比对，还需要**实验台账**（否则报告标 `G1 部分` 且禁止判 P-A）。

## 四、本平台特性

- **渐进披露**：初始只加载 `name` + `description`，真正用到时才读 `SKILL.md` 全文，再按需读 `core/`。占用极低。
- **插件上下文成本**可见：`/plugin` 的 **Context cost** 会显示估算值；本 skill 只有一个技能，成本很小。
- `manifest.yaml` 是 DeepSeek Harness 专用，Claude Code 会忽略它，不影响加载。
- 相对路径（`core/stance.md` 等）由 Claude Code 按技能目录解析，装到哪都能找到。

## 五、常见问题

**Q：装完没生效？**
A：确认路径是 `~/.claude/skills/sci-logic-narrative-review/SKILL.md`（要 SKILL.md 直接在技能目录里，不是多套一层）。然后重开会话。

**Q：`claude plugin validate` 报 `No manifest found`？**
A：那是把**技能目录**当插件校验了。技能目录本身不需要 `.claude-plugin/`；要校验插件请指向仓库根目录。

**Q：想改成英文报告？**
A：直接要求「用英文出报告」，skill 支持，但默认中文。

**Q：和别的 skill 冲突吗？**
A：不会。它只在自己被触发时工作，不常驻改写其它行为。
