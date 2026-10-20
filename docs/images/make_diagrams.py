#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成两张架构图 SVG：工作流程 + 文件架构。

不依赖第三方库，直接拼 SVG 文本。字体用系统 sans + 中文字体回退。
"""

from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(r"C:\Users\ASUS\Desktop\PFRPN\_publish_skill\docs\images")

# ---------------- 主题 ----------------
BG = "#0d1117"
PANEL = "#161b22"
PANEL2 = "#1c2330"
LINE = "#30363d"
FG = "#e6edf3"
DIM = "#9aa7b4"
ACCENT = "#58a6ff"
GREEN = "#7ee787"
WARN = "#ffa657"
DANGER = "#ff7b72"
PURPLE = "#d2a8ff"

FONT = "'Segoe UI','Noto Sans SC','PingFang SC','Microsoft YaHei',Helvetica,Arial,sans-serif"
MONO = "'Cascadia Code','Consolas','Liberation Mono',monospace"


def head(w: int, h: int, title: str) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'font-family="{FONT}" role="img" aria-label="{escape(title)}">',
        f"<title>{escape(title)}</title>",
        "<defs>",
        '<marker id="arw" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        f'<path d="M0,0 L10,5 L0,10 z" fill="{DIM}"/></marker>',
        '<marker id="arwA" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        f'<path d="M0,0 L10,5 L0,10 z" fill="{ACCENT}"/></marker>',
        '<marker id="arwG" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        f'<path d="M0,0 L10,5 L0,10 z" fill="{GREEN}"/></marker>',
        "<style>",
        f".t{{fill:{FG}}} .d{{fill:{DIM}}} .mk{{font-family:{MONO}}}",
        "text{dominant-baseline:middle}",
        "</style>",
        "</defs>",
        f'<rect width="{w}" height="{h}" rx="14" fill="{BG}"/>',
    ]


def foot() -> list[str]:
    return ["</svg>"]


def box(x, y, w, h, *, fill=PANEL, stroke=LINE, rx=11, sw=1.4, dash=None) -> str:
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" '
        f'stroke="{stroke}" stroke-width="{sw}"{d}/>'
    )


def text(x, y, s, *, size=14, color=FG, anchor="start", weight="400", mono=False, opacity=None) -> str:
    cls = ' class="mk"' if mono else ""
    op = f' opacity="{opacity}"' if opacity else ""
    return (
        f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}" '
        f'font-weight="{weight}"{cls}{op}>{escape(s)}</text>'
    )


def badge_width(s: str, *, size=11.5, padx=8) -> int:
    """按 ASCII/CJK 加权估算徽章宽度。"""
    wsum = sum(1.0 if ord(ch) > 0x2E80 else 0.58 for ch in s)
    return int(wsum * size) + padx * 2


def badge(x, y, s, *, color=ACCENT, size=11.5, padx=8, h=20) -> tuple[str, int]:
    w = badge_width(s, size=size, padx=padx)
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h/2}" fill="none" stroke="{color}" '
        f'stroke-width="1.2" opacity="0.85"/>'
        + text(x + w / 2, y + h / 2 + 0.5, s, size=size, color=color, anchor="middle"),
        w,
    )


def arrow(x1, y1, x2, y2, *, color=DIM, marker="arw", dash=None, sw=1.6) -> str:
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (
        f'<path d="M{x1},{y1} L{x2},{y2}" stroke="{color}" stroke-width="{sw}" fill="none" '
        f'marker-end="url(#{marker})"{d}/>'
    )


def path_arrow(points: list[tuple[float, float]], *, color=DIM, marker="arw", dash=None, sw=1.6) -> str:
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{'M' if i == 0 else 'L'}{px},{py}" for i, (px, py) in enumerate(points))
    return f'<path d="{pts}" stroke="{color}" stroke-width="{sw}" fill="none" marker-end="url(#{marker})"{d}/>'


# =====================================================================
# 图 1：工作流程全景
# =====================================================================

def build_workflow() -> str:
    W, H = 1160, 986
    out = head(W, H, "SCI逻辑叙事审查 工作流程架构图")

    # 标题
    out.append(text(36, 46, "SCI逻辑叙事审查 · 工作流程架构", size=23, weight="700"))
    out.append(text(36, 74, "从收料 → 分级 → 七步审查 → 三路径判定 → 报告交付 → 自检回环", size=13.5, color=DIM))

    # ---------------- 左列：七步 ----------------
    LX, LW = 36, 620
    PANEL_H = 724
    out.append(box(LX, 104, LW, PANEL_H, fill="#10161f", stroke=LINE, rx=14))
    out.append(text(LX + 20, 130, "审查执行：七步（产物缺一即未完成）", size=14, color=ACCENT, weight="700"))

    steps = [
        ("输入盘点与缺口分级", "稿件 · 图表 · 台账 · 期刊 → 判定 G0 / G1 / G2", ACCENT, "定位索引"),
        ("L1–L2 故事链前置", "缺口是否成立 → 方案是否逐条对症", GREEN, "短路规则"),
        ("L3 因果闭环", "主对比 / 等容量控制对照 / 泛化鲁棒（三层）", WARN, "最耗时"),
        ("L4–L6 结构性审查", "贡献三处摆放 · 图表分层 · 边界自限", PURPLE, ""),
        ("双轨比对", "数字轨 · 声称轨 · 口径轨（稿件 vs 台账）", ACCENT, "不可跳过"),
        ("评分与路径判定", "七维加权 + 六类致命项硬阈值 → P-A/P-B/P-C", DANGER, "先查阈值"),
        ("生成报告并自检", "填模板 → 落盘 → 跑校验器（自检不过不算完成）", GREEN, ""),
    ]

    # 徽章统一左边缘：先算所有徽章最大宽度，保证视觉对齐
    chip_w_max = max([badge_width(s[3], size=11) for s in steps if s[3]], default=0)

    sy = 150
    sh = 92
    gap = 6
    for i, (title, desc, col, chip) in enumerate(steps):
        y = sy + i * (sh + gap)
        out.append(box(LX + 20, y, LW - 40, sh, fill=PANEL, stroke=col))
        out.append(f'<rect x="{LX+20}" y="{y}" width="5" height="{sh}" rx="2.5" fill="{col}"/>')
        cx, cy = LX + 56, y + sh / 2
        out.append(f'<circle cx="{cx}" cy="{cy}" r="15" fill="{PANEL2}" stroke="{col}" stroke-width="1.4"/>')
        out.append(text(cx, cy + 1, str(i + 1), size=15, color=col, anchor="middle", weight="700"))
        out.append(text(LX + 84, y + 30, title, size=15.5, weight="600"))
        out.append(text(LX + 84, y + 56, desc, size=12.8, color=DIM))
        if chip:
            # 统一左边缘 + 右留白，且不压右边框
            out.append(badge(LX + LW - 20 - 30 - chip_w_max, y + 12, chip, color=col, size=11)[0])
        if i < len(steps) - 1:
            out.append(arrow(LX + 56, y + sh, LX + 56, y + sh + gap - 1, color=LINE))

    # ---------------- 右上：输入与产出 ----------------
    RX = 690
    RW = 434
    # 输入
    out.append(box(RX, 104, RW, 132, fill="#10161f", stroke=LINE, rx=14))
    out.append(text(RX + 18, 128, "输入（轨 A 稿件 / 轨 B 证据）", size=13.5, color=ACCENT, weight="700"))
    ins = ["稿件正文", "图表与图注", "实验台账", "目标期刊"]
    for i, s in enumerate(ins):
        bx = RX + 18 + (i % 2) * 205
        by = 146 + (i // 2) * 42
        out.append(box(bx, by, 190, 32, fill=PANEL2, stroke=LINE, rx=8))
        out.append(text(bx + 12, by + 17, s, size=12.8, color=FG))
    out.append(arrow(RX + RW / 2, 236, RX + RW / 2, 262, color=ACCENT, marker="arwA"))
    out.append(text(RX + RW / 2 + 10, 250, "无台账 → P0 无证据底座，禁止 P-A", size=11.5, color=WARN))

    # 判定
    out.append(box(RX, 266, RW, 150, fill="#10161f", stroke=LINE, rx=14))
    out.append(text(RX + 18, 290, "路径判定（三选一，须排除另两条）", size=13.5, color=DANGER, weight="700"))
    verdicts = [
        ("P-A", "方法创新型", "等容量对照明显弱 → 大修后接收", GREEN),
        ("P-B", "评估认知型", "对照缺失/微弱但缺口真 → 中修可接受", ACCENT),
        ("P-C", "证据不足", "无对照却称因果 / 数字不可溯源 → 拒稿", DANGER),
    ]
    for i, (code, name, desc, col) in enumerate(verdicts):
        y = 306 + i * 35
        out.append(box(RX + 18, y, RW - 36, 30, fill=PANEL2, stroke=col, rx=8, sw=1.2))
        out.append(text(RX + 30, y + 15, code, size=12.5, color=col, weight="700", mono=True))
        out.append(text(RX + 74, y + 15, name, size=12.5, color=FG, weight="600"))
        out.append(text(RX + 152, y + 15.5, desc, size=11.4, color=DIM))

    out.append(arrow(RX + RW / 2, 416, RX + RW / 2, 440, color=DANGER))

    # 报告
    out.append(box(RX, 444, RW, 156, fill="#10161f", stroke=GREEN, rx=14, sw=1.6))
    out.append(text(RX + 18, 468, "报告交付（每轮一份 · 强制）", size=13.5, color=GREEN, weight="700"))
    parts = [
        "判决摘要 + 致命项清单",
        "评分表（A–F 合计 − G 扣分）",
        "漏洞卡片 V-xx（八字段 · 带定位）",
        "数字核验表（≥8 行）",
        "声称强度越级清单",
        "处方 + 复审判据 + 下一步顺序",
    ]
    for i, s in enumerate(parts):
        out.append(text(RX + 26, 492 + i * 19, "▪ " + s, size=12.2, color="#c9d4e0"))

    # 自检回环
    out.append(arrow(RX + RW / 2, 600, RX + RW / 2, 622, color=GREEN, marker="arwG"))
    out.append(box(RX + 40, 624, RW - 80, 54, fill=PANEL2, stroke=GREEN, rx=10, dash="5 4"))
    out.append(text(RX + RW / 2, 644, "check_report.py 契约自检 · 12 类硬性项", size=12.4, color=GREEN, anchor="middle", weight="600"))
    out.append(text(RX + RW / 2, 662, "不过 → 补报告；通过 → 交付", size=11.3, color=DIM, anchor="middle"))

    # 回环：自检 → 下一轮（贴最右缘，标签左置避免裁切）
    LOOPX = 1148
    out.append(path_arrow(
        [(RX + RW - 40, 651), (LOOPX, 651), (LOOPX, 118), (RX + RW - 2, 118)],
        color=GREEN, marker="arwG", dash="6 5",
    ))
    out.append(text(LOOPX - 30, 470, "下一轮", size=11, color=GREEN, anchor="end", opacity="0.9"))
    out.append(text(LOOPX - 30, 486, "闭环差分", size=11, color=GREEN, anchor="end", opacity="0.9"))

    # 左栏 → 判定的入口箭头（走空白走廊，不压回环与标签）
    CORR = 680
    out.append(path_arrow(
        [(LX + LW - 2, 500), (CORR, 500), (CORR, 380), (RX - 2, 380)],
        color=ACCENT, marker="arwA",
    ))
    out.append(text(CORR + 11, 480, "判定", size=11.5, color=ACCENT))

    # ---------------- 底部：六个镜头 ----------------
    out.append(box(36, 848, 1088, 110, fill="#10161f", stroke=LINE, rx=14))
    out.append(text(56, 872, "六个审查镜头（顺序不可颠倒，后者依赖前者）", size=13.5, color=ACCENT, weight="700"))
    lenses = [
        ("L1", "缺口真实性", ACCENT),
        ("L2", "方案对症性", GREEN),
        ("L3", "因果闭环", WARN),
        ("L4", "贡献可分性", PURPLE),
        ("L5", "图表分层", ACCENT),
        ("L6", "边界自限", GREEN),
    ]
    lw = 158
    for i, (code, name, col) in enumerate(lenses):
        bx = 56 + i * (lw + 14)
        out.append(box(bx, 890, lw, 50, fill=PANEL, stroke=col, rx=9, sw=1.3))
        out.append(text(bx + 14, 915, code, size=13, color=col, weight="700", mono=True))
        out.append(text(bx + 44, 915, name, size=13, weight="600"))
        if i < len(lenses) - 1:
            out.append(f'<path d="M{bx+lw+1},{915} L{bx+lw+12},{915}" stroke="{LINE}" stroke-width="1.6"/>')
            out.append(f'<path d="M{bx+lw+12},{911} l5,4 l-5,4" fill="none" stroke="{LINE}" stroke-width="1.6"/>')

    out.extend(foot())
    return "\n".join(out)


# =====================================================================
# 图 2：文件架构与装载
# =====================================================================

def build_files() -> str:
    W, H = 1160, 720
    out = head(W, H, "SCI逻辑叙事审查 文件架构与装载图")
    out.append(text(36, 46, "文件架构与按需装载", size=23, weight="700"))
    out.append(text(36, 74, "SKILL.md 只做路由；core/ 是判据主体；references/ 按需；assets/ 是模板；scripts/ 强制契约", size=13.5, color=DIM))

    # SKILL.md
    out.append(box(36, 104, 1088, 74, fill=PANEL2, stroke=ACCENT, rx=12, sw=1.8))
    out.append(text(56, 130, "SKILL.md  —  Router", size=17, color=ACCENT, weight="700"))
    out.append(text(56, 154, "流程总览 · 六个镜头 · 双轨比对 · 输出约定 · 纪律红线", size=12.6, color=DIM))
    out.append(text(1104, 132, "用户唯一需要触发的那一层", size=11.5, color=DIM, anchor="end"))
    out.append(text(1104, 152, "manifest.yaml 决定本次装载哪些文件", size=11.5, color=DIM, anchor="end"))

    # 三大分区
    cols = [
        (36, 350, "core/  ·  恒读骨架与判据", GREEN, [
            ("stance.md", "立场 · P0–P3 · 红线"),
            ("flow.md", "七步序列 · 每步产出"),
            ("gap-checklist.md", "七类漏洞 · 60+ 判据"),
            ("rubric.md", "评分 · 硬阈值 · 判定"),
            ("report-contract.md", "报告契约 · 八字段"),
        ]),
        (398, 350, "references/  ·  按需", PURPLE, [
            ("judgment-paths.md", "三路径逐节处方"),
            ("methodology-source.md", "溯源 · 严格度分档"),
            ("input-intake.md", "取料 · 抽样 · 差分"),
        ]),
        (760, 364, "assets/ + scripts/", WARN, [
            ("report-template.md", "报告骨架（必用）"),
            ("example-report.md", "合格样例（校准）"),
            ("check_report.py", "契约自检 · 12 类硬性项"),
            ("check_manifest.py", "装载表完整性校验"),
        ]),
    ]

    for x, w, title, col, items in cols:
        out.append(box(x, 206, w, 250, fill="#10161f", stroke=LINE, rx=12))
        out.append(arrow(x + w / 2, 178, x + w / 2, 202, color=ACCENT, marker="arwA"))
        out.append(text(x + 16, 230, title, size=13.5, color=col, weight="700"))
        for i, (fn, desc) in enumerate(items):
            y = 248 + i * 40
            out.append(box(x + 14, y, w - 28, 32, fill=PANEL, stroke=LINE, rx=8))
            # 文件名在上，说明在下，避免长文件名与右侧说明重叠
            out.append(text(x + 26, y + 11.5, fn, size=11.6, color=FG, weight="600", mono=True))
            out.append(text(x + 26, y + 24.5, desc, size=10.4, color=DIM))

    # 报告落盘
    out.append(box(36, 486, 1088, 88, fill="#10161f", stroke=GREEN, rx=12))
    out.append(text(56, 512, "报告落盘（工作区，不进 skill 目录）", size=13.5, color=GREEN, weight="700"))
    out.append(text(56, 538, "审稿报告_SCI逻辑叙事审查_YYYYMMDD_rN.md", size=14, color=FG, weight="600", mono=True))
    out.append(text(56, 558, "多轮并存不覆盖 · 编号 V-xx 跨轮稳定 · 第二轮起必须附闭环差分表", size=11.8, color=DIM))
    out.append(arrow(560, 456, 560, 482, color=WARN, marker="arw"))

    # 校验回环
    out.append(box(36, 606, 1088, 82, fill=PANEL2, stroke=WARN, rx=12, dash="5 4"))
    out.append(text(56, 632, "自检闸门", size=13.5, color=WARN, weight="700"))
    out.append(text(56, 658, "python scripts/check_report.py <报告>        → 不合格不交付", size=12.4, color=FG, mono=True))
    out.append(text(600, 658, "python scripts/check_manifest.py", size=12.4, color=FG, mono=True))
    out.append(path_arrow([(1080, 574), (1104, 574), (1104, 646), (1118, 646)], color=WARN))
    out.append(text(760, 674, "结构自洽 ≠ 审查质量：契约只降低浅审风险", size=11.2, color=DIM))

    out.extend(foot())
    return "\n".join(out)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    wf = OUT / "workflow.svg"
    fs = OUT / "file-architecture.svg"
    wf.write_text(build_workflow(), encoding="utf-8")
    fs.write_text(build_files(), encoding="utf-8")
    print(f"written: {wf.name} ({wf.stat().st_size} B)")
    print(f"written: {fs.name} ({fs.stat().st_size} B)")


if __name__ == "__main__":
    main()
