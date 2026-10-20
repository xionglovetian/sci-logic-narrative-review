#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""校验 manifest.yaml 的结构完整性（不依赖 PyYAML）。

只认本 skill 用到的 YAML 子集：块映射、块序列、`|` 块标量、普通标量。
检查：顶层必需键、always_load 指向的文件是否存在、stages 每项的必需字段、
stages.values 的取值是否为单行标量、references.on_demand 的 path 是否存在。

用法：python scripts/check_manifest.py
退出码：0 通过 / 1 不合格 / 2 读不到文件
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "manifest.yaml"

REQUIRED_TOP = ["name", "version", "description", "always_load", "stages", "references"]
STAGE_FIELDS = ["detect", "read", "values", "default", "multi"]


def force_utf8() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
        except (AttributeError, OSError, ValueError):
            pass


def load_lines(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    return text.splitlines()


def top_level_keys(lines: list[str]) -> list[str]:
    keys = []
    for ln in lines:
        if not ln or ln.startswith(" ") or ln.startswith("#"):
            continue
        m = re.match(r"^([A-Za-z_][\w\-]*):", ln)
        if m:
            keys.append(m.group(1))
    return keys


def block(lines: list[str], key: str) -> list[str]:
    """返回某个顶层键下的所有行（含缩进的子行）。"""
    out: list[str] = []
    inside = False
    for ln in lines:
        if not inside:
            if re.match(rf"^{re.escape(key)}:", ln):
                inside = True
                out.append(ln)
            continue
        if ln and not ln.startswith(" ") and not ln.startswith("#"):
            break
        out.append(ln)
    return out


def list_items(lines: list[str]) -> list[str]:
    return [m.group(1).strip() for ln in lines if (m := re.match(r"^\s*-\s+(.+)$", ln))]


def stage_names(lines: list[str]) -> list[str]:
    names = []
    stages = block(lines, "stages")
    for ln in stages[1:]:
        m = re.match(r"^  ([A-Za-z_][\w\-]*):\s*$", ln)
        if m:
            names.append(m.group(1))
    return names


def stage_body(lines: list[str], name: str) -> list[str]:
    stages = block(lines, "stages")
    out: list[str] = []
    inside = False
    for ln in stages:
        m = re.match(r"^  ([A-Za-z_][\w\-]*):\s*$", ln)
        if m:
            if inside:
                break
            inside = m.group(1) == name
            if inside:
                out.append(ln)
            continue
        if inside:
            out.append(ln)
    return out


def check_path(rel: str, errors: list[str], where: str) -> None:
    target = (ROOT / rel.strip()).resolve()
    if not target.exists():
        errors.append(f"{where} 指向不存在的文件：{rel}")


def main() -> int:
    force_utf8()
    if not MANIFEST.is_file():
        print(f"[FAIL] 找不到 {MANIFEST}", file=sys.stderr)
        return 2

    lines = load_lines(MANIFEST)
    errors: list[str] = []
    warnings: list[str] = []

    keys = top_level_keys(lines)
    for key in REQUIRED_TOP:
        if key not in keys:
            errors.append(f"缺顶层键：{key}")
    for key in keys:
        if key not in REQUIRED_TOP:
            warnings.append(f"未知顶层键（不会被 SKILL.md 使用）：{key}")

    # always_load
    always = list_items(block(lines, "always_load"))
    if not always:
        errors.append("always_load 为空：审查骨架文件必须恒读")
    for rel in always:
        clean = rel.split("#")[0].strip()
        check_path(clean, errors, "always_load")

    # stages
    names = stage_names(lines)
    if not names:
        errors.append("stages 下没有识别到任何 stage")
    for name in names:
        body = stage_body(lines, name)
        for field in STAGE_FIELDS:
            if not any(re.match(rf"^    {field}:", ln) for ln in body):
                errors.append(f"stage「{name}」缺字段：{field}")
        # read 下的路径必须存在
        in_read = False
        for ln in body:
            if re.match(r"^    read:\s*$", ln):
                in_read = True
                continue
            if in_read:
                if re.match(r"^    \S", ln) and not ln.lstrip().startswith("-"):
                    in_read = False
                    continue
                m = re.match(r"^\s*-\s+(.+)$", ln)
                if m:
                    rel = m.group(1).split("#")[0].strip()
                    if rel:
                        check_path(rel, errors, f"stages.{name}.read")
        # values 里不应出现跨行内容（否则解析易歧义）
        values = block(body, "values")
        for ln in values:
            if ln.strip() and not re.match(r"^\s*(values:|-)\s*", ln) and not re.match(
                r"^\s+[^:]+:\s*\S.*$", ln
            ):
                warnings.append(f"stages.{name}.values 存在可疑行：{ln.strip()[:50]}")

    # references.on_demand
    refs = block(lines, "references")
    on_demand = [ln for ln in refs if re.match(r"^\s*path:", ln)]
    if not on_demand:
        errors.append("references.on_demand 下没有 path 条目")
    for ln in on_demand:
        m = re.match(r"^\s*path:\s*(\S+)", ln)
        if m:
            check_path(m.group(1).split("#")[0], errors, "references.on_demand")

    print(f"manifest: {MANIFEST.name}")
    print("-" * 60)
    print(f"  顶层键: {', '.join(keys)}")
    print(f"  always_load: {len(always)} 项")
    print(f"  stages: {len(names)} 个（{', '.join(names)}）")
    print(f"  on_demand: {len(on_demand)} 项")
    print("-" * 60)
    if errors:
        print(f"[FAIL] {len(errors)} 项违规：")
        for i, msg in enumerate(errors, 1):
            print(f"  {i}. {msg}")
    if warnings:
        print(f"[WARN] {len(warnings)} 项提醒：")
        for i, msg in enumerate(warnings, 1):
            print(f"  {i}. {msg}")
    if not errors:
        print("[PASS] manifest 结构完整，所有引用可达")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
