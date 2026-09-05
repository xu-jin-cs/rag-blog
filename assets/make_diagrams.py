#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_diagrams.py — 生成博客《RAG 知识库从 0 到 1》三张架构图（PNG）。

用法: python3 make_diagrams.py   （仅依赖 matplotlib，输出到本目录）
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

plt.rcParams["font.family"] = ["Hiragino Sans", "PingFang SC", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False

# 鲜艳饱满配色（tailwind-600 系）
C_BLUE, C_ORANGE, C_GREEN, C_PURPLE, C_RED, C_TEAL = (
    "#2563EB", "#EA580C", "#16A34A", "#9333EA", "#DC2626", "#0891B2")
C_LAYERS = [C_BLUE, C_ORANGE, C_GREEN, C_PURPLE, C_RED, C_TEAL]
C_BOX, C_BG = "#1e293b", "#f8fafc"


def rounded_box(ax, x, y, w, h, text, fc, fs=13, tc="white", weight="bold"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.012",
                                fc=fc, ec="none", mutation_aspect=1.1))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fs, color=tc, weight=weight)


def arrow(ax, x1, y1, x2, y2, color="#64748b", lw=2.2, ls="-"):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", lw=lw,
                                 color=color, linestyle=ls, mutation_scale=20))


def canvas(w, h):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    fig.patch.set_facecolor(C_BG)
    return fig, ax


# ── 图 1：分层架构 ────────────────────────────────────────────
def diagram_layers():
    fig, ax = canvas(16, 9.6)
    ax.set_title("RAG 知识库分层架构", fontsize=24, weight="bold", pad=24, color=C_BOX)

    layers = [
        ("应用层", "终端 / CLI / 编辑器插件    ·    MCP 工具封装"),
        ("检索层", "BM25 词法召回 ∥ 向量召回 → 融合排序 → 白名单过滤 → 上下文组装"),
        ("存储层", "向量数据库  |  全文索引  |  元数据记账（SQLite）  |  对象存储"),
        ("ETL 层", "校验 → 解析抽取 → 清洗 → 分片 → 向量化 → 三写落库 → 写后校验"),
        ("异步层", "消息队列 — 削峰 / 解耦 / 可靠投递    ·    消费者独立进程"),
        ("接入层", "上传 API（queued 即返）  ·  格式白名单校验  ·  文件前置落盘"),
    ]
    top, hh, gap = 0.955, 0.095, 0.034
    y = top
    for i, (name, desc) in enumerate(layers):
        rounded_box(ax, 0.04, y - hh, 0.115, hh, name, C_LAYERS[i], fs=17)
        rounded_box(ax, 0.185, y - hh, 0.775, hh, desc, "#ffffff", fs=13.5, tc=C_BOX, weight="normal")
        if i < len(layers) - 1:
            arrow(ax, 0.5725, y - hh - 0.005, 0.5725, y - hh - gap + 0.005)
        y -= hh + gap

    ax.text(0.04, 0.135, "三条记账旁路（贯穿所有层）", fontsize=13.5, weight="bold", color=C_BOX)
    legend = [
        ("① 审计事件：谁在什么时候入了什么", C_RED),
        ("② 性能埋点：每步耗时 / 吞吐指标", C_ORANGE),
        ("③ 监控面板：队列积压 / 水位看板", C_GREEN),
    ]
    xx = 0.04
    for t, c in legend:
        ax.text(xx, 0.055, "● " + t, fontsize=12.5, color=c, weight="bold")
        xx += 0.335
    fig.savefig("assets/diagram_1_layers.png", dpi=150, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)


