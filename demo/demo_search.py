#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""demo_search.py — 混合检索：BM25 词法召回 ∥ 向量召回 → RRF 融合 → 上下文组装。

用法: python3 demo_search.py "查询词" [查询词2 ...]
     python3 demo_search.py            # 无参数时跑内置示例查询（冒烟）
"""
import json
import os
import sqlite3
import sys

from config import SQLITE_PATH, BM25_PATH, TOP_K, RRF_K
from demo_ingest import embed, bm25_search, cosine


def load():
    if not os.path.exists(SQLITE_PATH):
        sys.exit("知识库为空：先运行 python3 demo_ingest.py 完成入库")
    db = sqlite3.connect(SQLITE_PATH)
    chunks = {cid: (text, json.loads(vec))
              for cid, text, vec in db.execute("SELECT chunk_id, text, vec FROM chunks")}
    index = json.load(open(BM25_PATH, encoding="utf-8"))
    return db, chunks, index


def rrf_fuse(rank_lists, k=RRF_K):
    """Reciprocal Rank Fusion：两路排名按 1/(k+rank) 融合，对立指标分开看。"""
    scores = {}
    for ranking in rank_lists:
        for rank, (cid, _s) in enumerate(ranking):
            scores[cid] = scores.get(cid, 0.0) + 1.0 / (k + rank + 1)
    return sorted(scores.items(), key=lambda x: -x[1])


def search(query, chunks, index, top_k=TOP_K):
    bm = bm25_search(index, query, top_k)                       # 路① 词法召回
    qv = embed(query)
    vec = sorted(((cid, cosine(qv, v)) for cid, (t, v) in chunks.items()
                  if cosine(qv, v) > 0),
                 key=lambda x: -x[1])[:top_k]                    # 路② 向量召回
    fused = rrf_fuse([bm, vec])
    return bm, vec, fused


def main():
    queries = sys.argv[1:] or ["分片 参数 怎么调", "消费失败 怎么处理", "RAG 架构"]
    db, chunks, index = load()
    for q in queries:
        bm, vec, fused = search(q, chunks, index)
        print(f"\n──── 查询「{q}」")
        print(f"  BM25 召回: {[c for c, _ in bm]}   向量召回: {[c for c, _ in vec]}")
        if not fused:
            print("  （无命中）")
            continue
        # 上下文组装：把命中块拼成可直接喂给大模型的上下文（检索质量的一部分）
        top = fused[:TOP_K]
        ctx = "\n".join(f"[{i+1}] {chunks[cid][0]}" for i, (cid, _s) in enumerate(top))
        print(f"  融合 Top{TOP_K}: {[c for c, _ in top]}")
        print(f"  组装后上下文 ↓\n{ctx}")


if __name__ == "__main__":
    main()
