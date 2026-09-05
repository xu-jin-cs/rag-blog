#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""config.py — demo 参数唯一真源。

所有可调参数集中在此（参数回写真源，禁止散落硬编码），
改这里即可体验"分片粒度 / 召回数量"对检索质量的影响。
"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CORPUS_DIR = os.path.join(BASE_DIR, "corpus")
DB_DIR = os.path.join(BASE_DIR, ".ragdemo")          # 派生数据目录（可随时删除重建）
SQLITE_PATH = os.path.join(DB_DIR, "demo.db")        # 元数据记账（真源，权威计数）
BM25_PATH = os.path.join(DB_DIR, "bm25.json")        # 全文索引（派生数据，可重建）
DOC_DIR = os.path.join(DB_DIR, "files")              # 原始文件副本（对象存储的极简替身）

# ── 分片（chunking）参数 ─────────────────────────────────────
MIN_CHUNK = 26      # 最小切长水位闸：累积不足 26 字符不在分隔符下刀，并段继续
MAX_CHUNK = 300     # 超限硬切兜底：单块超过 300 字符强制切（保证每块达标）
OVERLAP = 0         # 片间重叠字符数

# ── 向量化参数 ───────────────────────────────────────────────
EMBED_DIM = 256     # 模拟向量维度（demo 用 token 哈希投影，真实系统换 bge-m3 等 embedding 模型）

# ── 检索参数 ─────────────────────────────────────────────────
TOP_K = 3           # 每路召回条数
RRF_K = 60          # Reciprocal Rank Fusion 常数（BM25 与向量两路排名融合）
