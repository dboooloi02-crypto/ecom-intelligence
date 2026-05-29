# ecom-intelligence

**AI-powered cross-border e-commerce intelligence pipeline**

Collect → Analyze → Visualize — with your own browser session, zero 403 risk.

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![DuckDB](https://img.shields.io/badge/DuckDB-1.0-yellow?logo=duckdb)](https://duckdb.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30-red?logo=streamlit)](https://streamlit.io)

---

## 🚀 Quick Start

```bash
git clone https://github.com/dboooloi02-crypto/ecom-intelligence.git
cd ecom-intelligence
pip install -r requirements.txt
python demo.py
```

You'll see 30 real-world Shopee products scored by AI. **No API keys needed.**

Interactive dashboard:
```bash
streamlit run dashboard/app.py
```

Or with Docker:
```bash
docker compose up
# → http://localhost:8501
```

---

## 🏗 Architecture

```
Chrome Extension               Python Backend                  Dashboard
┌──────────────┐              ┌───────────────────┐          ┌──────────┐
│ API Intercept│──JSON/CSV──→│ Collector→DuckDB   │──→       │Streamlit │
│ SSR Extract  │              │         ↓         │          │Rankings  │
│ DOM Fallback │              │ DSPy + LLM Score  │          │Charts    │
└──────────────┘              └───────────────────┘          └──────────┘
```

**Core design: Zero 403 risk.** The extension uses your own browser session — Shopee sees traffic identical to normal browsing.

---

## ✨ Features

- **7 Shopee domains** + xiapibuy (TW/MY/TH/VN/ID/PH/SG)
- **Triple extraction**: API intercept → SSR JSON → DOM fallback
- **DuckDB storage**: columnar DB, historical trend queries
- **DSPy AI scoring**: programmatic LM programming (Zhipu/DeepSeek)
- **Mock scorer included**: works immediately without API keys
- **Streamlit dashboard**: rankings, charts, KPI cards
- **Docker**: one-command deploy

---

## 📁 Structure

```
ecom-intelligence/
├── extension/              # Chrome Extension (Manifest V3)
│   ├── content/content.js      # API interception + DOM
│   ├── content/extract.js      # SSR→API→DOM triple fallback
│   └── popup/                  # UI + CSV export
├── backend/
│   ├── collectors/             # Data parsing
│   ├── pipelines/              # AI scoring
│   └── storage/                # DuckDB
├── dashboard/app.py           # Streamlit
├── examples/shopee_sample.csv # 30 products
├── prompts/product_score.txt  # AI prompt
├── demo.py                    # Zero-setup demo
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🔧 Triple Extraction

| Layer | Method | Data |
|-------|--------|------|
| 1 | fetch/XHR API intercept | Full (rating, stock, likes) |
| 2 | SSR JSON (__INITIAL_STATE__) | Basic product data |
| 3 | DOM extraction (data-sqe) | Partial (fallback) |

```javascript
// API interception — monitor, don't modify
const originalFetch = window.fetch;
window.fetch = async function(...args) {
  const response = await originalFetch.apply(this, args);
  if (url.includes('search_items')) {
    captureProducts(await response.clone().json());
  }
  return response; // pass through transparently
};
```

---

## 🧪 Data Sources

| Source | API Key | Extension | Description |
|--------|:------:|:---------:|-------------|
| Sample CSV | ❌ | ❌ | 30 products, ready to go |
| CSV upload | ❌ | ❌ | Your own data |
| Extension | ❌ | ✅ | Live from Shopee |
| DuckDB | ❌ | ✅ | Historical data |

---

## 🛤 Roadmap

- [x] v0.1 — Demo + mock scorer + Streamlit dashboard
- [ ] v0.2 — Real DSPy + Zhipu integration
- [ ] v0.3 — Chrome extension packaging
- [ ] v0.4 — Docker production profile
- [ ] v0.5 — Multi-keyword trend tracking

---

## 📃 License

MIT
