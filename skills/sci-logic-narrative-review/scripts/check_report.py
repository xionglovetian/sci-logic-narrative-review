#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""审稿报告完整性校验器（sci-logic-narrative-review skill）。

只做一件事：检查一份报告是否满足 core/report-contract.md 的硬性契约。
它不评价审查质量，只抓"漏项、占位符残留、字段缺失、路径与结论自相矛盾"。

用法：
    python check_report.py <报告路径>
    python check_report.py <报告路径> --json
    python check_report.py <报告路径> --allow-placeholders   # 允许模板未填完（草稿模式）

退出码：
    0  通过（可能含警告）
    1  不合格（存在违规项）
    2  文件读不到或不是 UTF-8 文本
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------- 契约定义

META_FIELDS = [
    "审查对象",
    "审查轮次",
    "审查日期",
    "目标期刊",
    "输入完整度",
    "审查范围",
    "路径判定",
    "预估结果",
]

REQUIRED_SECTIONS = [
    (1, "判决摘要"),
    (2, "致命项"),
    (3, "评分表"),
    (4, "漏洞卡片"),
    (5, "数字核验表"),
    (6, "声称强度越级"),
    (7, "正面资产"),
    (8, "路径判定理由"),
    (9, "下一步顺序"),
    (11, "本轮边界声明"),
]

CARD_FIELDS = [
    "类别",
    "严重度",
    "定位",
    "证据",
    "审稿人原话",
    "为什么有问题",
    "修改处方",
    "复审判据",
]

VALID_SEVERITY = {"P0", "P1", "P2", "P3"}
VALID_PATH = {"P-A", "P-B", "P-C"}
VALID_RESULT = {"大修", "中修", "小修", "必拒", "无法判定", "拒稿"}
VALID_COMPLETENESS = {"G0", "G1", "G2"}
VALID_VERDICT = {"一致", "一致（需注明口径）", "不一致", "未找到来源"}

# 路径 -> 允许的预估结果（P-C 不能配小修/中修）
PATH_RESULT_COMPAT = {
    "P-A": {"大修", "中修"},
    "P-B": {"中修", "小修", "大修"},
    "P-C": {"必拒", "拒稿", "无发判定", "无法判定"},
}

# 禁止出现的软化/不可执行表述（core/report-contract.md 第八节）
FORBIDDEN_PHRASES = [
    "整体质量不错",
    "整体不错",
    "建议润色",
    "基本符合发表要求",
    "想必作者也意识到了",
    "建议补充更多实验",
    "data looks fine",
    "看起来很合理",
]

PLACEHOLDER_RE = re.compile(r"<[^<>\n]{0,120}>")
CARD_RE = re.compile(r"^###\s*\[?(V-\d{2,})\]?\s*(.*)$", re.MULTILINE)


def _force_utf8_stdout() -> None:
    """Windows 控制台默认 GBK，中文输出会变成乱码。优先切 UTF-8，失败则静默降级。"""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
        except (AttributeError, OSError, ValueError):
            pass


