# ecom-intelligence

**AI跨境研究员 — 输入一句话，自动生成市场研究报告**

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.133-009688?logo=fastapi)](https://fastapi.org)
[![DuckDB](https://img.shields.io/badge/DuckDB-1.0-yellow?logo=duckdb)](https://duckdb.org)

> 跨境电商版 Deep Research + Accio Work  
> 不是选品工具，是 **AI跨境研究员**

---

## 🚀 Quick Start

```bash
git clone https://github.com/dboooloi02-crypto/ecom-intelligence.git
cd ecom-intelligence
uvicorn backend.api.main:app --host 0.0.0.0 --port 8000
# 前端: cd frontend && python3 -m http.server 5500 → http://localhost:5500
```

**不需要 API Key，不需要数据库，开箱即用。**

---

## 🎯 一句话研究

输入 `分析台湾宠物用品市场` → 60秒输出：市场规模、热门TOP5、竞争分析、推荐产品

## 🏗 架构

```
用户一句话 → Agent Orchestrator → Collector → Scorer → Report
```

### 目录

```
agent/          # Agent 核心（orchestrator/planner/memory/researcher）
collectors/     # 数据采集（base/shopee/lazada/tiktok）
ai/             # AI能力（scorer/report/embeddings）
backend/api/    # FastAPI
frontend/       # 聊天式UI
db/             # DuckDB + Qdrant（预留）
```

## 🔧 设计原则

1. 先冻结架构，后写代码  
2. Fake Collector先跑通全链路  
3. V1不上LangGraph，简单串行  
4. AI研究员 > 选品工具

## 🛤 Roadmap

V1 ✅ AI选品助手 → V2 Deep Research → V3 竞品监控 → V4 Agent Browser → V5 内容生成 → V6 全自动运营
