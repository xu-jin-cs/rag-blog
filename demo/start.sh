#!/usr/bin/env bash
# start.sh — RAG demo 一键启动：环境检查 → 批量入库 → 检索冒烟，三步跑通端到端。
set -e
cd "$(dirname "$0")"

echo "════════ RAG demo 一键启动 ════════"

# ① 环境检查：仅需 python3 标准库，零第三方依赖
if ! command -v python3 >/dev/null; then
    echo "✗ 未找到 python3，请先安装（≥3.9）"; exit 1
fi
echo "① 环境检查 ✓  python3 = $(python3 -V)"

# ② 批量入库 + 写后计数对账（对账失败即退出，不带病就绪）
echo; echo "② 批量入库（校验→清洗→分片→向量化→三写落库→对账）"
python3 demo_ingest.py "$@"

# ③ 检索冒烟：混合检索 + 上下文组装
echo; echo "③ 检索冒烟"
python3 smoke_test.py

echo
echo "════════ 全部就绪 ════════"
echo "继续体验： python3 demo_search.py \"你的任意问题\""
echo "全量重建： bash start.sh --rebuild   （清掉派生数据，由语料真源重建）"