class Report:
    def __init__(self, text: str, path: Path) -> None:
        self.text = text
        self.path = path
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.stats: dict[str, object] = {}

    # ---------------------------------------------------------- 工具方法
    def err(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def has(self, needle: str) -> bool:
        return needle in self.text

    # ---------------------------------------------------------- 各项检查
    def check_placeholders(self, allow: bool) -> None:
        found = PLACEHOLDER_RE.findall(self.text)
        # 只把"看起来像待填字段"的尖括号当占位符：包含中文、冒号、竖线或 ≤ 空
        real = [f for f in found if "https://" not in f and "http://" not in f]
        self.stats["占位符残留"] = len(real)
        if real and not allow:
            sample = "、".join(real[:5])
            self.err(f"存在 {len(real)} 处未填写的占位符（示例：{sample}）")

    def check_meta(self) -> None:
        missing = [f for f in META_FIELDS if f not in self.text]
        if missing:
            self.err(f"元信息缺字段：{'、'.join(missing)}")
        self.stats["元信息字段数"] = len(META_FIELDS) - len(missing)

    def check_sections(self) -> None:
        missing = []
        for num, name in REQUIRED_SECTIONS:
            # 兼容 "## 一、判决摘要" / "## 1. 判决摘要" / "## 一 判决摘要" 等写法
            pat = re.compile(rf"^#+\s*[一二三四五六七八九十\d]*\s*[、.．]?\s*{re.escape(name)}", re.MULTILINE)
            if not pat.search(self.text):
                missing.append(f"{num}. {name}")
        if missing:
            self.err(f"缺必需章节：{'；'.join(missing)}")
        self.stats["必需章节覆盖"] = f"{len(REQUIRED_SECTIONS) - len(missing)}/{len(REQUIRED_SECTIONS)}"

    def parse_path_and_result(self) -> tuple[str | None, str | None]:
        path = None
        result = None
        m = re.search(r"路径判定[^\n]*", self.text)
        if m:
            line = m.group(0)
            for code in ("P-A", "P-B", "P-C"):
                if code in line:
                    path = code
                    break
        m = re.search(r"预估结果[^\n]*", self.text)
        if m:
            line = m.group(0)
            for word in ("大修", "中修", "小修", "必拒", "拒稿", "无法判定"):
                if word in line:
                    result = word
                    break
        return path, result

    def check_path_consistency(self) -> None:
        path, result = self.parse_path_and_result()
        self.stats["路径判定"] = path or "未识别"
        self.stats["预估结果"] = result or "未识别"
        if path is None:
            self.err("无法从'路径判定'行识别 P-A / P-B / P-C")
        if result is None:
            self.err("无法从'预估结果'行识别 大修/中修/小修/必拒/无法判定")
        if path and result:
            allowed = PATH_RESULT_COMPAT.get(path, set())
            normalized = "必拒" if result in {"拒稿", "无发判定"} else result
            if normalized not in allowed:
                self.err(
                    f"路径与预估结果自相矛盾：{path} 不应配「{result}」"
                    f"（允许：{'、'.join(sorted(allowed))}）"
                )

    def check_cards(self) -> None:
        blocks = CARD_RE.split(self.text)
        # split 结果为 [前言, 编号1, 标题1, 正文1, 编号2, ...]
        cards = []
        i = 1
        while i + 2 <= len(blocks) - 1:
            cards.append((blocks[i], blocks[i + 1], blocks[i + 2]))
            i += 3

        self.stats["漏洞卡片数"] = len(cards)
        if not cards:
            self.err("没有任何漏洞卡片（V-xx）。报告契约要求至少 1 张 P1 或 P2 卡片")
            return

        severities: list[str] = []
        for cid, title, body in cards:
            if not title.strip():
                self.err(f"{cid} 卡片的标题为空（应为一句话说清问题）")
            for field in CARD_FIELDS:
                if field not in body:
                    self.err(f"{cid} 缺少字段「{field}」")
            sev = re.search(r"严重度[^\n]*", body)
            if sev is None:
                severities.append("?")
                continue
            line = sev.group(0)
            hit = next((s for s in ("P0", "P1", "P2", "P3") if s in line), None)
            severities.append(hit or "?")
            if hit is None:
                self.err(f"{cid} 的严重度未写成 P0/P1/P2/P3")
            # 定位必须是"章节 + 引文"，至少包含一个定位符号
            loc = re.search(r"定位[^\n]*", body)
            if loc is None:
                self.err(f"{cid} 缺「定位」行")
            else:
                line = loc.group(0)
                if not re.search(r"[§#]|Tab|Table|Fig|图\s*\d|表\s*\d|Supp|摘要|引言|讨论|结果|结论", line):
                    self.warn(f"{cid} 的定位行缺少章节/图表锚点，可能写不出可复核位置")

        self.stats["严重度分布"] = {s: severities.count(s) for s in sorted(set(severities))}
        if "?" in severities:
            self.err("有卡片的严重度无法识别，必须写成 P0/P1/P2/P3")
        elif not any(s in {"P0", "P1", "P2"} for s in severities):
            self.err("全部卡片都是 P3：契约要求至少一条 P1/P2（零漏洞不可能）")

    def check_number_table(self) -> None:
        m = re.search(r"^#+.*数字核验表.*$", self.text, re.MULTILINE)
        if not m:
            return
        tail = self.text[m.end():]
        # 截到下一个同级或更高级标题
        nxt = re.search(r"^#+ ", tail, re.MULTILINE)
        section = tail[: nxt.start()] if nxt else tail
        rows = [ln for ln in section.splitlines() if ln.strip().startswith("|")]
        data_rows = [ln for ln in rows if not re.search(r"稿件值|^\|\s*[-:| ]+\|?\s*$", ln)]
        # 去掉表头行
        data_rows = [ln for ln in data_rows if not re.search(r"结论\s*\|", ln)]
        self.stats["数字核验行数"] = len(data_rows)
        if len(data_rows) < 8:
            self.err(f"数字核验表只有 {len(data_rows)} 行，契约要求 ≥ 8 行")

        bad = []
        for ln in data_rows:
            if not any(v in ln for v in VALID_VERDICT):
                bad.append(ln.strip()[:40])
        if bad:
            self.err(f"数字核验表有 {len(bad)} 行结论不在四选一取值内（示例：{bad[0]}）")

    def check_target_sections(self) -> None:
        # 第一节判决摘要须 5 行内可读完
        m = re.search(r"^#+.*判决摘要.*$", self.text, re.MULTILINE)
        if m:
            tail = self.text[m.end():]
            nxt = re.search(r"^#+ ", tail, re.MULTILINE)
            section = tail[: nxt.start()] if nxt else tail
            bullets = [ln for ln in section.splitlines() if ln.strip()]
            self.stats["判决摘要行数"] = len(bullets)
            if len(bullets) > 8:
                self.warn(f"判决摘要段有 {len(bullets)} 行，超过'5 行内读完'的意图")

    def check_edge_declaration(self) -> None:
        m = re.search(r"^#+.*本轮边界声明.*$", self.text, re.MULTILINE)
        if not m:
            return
        tail = self.text[m.end():]
        nxt = re.search(r"^#+ ", tail, re.MULTILINE)
        section = tail[: nxt.start()] if nxt else tail
        for key in ("覆盖", "未覆盖", "不适用"):
            if key not in section:
                self.err(f"本轮边界声明缺「{key}」项")

    def check_forbidden(self) -> None:
        hits = [p for p in FORBIDDEN_PHRASES if p in self.text]
        if hits:
            self.err(f"出现被禁的软化/不可执行表述：{'、'.join(hits)}")

    def check_round(self) -> None:
        m = re.search(r"审查轮次[^\n]*", self.text)
        if not m:
            return
        line = m.group(0)
        r = re.search(r"r(\d+)", line)
        if r is None:
            self.err("审查轮次未写成 r<N> 格式")
            return
        n = int(r.group(1))
        self.stats["轮次"] = n
        if n > 1 and "闭环差分" not in self.text and "差分" not in self.text:
            self.err(f"第 {n} 轮缺「上轮漏洞闭环差分表」")

    def check_filename(self, strict_name: bool = True) -> None:
        name = self.path.name
        if re.match(r"审稿报告_SCI逻辑叙事审查_\d{8}_r\d+\.md$", name):
            self.stats["文件名检查"] = "合规"
            return
        if strict_name:
            self.warn(f"文件名不符合约定（应为 审稿报告_SCI逻辑叙事审查_YYYYMMDD_rN.md）：{name}")
        else:
            self.stats["文件名检查"] = "已跳过（--any-filename）"

    # ---------------------------------------------------------- 主流程
    def run(self, allow_placeholders: bool, strict_name: bool = True) -> int:
        self.check_filename(strict_name)
        self.check_placeholders(allow_placeholders)
        self.check_meta()
        self.check_sections()
        self.check_path_consistency()
        self.check_cards()
        self.check_number_table()
        self.check_target_sections()
        self.check_edge_declaration()
        self.check_forbidden()
        self.check_round()
        return 0 if not self.errors else 1


def main(argv: list[str]) -> int:
    _force_utf8_stdout()
    ap = argparse.ArgumentParser(description="校验 sci-logic-narrative-review 审稿报告是否满足契约")
    ap.add_argument("report", help="报告文件路径")
    ap.add_argument("--json", action="store_true", help="以 JSON 输出结果")
    ap.add_argument(
        "--allow-placeholders",
        action="store_true",
        help="草稿模式：允许 <...> 占位符残留（用于模板初填阶段）",
    )
    ap.add_argument(
        "--any-filename",
        action="store_true",
        help="跳过文件名约定检查（用于检查示例/演示报告，如 examples/demo-report.md）",
    )
    args = ap.parse_args(argv)

    path = Path(args.report).expanduser()
    if not path.is_file():
        print(f"[FAIL] 找不到文件：{path}", file=sys.stderr)
        return 2
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        print(f"[FAIL] 不是 UTF-8 文本：{path}", file=sys.stderr)
        return 2

    report = Report(text, path)
    code = report.run(args.allow_placeholders, strict_name=not args.any_filename)

    if args.json:
        print(
            json.dumps(
                {
                    "ok": code == 0,
                    "file": str(path),
                    "errors": report.errors,
                    "warnings": report.warnings,
                    "stats": report.stats,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return code

    print(f"报告：{path.name}")
    print("-" * 60)
    for key, value in report.stats.items():
        print(f"  {key}: {value}")
    print("-" * 60)
    if report.errors:
        print(f"[FAIL] {len(report.errors)} 项违规：")
        for i, msg in enumerate(report.errors, 1):
            print(f"  {i}. {msg}")
    if report.warnings:
        print(f"[WARN] {len(report.warnings)} 项提醒：")
        for i, msg in enumerate(report.warnings, 1):
            print(f"  {i}. {msg}")
    if code == 0:
        print("[PASS] 报告满足契约")
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
