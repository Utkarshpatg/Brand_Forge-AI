import os
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from services.generate_brand import generate_brand_workflow, get_agent_registry


load_dotenv()

PORT = int(os.getenv("PORT", "5000"))
CLIENT_ORIGIN = os.getenv("CLIENT_ORIGIN", "http://localhost:5173")

app = FastAPI(title="BrandForge AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[CLIENT_ORIGIN, "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class GenerateBrandRequest(BaseModel):
    idea: Any = ""
    answers: dict[str, Any] = Field(default_factory=dict)
    currentAgent: Any = ""


@app.get("/")
def root() -> dict[str, Any]:
    return {
        "ok": True,
        "name": "BrandForge AI Backend",
        "endpoints": {
            "health": "GET /api/health",
            "agents": "GET /api/agents",
            "brand": "POST /api/generate-brand",
        },
    }


@app.get("/api/health")
def health() -> dict[str, Any]:
    return {
        "ok": True,
        "service": "brand-engine",
        "port": PORT,
        "agents": len(get_agent_registry()),
    }


@app.get("/api/agents")
def list_agents() -> dict[str, Any]:
    return {
        "ok": True,
        "agents": get_agent_registry(),
    }


@app.post("/api/generate-brand")
def generate_brand(payload: GenerateBrandRequest) -> dict[str, Any]:
    normalized_idea = payload.idea.strip() if isinstance(payload.idea, str) else ""

    if not normalized_idea:
        return JSONResponse(
            status_code=400,
            content={"status": "error", "error": "Startup idea is required."},
        )

    return generate_brand_workflow(
        idea=normalized_idea,
        answers=payload.answers,
        current_agent=payload.currentAgent if isinstance(payload.currentAgent, str) else "",
    )


@app.post("/api/generate")
def generate_legacy(payload: GenerateBrandRequest) -> dict[str, Any]:
    return generate_brand_workflow(
        idea=str(payload.idea or "").strip(),
        answers=payload.answers,
        current_agent=payload.currentAgent if isinstance(payload.currentAgent, str) else "",
    )


