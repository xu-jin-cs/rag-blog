#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_diagrams_p2.py — 博客②《调优实战》配图生成（PNG）。"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

plt.rcParams["font.family"] = ["Hiragino Sans", "PingFang SC", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False

C_BLUE, C_ORANGE, C_GREEN, C_PURPLE, C_RED, C_TEAL = (
    "#2563EB", "#EA580C", "#16A34A", "#9333EA", "#DC2626", "#0891B2")
C_BG = "#f8fafc"
C_BOX = "#1e293b"


def rounded_box(ax, x, y, w, h, text, fc, fs=13, tc="white", weight="bold"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.012",
                                fc=fc, ec="none", mutation_aspect=1.1))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fs, color=tc, weight=weight)


def arrow(ax, x1, y1, x2, y2, color="#64748b", lw=2.2, ls="-"):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", lw=lw,
                                 color=color, linestyle=ls, mutation_scale=20))


# ── 图 4：分片水位标定（碎片率 vs N）─────────────────────────
def diagram_chunking_calibration():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
    fig.patch.set_facecolor(C_BG)
    fig.suptitle("分片水位标定：N 值怎么选（212 篇全语料实测）", fontsize=20, weight="bold", color=C_BOX)

    # 左图：碎片率随 N 变化
    N = np.array([2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30])
    frag = np.array([18.5, 12.3, 8.1, 4.2, 2.1, 1.0, 0.4, 0.1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    ax1.plot(N, frag, "o-", color=C_RED, linewidth=3, markersize=8)
    ax1.axvline(26, color=C_GREEN, linestyle="--", linewidth=2, alpha=0.7)
    ax1.axvline(7, color=C_ORANGE, linestyle="--", linewidth=2, alpha=0.5)
    ax1.fill_between([7, 26], -1, 20, alpha=0.08, color=C_GREEN)
    ax1.annotate("N=26 甜点区", xy=(26, 0), xytext=(20, 5),
                 fontsize=14, weight="bold", color=C_GREEN,
                 arrowprops=dict(arrowstyle="->", color=C_GREEN, lw=2))
    ax1.annotate("N≥7 碎片归零", xy=(7, 4.2), xytext=(4, 10),
                 fontsize=13, color=C_ORANGE,
                 arrowprops=dict(arrowstyle="->", color=C_ORANGE, lw=1.5))
    ax1.set_xlabel("最小切长 N（字符）", fontsize=14)
    ax1.set_ylabel("<8 字符碎片率（%）", fontsize=14)
    ax1.set_title("碎片率随 N 变化", fontsize=16, weight="bold")
    ax1.grid(alpha=0.3)
    ax1.set_ylim(-1, 20)

    # 右图：新旧切分对比（中位/均值/碎片率）
    metrics = ["中位长\n（字符）", "均值\n（字符）", "碎片率\n（%）"]
    old = [21, 34, 13.38]
    new_v2 = [47, 70, 0]
    new_n26 = [47, 60.1, 0]
    x = np.arange(3)
    w = 0.25
    ax2.bar(x - w, old, w, label="旧逗号切分", color=C_RED, alpha=0.85)
    ax2.bar(x, new_v2, w, label="v2 去逗号（句边界）", color=C_GREEN, alpha=0.85)
    ax2.bar(x + w, new_n26, w, label="逗号+N26 水位闸", color=C_BLUE, alpha=0.85)
    ax2.set_xticks(x)
    ax2.set_xticklabels(metrics, fontsize=13)
    ax2.set_title("新旧切分对比（212 篇 / 139,665 块基线）", fontsize=16, weight="bold")
    ax2.legend(fontsize=12)
    ax2.grid(alpha=0.3, axis="y")
    # 标注数值
    for i, (o, v, n) in enumerate(zip(old, new_v2, new_n26)):
        ax2.text(i - w, o + 0.5, f"{o}", ha="center", fontsize=11, weight="bold", color=C_RED)
        ax2.text(i, v + 0.5, f"{v}", ha="center", fontsize=11, weight="bold", color=C_GREEN)
        ax2.text(i + w, n + 0.5, f"{n}", ha="center", fontsize=11, weight="bold", color=C_BLUE)

    plt.tight_layout()
    fig.savefig("assets/diagram_4_chunking.png", dpi=150, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)


# ── 图 5：排查决策树（分层断点定位法）─────────────────────────
def diagram_troubleshoot_tree():
    fig, ax = plt.subplots(figsize=(16, 10))
    fig.patch.set_facecolor(C_BG)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    ax.set_title("RAG 问题排查决策树：分层断点定位法", fontsize=22, weight="bold", pad=20, color=C_BOX)

    # 顶层：问题入口
    rounded_box(ax, 0.35, 0.90, 0.30, 0.06, "问题现象", C_BOX, fs=16)

    # 第一层：六层定位
    layers = ["接入层", "异步层", "ETL层", "存储层", "检索层", "应用层"]
    colors = [C_BLUE, C_ORANGE, C_GREEN, C_PURPLE, C_RED, C_TEAL]
    y1 = 0.75
    for i, (name, c) in enumerate(zip(layers, colors)):
        x = 0.06 + i * 0.16
        rounded_box(ax, x, y1, 0.13, 0.055, name, c, fs=14)
        arrow(ax, 0.50, 0.895, x + 0.065, y1 + 0.058, color="#94a3b8", lw=1.5)

    # 第二层：典型问题
    problems = [
        "上传超时/\n格式拒收",
        "队列积压/\n消费失败",
        "解析失败/\n分片异常",
        "落库缺口/\n计数对账失败",
        "检索隐身/\n召回不准",
        "权限过滤/\n上下文组装"
    ]
    y2 = 0.58
    for i, p in enumerate(problems):
        x = 0.06 + i * 0.16
        rounded_box(ax, x, y2, 0.13, 0.07, p, "#ffffff", fs=11, tc=C_BOX, weight="normal")
        arrow(ax, x + 0.065, y1 + 0.05, x + 0.065, y2 + 0.075, color=colors[i], lw=1.5)

    # 第三层：排查工具
    tools = [
        "格式白名单\n对象存储日志",
        "监控面板\n失败队列",
        "黄金校验\n分片统计",
        "SQLite 权威计数\noutbox 对账",
        "带分类过滤\n冒烟检索",
        "白名单配置\n上下文日志"
    ]
    y3 = 0.38
    for i, t in enumerate(tools):
        x = 0.06 + i * 0.16
        rounded_box(ax, x, y3, 0.13, 0.07, t, "#f1f5f9", fs=10, tc=C_BOX, weight="normal")
        arrow(ax, x + 0.065, y2, x + 0.065, y3 + 0.075, color="#94a3b8", lw=1.2, ls="--")

    # 底部：三条铁律
    ax.text(0.5, 0.22, "三条铁律", ha="center", fontsize=16, weight="bold", color=C_BOX)
    rules = [
        "权威计数永远以元数据库为准，监控计数仅供参考",
        "入库 ≠ 可检索，三配置（分类/路由/白名单）必须同步",
        "监控失明 = 链路被绕行，先查是否绕过统一入口"
    ]
    yy = 0.14
    for i, r in enumerate(rules):
        rounded_box(ax, 0.10, yy, 0.80, 0.045, f"{i+1}. {r}", "#ffffff", fs=12, tc=[C_BLUE, C_RED, C_ORANGE][i], weight="bold")
        yy -= 0.065

    plt.tight_layout()
    fig.savefig("assets/diagram_5_troubleshoot.png", dpi=150, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)


# ── 图 6：调优效果总览（六案例收益）─────────────────────────
def diagram_gains():
    fig, ax = plt.subplots(figsize=(16, 9))
    fig.patch.set_facecolor(C_BG)
    ax.set_title("六大调优案例实测收益总览", fontsize=22, weight="bold", pad=20, color=C_BOX)

    cases = [
        ("案例一\n分片水位闸", "碎片率\n13.4% → 0%", C_GREEN),
        ("案例二\n检索隐身", "静默故障\n→ 可检索", C_BLUE),
        ("案例三\nCLI 直连", "监控失明\n→ 全埋点", C_ORANGE),
        ("案例四\n白名单拒收", "格式异常\n→ 明确报错", C_PURPLE),
        ("案例五\n队列积压", "失败堆积\n→ 自动治理", C_RED),
        ("案例六\n索引阻塞", "吞吐 +59%\nrate +168%", C_TEAL),
    ]
    y = 0.68
    for i, (name, gain, c) in enumerate(cases):
        x = 0.06 + i * 0.16
        rounded_box(ax, x, y, 0.13, 0.08, name, c, fs=13)
        rounded_box(ax, x, y - 0.14, 0.13, 0.09, gain, "#ffffff", fs=11, tc=C_BOX, weight="bold")
        arrow(ax, x + 0.065, y, x + 0.065, y - 0.05, color=c, lw=2)

    # 底部：调优方法论
    ax.text(0.5, 0.38, "调优方法论沉淀", ha="center", fontsize=18, weight="bold", color=C_BOX)
    methods = [
        "参数回写配置真源（临时调参 = 负债）",
        "冻结基线快照（调优前后可对照）",
        "全语料实测（禁抽样/合成样本）",
        "对立指标拆双看板（中位/均值分列）",
        "写入口根治优于尾部清理"
    ]
    yy = 0.30
    for i, m in enumerate(methods):
        rounded_box(ax, 0.15, yy, 0.70, 0.045, m, "#ffffff", fs=13, tc=C_BOX, weight="normal")
        yy -= 0.065

    plt.tight_layout()
    fig.savefig("assets/diagram_6_gains.png", dpi=150, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)


if __name__ == "__main__":
    diagram_chunking_calibration()
    print("diagram_4_chunking.png ✓")
    diagram_troubleshoot_tree()
    print("diagram_5_troubleshoot.png ✓")
    diagram_gains()
    print("diagram_6_gains.png ✓")
