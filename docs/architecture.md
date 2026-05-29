# Architecture

```
Chrome Extension               Python Backend                  Dashboard
┌──────────────┐              ┌───────────────────┐          ┌──────────┐
│ API Intercept│──JSON/CSV──→│ Collector→DuckDB   │──→       │Streamlit │
│ SSR Extract  │              │         ↓         │          │Rankings  │
│ DOM Fallback │              │ DSPy + LLM Score  │          │Charts    │
└──────────────┘              └───────────────────┘          └──────────┘
```

## Data Collection

**Path A: Chrome Extension**
- Intercepts fetch()/XHR to Shopee's search API
- SSR JSON extraction for xiapibuy (server-rendered)
- DOM fallback with multi-selector strategy
- Zero 403 risk: uses user's own session

**Path B: CSV**
- Manual data import, handles EN/CN column names

## Storage (DuckDB)

Columnar embedded DB → fast analytical queries.
Direct CSV query without import.

## AI Scoring (DSPy)

**Real mode:** DSPy ProductScore signature → ChainOfThought → Zhipu GLM-4-Flash or DeepSeek
**Mock mode:** Rule-based scoring (price + sales + rating + keywords)

## Tech Stack

| Layer | Choice | Reason |
|-------|--------|--------|
| Data | Chrome MV3 | User session → no 403 |
| DB | DuckDB | Columnar, fast analytics |
| AI | DSPy | Programmatic LM programming |
| LLM | Zhipu GLM-4 | China-accessible |
| UI | Streamlit | Fastest Python dashboard |
| Deploy | Docker Compose | One command |
```

ecom-intelligence/
├── extension/          # Chrome Extension
├── backend/            # Python
│   ├── collectors/     # Data parsing
│   ├── pipelines/      # AI scoring
│   ├── storage/        # DuckDB
│   └── scheduler/      # (future)
├── dashboard/          # Streamlit
├── examples/           # Sample data
├── prompts/            # AI prompts
├── docs/               # This doc
├── docker-compose.yml
├── Dockerfile
└── README.md
```
