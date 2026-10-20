# Codex 版安装指南

> 适用：Codex CLI、IDE 扩展、ChatGPT 桌面版里的 Codex
> 技能格式：Agent Skills（`SKILL.md` + `name` / `description` frontmatter）

## 一、安装

Codex 的独立技能放在 `~/.codex/skills/<name>/SKILL.md`，也可以用 `config.toml` 的 `[[skills.config]]` 指向任意路径。

### 方式 A：装成独立技能（推荐，最稳）

```bash
git clone https://github.com/xionglovetian/sci-logic-narrative-review.git
mkdir -p ~/.codex/skills
cp -r sci-logic-narrative-review/skills/sci-logic-narrative-review ~/.codex/skills/
```

Windows PowerShell：

```powershell
git clone https://github.com/xionglovetian/sci-logic-narrative-review.git
New-Item -ItemType Directory -Force "$env:USERPROFILE\.codex\skills" | Out-Null
Copy-Item -Recurse -Force "sci-logic-narrative-review\skills\sci-logic-narrative-review" "$env:USERPROFILE\.codex\skills\"
```

### 方式 B：用 config.toml 显式登记（便于开关）

在 `~/.codex/config.toml` 里加：

```toml
[[skills.config]]
path = "C:/path/to/sci-logic-narrative-review/skills/sci-logic-narrative-review/SKILL.md"
enabled = true
```

改完需要**重启 Codex**。想临时关掉就改成 `enabled = false`。

### 方式 C：装成插件

本仓库根目录的 `plugin.json` 是 Agent Plugins 清单，`skills/` 是插件内技能目录，`.agents/plugins/marketplace.json` 是本仓库的市场目录。

```bash
codex plugin marketplace add xionglovetian/sci-logic-narrative-review
codex plugin marketplace list
```

在 `config.toml` 里按 `插件名@市场名` 启用：

```toml
[plugins."sci-logic-narrative-review@sci-logic-narrative-review"]
enabled = true
```

> 说明：Codex 的插件**安装界面**主要在 ChatGPT 桌面版（Plugins 目录）。CLI 侧用方式 A 或 B 最省事。

## 二、验证安装

```bash
# 三端清单校验（零依赖，仓库根目录执行）
python skills/sci-logic-narrative-review/scripts/check_platforms.py
```

`~/.codex/skills/` 下应出现 `sci-logic-narrative-review/`，结构与本机其它技能一致：

```
sci-logic-narrative-review/
├── SKILL.md
├── manifest.yaml          # DSH 专用，Codex 忽略
├── agents/openai.yaml     # 本平台的可选元数据
├── core/ references/ assets/ scripts/
```

## 三、怎么用

直接说：

- 「用 SCI逻辑叙事审查 审一下这篇稿」
- 「投稿前查一遍，审稿人会打哪里」

也可以用 `$sci-logic-narrative-review` 显式调用。

首轮需要：**稿件 + 图表图注 + 目标期刊**；要完整双轨比对还需**实验台账**。

## 四、本平台特性

- **初始技能列表有 token 预算**：默认约上下文窗口的 2%（未知窗口时 8000 字符）。装了很多技能时，Codex 会先压缩描述、必要时省略部分技能。技能多时可用 `skills.max_context_tokens` 调整（上限 10000）。
- **`agents/openai.yaml`** 提供展示名「SCI逻辑叙事审查」、短描述、默认提示词与调用策略；只对读取该文件的产品生效，不影响其它宿主。
- 技能被选中后会读 `SKILL.md` 全文，之后按需读 `core/`——与 Claude / DSH 的渐进披露一致。

## 五、常见问题

**Q：`~/.agents/skills` 里放了但 Codex 没发现？**
A：新版 Codex 以 `~/.codex/skills/` 为主。请放到该目录，或用 `[[skills.config]]` 显式指向。

**Q：改了 config.toml 没反应？**
A：必须重启 Codex。

**Q：`check_manifest.py` 报错要管吗？**
A：它校验的是 DeepSeek Harness 的装载表。`check_platforms.py` 通过即可，`check_manifest.py` 在 Codex 下仅供参考。
