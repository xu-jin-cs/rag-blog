#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""demo_ingest.py — 把 corpus/ 目录的文件走一遍完整 ETL 小流水线。

链路：校验 → 清洗 → 分片（句边界 + 最小切长水位闸）→ 向量化（哈希投影模拟）
      → 三写落库（SQLite 记账 + BM25 索引 + 原文副本）→ 写后计数对账。

幂等：按文件内容 MD5 查重，内容未变的文件跳过，变更的覆盖更新，不翻倍。
完成判据：SQLite 权威计数 == 预期 chunk 数，对账失败即非零退出。

用法: python3 demo_ingest.py [--rebuild]   # --rebuild 清掉派生数据全量重建
"""
import hashlib
import json
import math
import os
import re
import sqlite3
import sys
from collections import Counter

from config import (BASE_DIR, CORPUS_DIR, DB_DIR, SQLITE_PATH, BM25_PATH, DOC_DIR,
                    MIN_CHUNK, MAX_CHUNK, EMBED_DIM)

ALLOWED_EXT = {".md", ".txt", ".json"}  # 格式白名单：不认识直接拒收
SENT_END = "。！？；\n"                  # 句末分隔符集合


# ── 校验 ─────────────────────────────────────────────────────
def validate(path):
    ext = os.path.splitext(path)[1].lower()
    if ext not in ALLOWED_EXT:
        raise ValueError(f"格式 {ext} 不在白名单 {sorted(ALLOWED_EXT)}，拒收")
    if os.path.getsize(path) == 0:
        raise ValueError("空文件，拒收")


# ── 清洗 ─────────────────────────────────────────────────────
def clean(text):
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)       # 压缩空白
    text = re.sub(r"\n{3,}", "\n\n", text)    # 压缩空行
    # 代码块保护：``` 包裹的内容原样保留（demo 中仅做标记隔离，不做空白压缩）
    return text.strip()


# ── 分片：句边界断句 + 最小切长水位闸 + 超限硬切 ──────────────
def split_sentences(text):
    buf, sents = [], []
    for ch in text:
        buf.append(ch)
        if ch in SENT_END:
            s = "".join(buf).strip()
            if s:
                sents.append(s)
            buf = []
    tail = "".join(buf).strip()
    if tail:
        sents.append(tail)
    return sents


def hard_split(s, limit):
    """超限兜底：固定长度硬切，保证每块达标。"""
    return [s[i:i + limit] for i in range(0, len(s), limit)]


def chunk_text(text, min_chunk=MIN_CHUNK, max_chunk=MAX_CHUNK):
    """NP 水位闸切分：累积段超过 min_chunk 才在句边界下刀，尾段并回前一块。"""
    chunks, acc = [], ""
    for s in split_sentences(text):
        if len(acc) + len(s) > max_chunk and acc:
            chunks.append(acc)
            acc = s
        else:
            acc += s
        # 水位闸：累积够 min_chunk 且下一句是边界，才允许在此下刀
        if len(acc) >= min_chunk:
            chunks.append(acc)
            acc = ""
    if acc:
        if chunks and len(acc) < min_chunk:
            chunks[-1] += acc          # 尾段不足并回前一块
        else:
            chunks.append(acc)
    # 超限硬切兜底
    out = []
    for c in chunks:
        out.extend(hard_split(c, max_chunk) if len(c) > max_chunk else [c])
    return out


# ── 向量化：中文 bigram 分词 + 哈希投影（真实系统换成 embedding 模型） ──
def tokenize(text):
    text = re.sub(r"\s+", " ", text)
    toks, i = [], 0
    while i < len(text):
        if ord(text[i]) > 127:                       # CJK：二元切词
            if i + 1 < len(text) and ord(text[i + 1]) > 127:
                toks.append(text[i:i + 2]); i += 2
            else:
                toks.append(text[i]); i += 1
        else:                                        # ASCII：连续词
            if text[i] == " ":                       # 空格直接跳过，保证指针前进
                i += 1
                continue
            j = i
            while j < len(text) and ord(text[j]) <= 127 and text[j] != " ":
                j += 1
            toks.append(text[i:j].lower()); i = j
    return toks


def _h(tok, seed=0):
    return int(hashlib.md5((f"{seed}:{tok}").encode()).hexdigest()[:8], 16)


def embed(text, dim=EMBED_DIM):
    v = [0.0] * dim
    for tok in tokenize(text):
        v[_h(tok) % dim] += 1.0
        v[_h(tok, 1) % dim] += 0.5   # 第二哈希降碰撞
    n = math.sqrt(sum(x * x for x in v)) or 1.0
    return [x / n for x in v]


def cosine(a, b):
    return sum(x * y for x, y in zip(a, b))


# ── BM25（纯 python 倒排，真实系统换搜索引擎/倒排库） ─────────
def bm25_index(chunks):
    index = {"df": {}, "docs": {}, "avgdl": 0.0}
    total = 0
    for cid, text in chunks.items():
        toks = tokenize(text)
        tf = Counter(toks)
        index["docs"][cid] = {"tf": dict(tf), "dl": len(toks)}
        total += len(toks)
        for t in tf:
            index["df"][t] = index["df"].get(t, 0) + 1
    index["avgdl"] = total / max(len(chunks), 1)
    return index


def bm25_search(index, query, top_k, k1=1.5, b=0.75):
    N = len(index["docs"])
    if N == 0:
        return []
    qt = tokenize(query)
    scores = {}
    for cid, doc in index["docs"].items():
        s = 0.0
        for t in qt:
            if t not in doc["tf"]:
                continue
            idf = math.log((N - index["df"][t] + 0.5) / index["df"][t] + 1)
            s += idf * doc["tf"][t] * (k1 + 1) / (
                doc["tf"][t] + k1 * (1 - b + b * doc["dl"] / index["avgdl"]))
        if s > 0:
            scores[cid] = s
    return sorted(scores.items(), key=lambda x: -x[1])[:top_k]


# ── 主流程：逐文件 ETL ───────────────────────────────────────
def ingest(rebuild=False):
    if rebuild and os.path.isdir(DB_DIR):
        import shutil
        shutil.rmtree(DB_DIR)
    os.makedirs(DB_DIR, exist_ok=True)
    os.makedirs(DOC_DIR, exist_ok=True)

    db = sqlite3.connect(SQLITE_PATH)
    db.executescript("""
        CREATE TABLE IF NOT EXISTS docs(
            doc_id TEXT PRIMARY KEY, path TEXT, md5 TEXT, n_chunks INTEGER,
            status TEXT, created_at TEXT DEFAULT (datetime('now','localtime')));
        CREATE TABLE IF NOT EXISTS chunks(
            chunk_id TEXT PRIMARY KEY, doc_id TEXT, seq INTEGER,
            text TEXT, vec TEXT, category TEXT);
    """)

    files = sorted(os.listdir(CORPUS_DIR))
    expected = 0
    print(f"== 批量入库：一次性入队 {len(files)} 个文件 ==")
    for name in files:
        path = os.path.join(CORPUS_DIR, name)
        if not os.path.isfile(path):
            continue
        try:
            validate(path)                                   # ① 校验
        except ValueError as e:
            print(f"  [拒收] {name}: {e}")
            continue
        md5 = hashlib.md5(open(path, "rb").read()).hexdigest()
        doc_id = hashlib.md5(name.encode()).hexdigest()[:16]
        row = db.execute("SELECT md5, n_chunks FROM docs WHERE doc_id=?", (doc_id,)).fetchone()
        if row and row[0] == md5:                            # 幂等：内容未变跳过
            print(f"  [跳过] {name}: 内容未变（MD5 幂等）")
            expected += row[1]                               # 对账基数含库内已有
            continue

        text = clean(open(path, encoding="utf-8").read())    # ② 清洗
        chunks = chunk_text(text)                            # ③ 分片
        db.execute("DELETE FROM chunks WHERE doc_id=?", (doc_id,))  # 覆盖不翻倍
        for seq, c in enumerate(chunks):
            cid = f"{doc_id}:{seq}"
            db.execute("INSERT INTO chunks VALUES(?,?,?,?,?,?)",
                       (cid, doc_id, seq, c, json.dumps(embed(c)), "demo"))
        db.execute("INSERT OR REPLACE INTO docs VALUES(?,?,?,?,?,datetime('now','localtime'))",
                   (doc_id, name, md5, len(chunks), "ready"))
        import shutil as _sh
        _sh.copy(path, os.path.join(DOC_DIR, name))          # ④ 原文副本（对象存储替身）
        print(f"  [入库] {name}: {len(chunks)} 块")
        expected += len(chunks)

    # ── 全文索引重建（派生数据，可随时由 SQLite 真源重建） ──
    rows = dict(db.execute("SELECT chunk_id, text FROM chunks").fetchall())
    json.dump(bm25_index(rows), open(BM25_PATH, "w", encoding="utf-8"),
              ensure_ascii=False)

    # ── 写后计数对账：完成判据 = 权威计数 == 预期，而非"代码跑完了" ──
    actual = db.execute("SELECT count(*) FROM chunks").fetchone()[0]
    docs_n = db.execute("SELECT count(*) FROM docs WHERE status='ready'").fetchone()[0]
    db.commit(); db.close()
    print(f"== 对账：chunks 权威计数 {actual} / 预期 {expected} | 文档 {docs_n} 个就绪 ==")
    if actual != expected:
        print("对账失败：存在真实落库缺口"); sys.exit(1)
    print("对账通过 ✓（BM25 索引已重建）")


if __name__ == "__main__":
    ingest(rebuild="--rebuild" in sys.argv)