# ── 图 2：一份文件的旅程（数据链路） ─────────────────────────
def diagram_pipeline():
    fig, ax = canvas(18, 9.0)
    ax.set_title("一份文件的旅程：从上传到被检索命中", fontsize=24, weight="bold",
                 pad=24, color=C_BOX)

    steps = [
        ("① 上传\n上传接口", C_BLUE),
        ("② 校验\n文件落盘", C_BLUE),
        ("③ 入队\n即发即返", C_ORANGE),
        ("④ 消费者\n独立进程", C_ORANGE),
        ("⑤ ETL\n流水线", C_GREEN),
        ("⑥ 向量库\n批量写入", C_PURPLE),
        ("⑦ 全文\n索引", C_PURPLE),
        ("⑧ 元数据\n记账", C_PURPLE),
        ("⑨ 写后\n对账", C_RED),
        ("⑩ 就绪\n可检索", C_GREEN),
    ]
    n = len(steps); x0, x1 = 0.025, 0.975
    slot = (x1 - x0) / n
    w, gap = slot * 0.88, slot * 0.12
    y, hh = 0.62, 0.17
    for i, (t, c) in enumerate(steps):
        x = x0 + i * slot + gap / 2
        rounded_box(ax, x, y, w, hh, t, c, fs=13)
        if i < n - 1:
            arrow(ax, x + w + 0.005, y + hh / 2, x + slot + gap / 2 - 0.005, y + hh / 2)
    ax.text(0.19, y - 0.07, "同步段（①②）快速响应", ha="center", fontsize=13.5,
            color=C_BLUE, weight="bold")
    ax.text(0.63, y - 0.07, "异步段（③~⑨）消费者节奏自主，不阻塞上传方", ha="center",
            fontsize=13.5, color=C_ORANGE, weight="bold")

    # 检索侧
    rounded_box(ax, 0.05, 0.10, 0.21, 0.16, "用户提问\n（MCP 工具 / API）", C_TEAL, fs=14)
    rounded_box(ax, 0.335, 0.10, 0.26, 0.16, "混合检索\nBM25 ∥ 向量 → 融合排序", C_TEAL, fs=14)
    rounded_box(ax, 0.66, 0.10, 0.29, 0.16, "白名单过滤 → 上下文组装\n→ 交给大模型", C_TEAL, fs=14)
    arrow(ax, 0.264, 0.18, 0.331, 0.18); arrow(ax, 0.599, 0.18, 0.656, 0.18)
    arrow(ax, 0.93, 0.615, 0.93, 0.28, color=C_PURPLE, ls=":")
    arrow(ax, 0.93, 0.28, 0.80, 0.20, color=C_PURPLE, ls=":")
    ax.text(0.938, 0.43, "读取\n⑥⑦⑧", fontsize=12, color=C_PURPLE, weight="bold")

    ax.text(0.5, 0.028, "幂等：按内容指纹查重，重复文件覆盖不翻倍    |    失败：进死信队列，逐行核查后人工处置",
            ha="center", fontsize=12.5, color="#64748b", style="italic")
    fig.savefig("assets/diagram_2_pipeline.png", dpi=150, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)


# ── 图 3：ETL 流水线内部拆解 ────────────────────────────────
def diagram_etl():
    fig, ax = canvas(17, 9.6)
    ax.set_title("ETL 流水线内部拆解：大到向量库，小到清洗与分片", fontsize=24,
                 weight="bold", pad=24, color=C_BOX)

    nodes = [
        ("1. 校验", "格式白名单\n不认识直接拒收", C_BLUE),
        ("2. 解析抽取", "按格式分发\n适配器接自定义源", C_BLUE),
        ("3. 清洗", "代码块保护标记\n调试数据隔离", C_BLUE),
        ("4. 分片", "句边界断句\n最小切长水位闸\n超限硬切兜底", C_ORANGE),
        ("5. 向量化", "批量嵌入\n模型常驻复用\n锁防并发", C_ORANGE),
        ("6. 落库", "向量库+索引\n+SQLite 三写", C_PURPLE),
        ("7. 校验收尾", "写后计数对账\n埋点+审计", C_RED),
    ]
    n = len(nodes); x0, x1 = 0.025, 0.975
    slot = (x1 - x0) / n
    w, gap = slot * 0.84, slot * 0.16
    ytop, ht, hb = 0.83, 0.085, 0.21
    for i, (t, d, c) in enumerate(nodes):
        x = x0 + i * slot + gap / 2
        rounded_box(ax, x, ytop, w, ht, t, c, fs=14)
        rounded_box(ax, x, ytop - hb - 0.02, w, hb, d, "#ffffff", fs=11.5, tc=C_BOX, weight="normal")
        if i < n - 1:
            arrow(ax, x + w + 0.004, ytop + ht / 2, x + slot + gap / 2 - 0.004, ytop + ht / 2)

    ax.text(0.04, 0.50, "三条关键防线", ha="left", fontsize=16, weight="bold", color=C_BOX)
    notes = [
        ("黄金校验：自定义适配器配固定样本，改动后逐条比对抽取产物", C_GREEN),
        ("入库 ≠ 可检索：数据分类 / 层级路由 / 白名单三个配置必须同步扩", C_RED),
        ("完成判据 = 真实落库计数对账通过，而非「代码跑完了」", C_BLUE),
    ]
    yy = 0.39
    for t, c in notes:
        rounded_box(ax, 0.04, yy, 0.92, 0.075, t, "#ffffff", fs=13.5, tc=c, weight="bold")
        yy -= 0.10
    ax.text(0.5, 0.045, "分片是检索质量的第一决定因素：切太碎丢语义、切太粗稀释相关度 —— 调优实录见博客②",
            ha="center", fontsize=13, color="#64748b", style="italic")
    fig.savefig("assets/diagram_3_etl.png", dpi=150, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)


if __name__ == "__main__":
    diagram_layers(); print("diagram_1_layers.png ✓")
    diagram_pipeline(); print("diagram_2_pipeline.png ✓")
    diagram_etl(); print("diagram_3_etl.png ✓")
