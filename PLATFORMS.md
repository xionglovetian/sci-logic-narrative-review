# 平台支持：Claude Code / Codex / DeepSeek Harness

这套 skill 遵循 [Agent Skills 开放标准](https://agentskills.io/)（`SKILL.md` + `name` / `description` frontmatter），所以**一份技能目录，四端通用**。差别只在"怎么装进去"和"插件清单长什么样"。

| 平台 | 读取的技能格式 | 本仓库提供的清单 |
|---|---|---|
| **Claude Code** | `SKILL.md`（Agent Skills） | `.claude-plugin/plugin.json` + `.claude-plugin/marketplace.json` |
| **Codex**（CLI / IDE / 桌面版） | `SKILL.md`（Agent Skills） | 根目录 `plugin.json`（Agent Plugins schema）+ `.agents/plugins/marketplace.json` |
| **DeepSeek Harness (DSH)** | `SKILL.md` + 声明式 `manifest.yaml` | 技能目录内的 `manifest.yaml`（其它宿主自动忽略） |
| **其它 / 通用 Agent** | 读根目录 `AGENTS.md` | 仓库根 `AGENTS.md`（单文件全量摘要） |

---

## 一、Claude Code

### 方式 A：作为技能直接装（最简单，推荐）

Claude Code 会把 `~/.claude/skills/<name>/SKILL.md` 视为全局技能，在所有项目可用。

```bash
git clone https://github.com/xionglovetian/sci-logic-narrative-review.git
mkdir -p ~/.claude/skills
cp -r sci-logic-narrative-review/skills/sci-logic-narrative-review ~/.claude/skills/
```

项目级（只在本仓库可用）：

```bash
mkdir -p /你的项目/.claude/skills
cp -r sci-logic-narrative-review/skills/sci-logic-narrative-review /你的项目/.claude/skills/
```

Windows PowerShell：

```powershell
git clone https://github.com/xionglovetian/sci-logic-narrative-review.git
New-Item -ItemType Directory -Force "$env:USERPROFILE\.claude\skills" | Out-Null
Copy-Item -Recurse -Force "sci-logic-narrative-review\skills\sci-logic-narrative-review" "$env:USERPROFILE\.claude\skills\"
```

### 方式 B：作为插件安装（走 marketplace）

本仓库本身就是一个 Claude Code marketplace。在 Claude Code 里：

```
/plugin marketplace add xionglovetian/sci-logic-narrative-review
/plugin install sci-logic-narrative-review@sci-logic-narrative-review-marketplace
```

或直接从克隆下来的目录加载（开发调试用）：

```bash
claude --plugin-dir ./sci-logic-narrative-review
```

### 自检

```bash
claude plugin validate .            # 应输出 Validation passed
claude plugin validate . --strict   # 不应有 warning
```

安装后可用 `/plugin` 的 **Installed** 标签确认，或用 `claude plugin details sci-logic-narrative-review` 看组件清单与 token 成本。

---

## 二、Codex

Codex 的独立技能放 `~/.codex/skills/<name>/SKILL.md`（也可用 `config.toml` 的 `[[skills.config]]` 指向任意路径）。

### 方式 A：装成独立技能

```bash
git clone https://github.com/xionglovetian/sci-logic-narrative-review.git
mkdir -p ~/.codex/skills
cp -r sci-logic-narrative-review/skills/sci-logic-narrative-review ~/.codex/skills/
```

```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\.codex\skills" | Out-Null
Copy-Item -Recurse -Force "sci-logic-narrative-review\skills\sci-logic-narrative-review" "$env:USERPROFILE\.codex\skills\"
```

或者在 `~/.codex/config.toml` 里显式登记（推荐，便于开关）：

```toml
[[skills.config]]
path = "C:/path/to/sci-logic-narrative-review/skills/sci-logic-narrative-review/SKILL.md"
enabled = true
```

改完 `config.toml` 需要重启 Codex。

### 方式 B：装成插件

本仓库根目录的 `plugin.json` 是 Agent Plugins 清单，`skills/` 是插件内的技能目录，`.agents/plugins/marketplace.json` 是本仓库的 marketplace 目录。

```bash
codex plugin marketplace add xionglovetian/sci-logic-narrative-review
codex plugin marketplace list
```

插件在 `config.toml` 里以 `插件名@市场名` 形式启用：

```toml
[plugins."sci-logic-narrative-review@sci-logic-narrative-review"]
enabled = true
```

> 说明：Codex 的插件安装面主要在 ChatGPT 桌面版（Plugins 目录）。CLI 侧用方式 A 最稳。

### 可选元数据

`skills/sci-logic-narrative-review/agents/openai.yaml` 提供展示名、短描述、默认提示词与调用策略（`allow_implicit_invocation`），只对读取该文件的产品生效，不影响其它宿主。

---

## 三、DeepSeek Harness (DSH)

DSH 支持**渐进披露**：先读 `SKILL.md` 的 `name` / `description`，按需再读 `manifest.yaml` 指定的文件。这正是本 skill 的原始形态。

```bash
# 用户级（所有项目可用）
mkdir -p ~/.agents/skills
cp -r sci-logic-narrative-review/skills/sci-logic-narrative-review ~/.agents/skills/
```

```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\.agents\skills" | Out-Null
Copy-Item -Recurse -Force "sci-logic-narrative-review\skills\sci-logic-narrative-review" "$env:USERPROFILE\.agents\skills\"
```

项目级：放到 `<项目>/.dsh/skills/` 或 `<项目>/.agents/skills/`，DSH 会自动发现。

`manifest.yaml` 只有 DSH 会读；Claude Code 与 Codex 忽略它，不影响加载。

---

## 四、通用 Agent / 无插件宿主

任何"能读文件"的 agent 都能用：

1. 让它读仓库根目录的 [`AGENTS.md`](AGENTS.md)（全量摘要，含六镜头、判定标准、报告契约）；
2. 需要细节时，让它读 `skills/sci-logic-narrative-review/SKILL.md` 及其 `core/` 下文件。

---

## 五、四个平台的差异对照

| 维度 | Claude Code | Codex | DSH |
|---|---|---|---|
| 技能发现 | `~/.claude/skills/`、插件 `skills/` | `~/.codex/skills/`、`[[skills.config]]`、插件 `skills/` | `.dsh/skills/`、`~/.agents/skills/`、`.agents/skills/` |
| 清单文件 | `.claude-plugin/plugin.json` | 根 `plugin.json`（`.codex-plugin/plugin.json` 为兼容回退） | 技能内 `manifest.yaml` |
| 市场目录 | `.claude-plugin/marketplace.json` | `.agents/plugins/marketplace.json` | 无（直接放目录） |
| 渐进披露 | 支持（`SKILL.md` → 按需读） | 支持（初始列表有 token 预算） | 支持（`manifest.yaml` 装载表） |
| 显示名来源 | `displayName` 或 marketplace 条目 | `agents/openai.yaml` 的 `interface.display_name` | `description` 首段 |
| 校验手段 | `claude plugin validate` | `plugin-creator` / 手动核对 | `scripts/check_manifest.py` |

## 六、一致的产出契约（平台无关）

无论在哪端运行，产出都是同一份报告，落在稿件目录下：

```
审稿报告_SCI逻辑叙事审查_YYYYMMDD_rN.md
```

并用同一个校验器自检（纯标准库，三端都能跑）：

```bash
python skills/sci-logic-narrative-review/scripts/check_report.py <报告.md>
```

## 七、已知限制

- 本 skill 的正文与报告模板是**中文**；英文稿件照样能审，报告用中文写（用户可要求英文输出）。
- Claude Code 的插件 token 成本可在 `/plugin` 的 **Context cost** 里看到；本 skill 只有一份技能，成本很低。
- Codex 如果安装了很多技能，初始技能列表有预算限制（默认约 2% 上下文），必要时用 `skills.max_context_tokens` 调整。
- `check_manifest.py` 只校验 DSH 的装载表；在 Claude / Codex 下它不影响加载。
