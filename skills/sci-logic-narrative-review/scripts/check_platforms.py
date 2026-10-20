#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""跨平台清单校验器（Claude Code / Codex / DSH）。

零依赖。检查：
  1. SKILL.md 的 frontmatter 是否满足 Agent Skills 标准（name + description，name 为 kebab-case）
  2. DSH 装载表 manifest.yaml 是否可达（复用逻辑，只在存在时检查）
  3. Claude Code：.claude-plugin/plugin.json + .claude-plugin/marketplace.json
  4. Codex：根 plugin.json（Agent Plugins schema）+ .agents/plugins/marketplace.json
  5. Codex 可选：agents/openai.yaml 的 interface / policy 段

仓库根目录通过「脚本位置向上两级」推断：<root>/skills/<skill>/scripts/check_platforms.py
若该推断不成立（例如脚本被单独拷走），只校验技能目录内的部分并给出提示。

用法：
    python check_platforms.py                 # 自动推断仓库根
    python check_platforms.py --root <path>   # 指定仓库根
    python check_platforms.py --json

退出码：0 通过 / 1 不合格 / 2 找不到技能目录
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SKILL_NAME = "sci-logic-narrative-review"
KEBAB = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def force_utf8() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
        except (AttributeError, OSError, ValueError):
            pass


