"""
FastAPI Server for E-Commerce Knowledge Graph Explorer & AI Retrieval Dashboard.
Provides REST API endpoints and serves an interactive web interface.
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from backend.pipeline import KnowledgeGraphPipeline
from main import SAMPLE_QUESTIONS


from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="E-Commerce Knowledge Graph & AI Retrieval System",
    description="Knowledge Graph Explorer and Strictly Grounded AI Question-Answering Engine",
    version="1.0.0"
)

# Enable CORS for React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Pipeline
pipeline = KnowledgeGraphPipeline()

# Serve React Vite static build files if available, fallback to web static
current_dir = os.path.dirname(os.path.abspath(__file__))
frontend_dist = os.path.join(current_dir, "frontend", "dist")
frontend_assets = os.path.join(frontend_dist, "assets")
web_dir = os.path.join(current_dir, "web")
static_dir = os.path.join(web_dir, "static")

if os.path.exists(frontend_assets):
    app.mount("/assets", StaticFiles(directory=frontend_assets), name="assets")

if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


class QueryRequest(BaseModel):
    question: str


@app.get("/", response_class=HTMLResponse)
async def serve_index():
    react_index = os.path.join(frontend_dist, "index.html")
    if os.path.exists(react_index):
        with open(react_index, "r", encoding="utf-8") as f:
            return f.read()

    index_file = os.path.join(web_dir, "templates", "index.html")
    if os.path.exists(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            return f.read()

    return "<h1>Knowledge Graph Web Dashboard (Template missing)</h1>"


@app.get("/api/graph")
async def get_graph_data():
    """Returns nodes and edges formatted for Vis-Network graph visualization."""
    return pipeline.kg.to_visualization_dict()


@app.get("/api/stats")
async def get_graph_stats():
    """Returns overall summary and banana requirement audit."""
    summary = pipeline.kg.get_summary()
    banana_audit = pipeline.kg.count_banana_occurrences()
    return {
        "summary": summary,
        "banana_audit": banana_audit,
        "active_model": pipeline.llm.get_provider_name()
    }


@app.get("/api/sample-questions")
async def get_sample_questions():
    """Returns the benchmark evaluation questions."""
    return SAMPLE_QUESTIONS


@app.post("/api/query")
async def execute_query(req: QueryRequest):
    """Executes the full pipeline for a natural language question."""
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    response = pipeline.query(req.question.strip())
    return {
        "question": response.question,
        "graph_query": response.graph_query,
        "retrieved_nodes_count": len(response.retrieved_data.matched_nodes),
        "retrieved_nodes": response.retrieved_data.matched_nodes,
        "relationships": response.retrieved_data.relationships,
        "facts": response.retrieved_data.summary_facts,
        "final_answer": response.final_answer,
        "grounded": response.grounded,
        "model_used": response.model_used
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
