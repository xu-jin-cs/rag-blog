#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""start.sh 的核心：一行命令跑通 入库 → 检索 冒烟验证（也可直接用 start.sh）。"""
import subprocess
import sys

SMOKE_QUERIES = ["分片 参数 怎么调", "消费失败 怎么处理", "RAG 架构"]


def sh(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(r.stdout, end="")
    if r.returncode != 0:
        print(r.stderr, file=sys.stderr); sys.exit(r.returncode)


if __name__ == "__main__":
    print("── 检索冒烟：混合检索 + 上下文组装（前置：start.sh 已完成入库）")
    sh("python3 demo_search.py " + " ".join(f'"{q}"' for q in SMOKE_QUERIES))
    print("\n全部冒烟通过 ✓  现在可以: python3 demo_search.py \"你的任意问题\"")
