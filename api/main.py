import os
import sys
import uuid
import threading
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import sqlite3
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv()

from graph.graph import build_graph
from graph.state import ResearchState
from tools.graveyard import get_graveyard_summary, init_db
from tools.streaming import print_stream_event

app = FastAPI(
    title="Quant Research Agent API",
    description="Autonomous quantitative research powered by LangGraph",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── In-memory job store ───────────────────────────────────────
jobs: dict[str, dict] = {}


# ── Request / Response models ─────────────────────────────────
class ResearchRequest(BaseModel):
    hypothesis: str
    max_refinements: int = 2
    auto_approve: bool = True


class ResearchResponse(BaseModel):
    job_id: str
    status: str
    message: str


# ── Background task ───────────────────────────────────────────
def run_research_job(
    job_id: str, hypothesis: str, max_refinements: int, auto_approve: bool
):
    jobs[job_id]["status"] = "running"
    jobs[job_id]["started_at"] = datetime.now().isoformat()
    jobs[job_id]["logs"] = []

    os.environ["MAX_REFINEMENTS"] = str(max_refinements)
    os.environ["AUTO_APPROVE"] = "1" if auto_approve else "0"

    initial_state: ResearchState = {
        "hypothesis": hypothesis,
        "sub_questions": [],
        "assets": [],
        "timeframe": {},
        "generated_code": "",
        "execution_result": {},
        "analysis": {},
        "iteration": 0,
        "refined_hypothesis": "",
        "final_report": "",
        "status": "planning",
        "human_approved": False,
        "human_feedback": "",
    }

    try:
        graph = build_graph()
        final_state = None

        for event in graph.stream(initial_state, stream_mode="updates"):
            for node_name, node_state in event.items():
                log_entry = {
                    "node": node_name,
                    "timestamp": datetime.now().isoformat(),
                    "status": node_state.get("status", ""),
                    "iteration": node_state.get("iteration", 0),
                }
                jobs[job_id]["logs"].append(log_entry)
                jobs[job_id]["current_node"] = node_name
                final_state = node_state

        if final_state:
            analysis = final_state.get("analysis", {})
            jobs[job_id]["status"] = "completed"
            jobs[job_id]["verdict"] = analysis.get("verdict", "weak")
            jobs[job_id]["sharpe_ratio"] = analysis.get("sharpe_ratio")
            jobs[job_id]["total_return"] = analysis.get("total_return")
            jobs[job_id]["n_trades"] = analysis.get("n_trades")
            jobs[job_id]["final_report"] = final_state.get("final_report", "")
            jobs[job_id]["assets"] = final_state.get("assets", [])
            jobs[job_id]["iterations"] = final_state.get("iteration", 0)
            jobs[job_id]["completed_at"] = datetime.now().isoformat()

    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)


# ── Routes ────────────────────────────────────────────────────


@app.get("/")
def root():
    return {
        "name": "Quant Research Agent API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": [
            "POST /research",
            "GET  /research/{job_id}",
            "GET  /research/{job_id}/logs",
            "GET  /jobs",
            "GET  /graveyard",
            "GET  /reports",
            "GET  /reports/{filename}",
        ],
    }


@app.post("/research", response_model=ResearchResponse)
def start_research(request: ResearchRequest, background_tasks: BackgroundTasks):
    if not request.hypothesis.strip():
        raise HTTPException(status_code=400, detail="Hypothesis cannot be empty")

    job_id = str(uuid.uuid4())[:8]
    jobs[job_id] = {
        "job_id": job_id,
        "hypothesis": request.hypothesis,
        "status": "queued",
        "created_at": datetime.now().isoformat(),
        "current_node": None,
        "logs": [],
    }

    background_tasks.add_task(
        run_research_job,
        job_id,
        request.hypothesis,
        request.max_refinements,
        request.auto_approve,
    )

    return ResearchResponse(
        job_id=job_id,
        status="queued",
        message=f"Research job {job_id} started. Poll GET /research/{job_id} for status.",
    )


@app.get("/research/{job_id}")
def get_job(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    job = jobs[job_id].copy()
    job.pop("logs", None)  # exclude logs from summary
    job.pop("final_report", None)
    return job


@app.get("/research/{job_id}/logs")
def get_job_logs(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    return {
        "job_id": job_id,
        "status": jobs[job_id]["status"],
        "current_node": jobs[job_id].get("current_node"),
        "logs": jobs[job_id].get("logs", []),
    }


@app.get("/research/{job_id}/report")
def get_job_report(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    report = jobs[job_id].get("final_report", "")
    if not report:
        raise HTTPException(status_code=404, detail="Report not ready yet")
    return {"job_id": job_id, "report": report}


@app.get("/jobs")
def list_jobs():
    summary = []
    for job_id, job in jobs.items():
        summary.append(
            {
                "job_id": job_id,
                "hypothesis": (
                    job["hypothesis"][:60] + "..."
                    if len(job["hypothesis"]) > 60
                    else job["hypothesis"]
                ),
                "status": job["status"],
                "verdict": job.get("verdict"),
                "created_at": job["created_at"],
            }
        )
    return {"jobs": sorted(summary, key=lambda x: x["created_at"], reverse=True)}


@app.get("/graveyard")
def get_graveyard():
    init_db()
    conn = sqlite3.connect("outputs/graveyard.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, timestamp, original_hypothesis, final_hypothesis,
               verdict, sharpe_ratio, total_return, win_rate,
               n_trades, max_drawdown, iterations, reasoning,
               suggested_refinement, report_path
        FROM hypothesis_graveyard
        ORDER BY timestamp DESC
    """
    )
    rows = cursor.fetchall()
    conn.close()

    columns = [
        "id",
        "timestamp",
        "original_hypothesis",
        "final_hypothesis",
        "verdict",
        "sharpe_ratio",
        "total_return",
        "win_rate",
        "n_trades",
        "max_drawdown",
        "iterations",
        "reasoning",
        "suggested_refinement",
        "report_path",
    ]

    entries = [dict(zip(columns, row)) for row in rows]
    return {"count": len(entries), "entries": entries}


@app.get("/reports")
def list_reports():
    outputs_dir = "outputs"
    if not os.path.exists(outputs_dir):
        return {"reports": []}
    files = [
        f
        for f in os.listdir(outputs_dir)
        if f.startswith("research_report_") and f.endswith(".md")
    ]
    files.sort(reverse=True)
    return {"count": len(files), "reports": files}


@app.get("/reports/{filename}")
def get_report(filename: str):
    path = os.path.join("outputs", filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Report not found")
    return FileResponse(path, media_type="text/markdown")


@app.get("/health")
def health():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


@app.get("/research/{job_id}/chart")
def get_job_chart(job_id: str):
    chart_path = "outputs/backtest_chart.png"
    if not os.path.exists(chart_path):
        raise HTTPException(status_code=404, detail="Chart not available")
    return FileResponse(chart_path, media_type="image/png")


@app.get("/graveyard/{entry_id}/report")
def get_graveyard_report(entry_id: int):
    init_db()
    conn = sqlite3.connect("outputs/graveyard.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT report_path FROM hypothesis_graveyard WHERE id = ?", (entry_id,)
    )
    row = cursor.fetchone()
    conn.close()

    if not row or not row[0]:
        raise HTTPException(status_code=404, detail="No report found for this entry")

    report_path = row[0]
    if not os.path.exists(report_path):
        raise HTTPException(
            status_code=404, detail=f"Report file not found: {report_path}"
        )

    with open(report_path, "r", encoding="utf-8") as f:
        content = f.read()

    return {"id": entry_id, "report": content, "path": report_path}
