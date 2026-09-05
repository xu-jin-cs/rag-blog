# dsh-skills · RAG 知识库系列博客配套仓库

本仓库是《RAG 知识库从 0 到 1》系列博客的配套开源材料：**架构图 + 可运行 mini RAG demo**，内容源自真实生产实践（通用化脱敏版）。

## 目录

```
dsh-skills/
├── blog/                    # 系列博客正文
│   └── rag_from_zero_part1.md   # 第一篇：架构、链路与快速搭建
├── assets/                  # 架构图（PNG + 生成源码）
│   ├── diagram_1_layers.png     # 分层架构
│   ├── diagram_2_pipeline.png   # 一份文件的旅程（数据链路）
│   ├── diagram_3_etl.png        # ETL 流水线拆解
│   └── make_diagrams.py         # 图表生成源码（仅依赖 matplotlib）
└── demo/                    # 零依赖 mini RAG（纯 Python 标准库）
    ├── start.sh                 # 一键启动：环境检查→入库对账→检索冒烟
    ├── config.py                # 参数唯一真源（分片/向量/检索参数集中在此）
    ├── demo_ingest.py           # ETL：校验→清洗→分片→向量化→三写落库→对账
    ├── demo_search.py           # 检索：BM25∥向量→RRF融合→上下文组装
    ├── smoke_test.py            # 冒烟测试
    └── corpus/                  # 示例语料（3 种格式）
```

## 30 秒跑通

```bash
cd demo
bash start.sh                          # 首次：入库 + 检索冒烟
python3 demo_search.py "你的任意问题"    # 自由提问
bash start.sh --rebuild                # 清掉派生数据全量重建
```

零第三方依赖（Python ≥ 3.9 标准库）。已覆盖生产链路的核心机制：格式白名单、MD5 幂等、
句边界+最小切长水位闸分片、哈希向量化、纯 Python BM25、RRF 融合、写后计数对账、派生数据可重建。

## 系列

- **第一篇（已发布）**：[架构、链路与快速搭建](blog/rag_from_zero_part1.md)
- 第二篇（写作中）：调优实战——六个真实案例：问题 → 排查 → 根因 → 参数 → 实测收益

## License

MIT
