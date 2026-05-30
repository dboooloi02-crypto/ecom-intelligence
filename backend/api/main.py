import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent.orchestrator.orchestrator import EcomAgent
from ai.report.report_generator import ReportGenerator

app = FastAPI(title="AI跨境研究员", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
agent = EcomAgent()
reporter = ReportGenerator()

class ResearchRequest(BaseModel):
    query: str

class ResearchResponse(BaseModel):
    query: str
    summary: str
    market_size: str
    hot_products: list[dict]
    competition: str
    recommendation: str
    score: float
    markdown: str
    sources: list[str]

@app.get("/")
def root():
    return {"name": "AI跨境研究员", "version": "0.1.0", "status": "ready"}

@app.post("/api/research", response_model=ResearchResponse)
def research(req: ResearchRequest):
    report = agent.research(req.query)
    md = reporter.to_markdown(report)
    return ResearchResponse(query=report.query, summary=report.summary, market_size=report.market_size, hot_products=report.hot_products, competition=report.competition, recommendation=report.recommendation, score=report.score, markdown=md, sources=report.sources)