class Checker:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.notes: list[str] = []
        self.stats: dict[str, object] = {}

    def err(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def note(self, msg: str) -> None:
        self.notes.append(msg)

    # ---------------------------------------------------------------- 工具
    @staticmethod
    def read_json(path: Path, label: str, c: "Checker") -> dict | None:
        try:
            raw = path.read_text(encoding="utf-8")
        except OSError:
            c.err(f"{label}: 读不到文件 {path}")
            return None
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            c.err(f"{label}: JSON 语法错误（{exc}）")
            return None
        if not isinstance(data, dict):
            c.err(f"{label}: 顶层必须是对象")
            return None
        return data

    # ------------------------------------------------------------ SKILL.md
    def check_skill_md(self, skill_dir: Path) -> None:
        sk = skill_dir / "SKILL.md"
        if not sk.is_file():
            self.err(f"缺 SKILL.md：{sk}")
            return
        text = sk.read_text(encoding="utf-8")
        if not text.startswith("---"):
            self.err("SKILL.md 缺 YAML frontmatter（必须以 --- 开头）")
            return
        end = text.find("\n---", 3)
        if end < 0:
            self.err("SKILL.md frontmatter 没有结束标记 ---")
            return
        fm = text[3:end]
        name = re.search(r"^name:\s*(.+)$", fm, re.MULTILINE)
        desc = re.search(r"^description:\s*(.+)$", fm, re.MULTILINE)
        if name is None:
            self.err("SKILL.md frontmatter 缺 name")
        else:
            val = name.group(1).strip().strip("\"'")
            self.stats["skill.name"] = val
            if not KEBAB.match(val):
                self.err(f"SKILL.md 的 name 不是 kebab-case：{val}")
            if val != SKILL_NAME:
                self.warn(f"SKILL.md 的 name 与目录名不一致：{val} vs {SKILL_NAME}")
        if desc is None:
            self.err("SKILL.md frontmatter 缺 description")
        else:
            val = desc.group(1).strip()
            self.stats["skill.description_len"] = len(val)
            if len(val) < 40:
                self.warn("description 偏短，可能不足以触发正确调用")

        # 相对引用是否可达
        for rel in re.findall(r"(?:core|references|assets|scripts)/[A-Za-z0-9_\-]+\.(?:md|py)", text):
            if not (skill_dir / rel).is_file():
                self.err(f"SKILL.md 引用了不存在的文件：{rel}")

    # --------------------------------------------------------------- 技能内
    def check_skill_internals(self, skill_dir: Path) -> None:
        for name in ("core", "references", "assets", "scripts"):
            if not (skill_dir / name).is_dir():
                self.err(f"技能目录缺子目录：{name}/")
        if not (skill_dir / "manifest.yaml").is_file():
            self.warn("技能目录内没有 manifest.yaml（DSH 会退化为只读 SKILL.md）")

    # ------------------------------------------------------------ Claude
    def check_claude(self, root: Path) -> None:
        cdir = root / ".claude-plugin"
        pj = cdir / "plugin.json"
        if not pj.is_file():
            self.err("Claude: 缺 .claude-plugin/plugin.json")
        else:
            data = self.read_json(pj, "Claude plugin.json", self)
            if data:
                self.stats["claude.plugin"] = data.get("name")
                for key in ("name", "version", "description"):
                    if key not in data:
                        self.err(f"Claude plugin.json 缺字段：{key}")
                nm = data.get("name")
                if isinstance(nm, str) and not KEBAB.match(nm):
                    self.err(f"Claude plugin.json 的 name 不是 kebab-case：{nm}")
                if isinstance(nm, str) and re.match(r"^(claude-|anthropic-|anthropics-|cc-plugin-)", nm):
                    self.err(f"Claude 保留名，不能使用：{nm}")
                skills = data.get("skills")
                if skills is None:
                    self.warn("Claude plugin.json 未声明 skills，将依赖默认 skills/ 扫描")
                else:
                    for rel in skills if isinstance(skills, list) else [skills]:
                        target = (root / str(rel)).resolve()
                        if not target.exists():
                            self.err(f"Claude plugin.json 的 skills 路径不存在：{rel}")

        mp = cdir / "marketplace.json"
        if not mp.is_file():
            self.err("Claude: 缺 .claude-plugin/marketplace.json")
        else:
            data = self.read_json(mp, "Claude marketplace.json", self)
            if data:
                if "name" not in data:
                    self.err("Claude marketplace.json 缺 name")
                if "owner" not in data:
                    self.err("Claude marketplace.json 缺 owner")
                if not data.get("description"):
                    self.warn("Claude marketplace.json 缺 description（validate 会给 warning）")
                plugins = data.get("plugins")
                if not isinstance(plugins, list) or not plugins:
                    self.err("Claude marketplace.json 的 plugins 为空")
                else:
                    self.stats["claude.marketplace_plugins"] = len(plugins)
                    for entry in plugins:
                        if not isinstance(entry, dict):
                            continue
                        if "name" not in entry or "source" not in entry:
                            self.err("Claude marketplace 条目缺 name 或 source")
                            continue
                        src = entry["source"]
                        if isinstance(src, str):
                            target = (root / src).resolve()
                            if not target.exists():
                                self.err(f"Claude marketplace 条目 source 不存在：{src}")
                            if not src.startswith("./"):
                                self.warn(f"Claude marketplace 条目 source 建议以 ./ 开头：{src}")

    # -------------------------------------------------------------- Codex
    def check_codex(self, root: Path, skill_dir: Path) -> None:
        pj = root / "plugin.json"
        if not pj.is_file():
            self.err("Codex: 缺根目录 plugin.json")
        else:
            data = self.read_json(pj, "Codex plugin.json", self)
            if data:
                self.stats["codex.plugin"] = data.get("name")
                if "$schema" not in data:
                    self.warn("Codex plugin.json 建议声明 $schema（agent-plugins.org）")
                for key in ("name", "version", "description"):
                    if key not in data:
                        self.err(f"Codex plugin.json 缺字段：{key}")
                nm = data.get("name")
                if isinstance(nm, str) and not KEBAB.match(nm):
                    self.err(f"Codex plugin.json 的 name 不是 kebab-case：{nm}")
                # 便携包从根 skills/ 发现技能，无需 skills 字段；若写了则必须存在
                if "skills" in data:
                    target = root / str(data["skills"])
                    if not target.exists():
                        self.err(f"Codex plugin.json 的 skills 路径不存在：{data['skills']}")
                if not (root / "skills").is_dir():
                    self.err("Codex 便携包要求根目录存在 skills/")

        mp = root / ".agents" / "plugins" / "marketplace.json"
        if not mp.is_file():
            self.warn("Codex: 没有 .agents/plugins/marketplace.json（本地市场不可用，但技能仍可直装）")
        else:
            data = self.read_json(mp, "Codex marketplace.json", self)
            if data:
                if "name" not in data:
                    self.err("Codex marketplace.json 缺 name")
                plugins = data.get("plugins")
                if not isinstance(plugins, list) or not plugins:
                    self.err("Codex marketplace.json 的 plugins 为空")
                else:
                    self.stats["codex.marketplace_plugins"] = len(plugins)
                    for entry in plugins:
                        if not isinstance(entry, dict):
                            continue
                        src = entry.get("source")
                        if isinstance(src, dict) and "path" in src:
                            rel = str(src["path"])
                            if not rel.startswith("./"):
                                self.warn(f"Codex marketplace 的 source.path 建议以 ./ 开头：{rel}")
                            if not (root / rel).resolve().exists():
                                self.err(f"Codex marketplace 的 source.path 不存在：{rel}")
                        else:
                            self.err("Codex marketplace 条目缺 source.path")

        # agents/openai.yaml（可选）
        oy = skill_dir / "agents" / "openai.yaml"
        if oy.is_file():
            text = oy.read_text(encoding="utf-8")
            for section in ("interface:", "policy:"):
                if section not in text:
                    self.warn(f"agents/openai.yaml 缺 {section} 段")
            self.stats["codex.openai_yaml"] = "present"
        else:
            self.note("未提供 agents/openai.yaml（Codex 桌面版不显示自定义名称，不影响功能）")

    # ---------------------------------------------------------------- DSH
    def check_dsh(self, skill_dir: Path) -> None:
        man = skill_dir / "manifest.yaml"
        if not man.is_file():
            return
        text = man.read_text(encoding="utf-8")
        for key in ("name:", "always_load:", "references:"):
            if key not in text:
                self.err(f"manifest.yaml 缺 {key} 段")
        # always_load 指向的文件
        block = re.search(r"^always_load:\s*$(.*?)(?=^\S)", text, re.MULTILINE | re.DOTALL)
        if block:
            for rel in re.findall(r"^\s*-\s+(\S+)", block.group(1), re.MULTILINE):
                rel = rel.split("#")[0].strip()
                if rel and not (skill_dir / rel).is_file():
                    self.err(f"manifest.yaml always_load 指向不存在文件：{rel}")


def main(argv: list[str]) -> int:
    force_utf8()
    ap = argparse.ArgumentParser(description="校验 Claude Code / Codex / DSH 的清单与文件结构")
    ap.add_argument("--root", help="仓库根目录（默认由脚本位置推断）")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    skill_dir = Path(__file__).resolve().parent.parent
    if not skill_dir.is_dir():
        print("[FAIL] 找不到技能目录", file=sys.stderr)
        return 2

    if args.root:
        root = Path(args.root).resolve()
    else:
        candidate = skill_dir.parent.parent
        root = candidate if (candidate / "plugin.json").is_file() or (candidate / "skills").is_dir() else skill_dir

    c = Checker()
    c.check_skill_md(skill_dir)
    c.check_skill_internals(skill_dir)
    c.check_dsh(skill_dir)

    if root != skill_dir:
        c.stats["root"] = str(root)
        c.check_claude(root)
        c.check_codex(root, skill_dir)
    else:
        c.note("未在仓库根上运行：跳过 Claude / Codex 清单校验（用 --root 指定仓库根）")

    code = 0 if not c.errors else 1

    if args.json:
        print(json.dumps({"ok": code == 0, "root": str(root), "errors": c.errors,
                          "warnings": c.warnings, "notes": c.notes, "stats": c.stats},
                         ensure_ascii=False, indent=2))
        return code

    print(f"技能目录：{skill_dir}")
    print(f"仓库根  ：{root}")
    print("-" * 64)
    for k, v in c.stats.items():
        print(f"  {k}: {v}")
    print("-" * 64)
    for label, items in (("FAIL", c.errors), ("WARN", c.warnings), ("NOTE", c.notes)):
        if items:
            print(f"[{label}] {len(items)} 项：")
            for i, msg in enumerate(items, 1):
                print(f"  {i}. {msg}")
    if code == 0:
        print("[PASS] 平台清单与技能结构均合规")
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
