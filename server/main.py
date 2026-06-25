import logging
import os
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from dtos import (
    AgentsResponse,
    BrandWorkflowResponse,
    GenerateBrandRequest,
    HealthResponse,
    ModelStatusResponse,
    SystemStatusResponse,
)
from models import get_model_status
from agents import get_workflow_public_ids
from services.generate_brand import generate_brand_workflow, get_agent_registry

load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger(__name__)

PORT = int(os.getenv("PORT", "5000"))
CLIENT_ORIGIN = os.getenv("CLIENT_ORIGIN", "http://localhost:5173")
ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        f"{CLIENT_ORIGIN},http://127.0.0.1:5173",
    ).split(",")
    if origin.strip()
]

app = FastAPI(title="BrandForge AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root() -> dict[str, Any]:
    return {
        "ok": True,
        "name": "BrandForge AI Backend",
        "endpoints": {
            "health": "GET /api/health",
            "agents": "GET /api/agents",
            "models": "GET /api/models",
            "system": "GET /api/system",
            "brand": "POST /api/generate-brand",
            "legacyBrand": "POST /api/generate",
        },
    }


@app.get("/api/health", response_model=HealthResponse)
def health() -> dict[str, Any]:
    return {
        "ok": True,
        "service": "brand-engine",
        "port": PORT,
        "agents": len(get_agent_registry()),
        "model": get_model_status(),
    }


@app.get("/api/agents", response_model=AgentsResponse)
def list_agents() -> dict[str, Any]:
    return {
        "ok": True,
        "agents": get_agent_registry(),
    }


@app.get("/api/models", response_model=ModelStatusResponse)
def model_status() -> dict[str, Any]:
    return {
        "ok": True,
        "model": get_model_status(),
    }


@app.get("/api/system", response_model=SystemStatusResponse)
def system_status() -> dict[str, Any]:
    return {
        "ok": True,
        "agents": get_agent_registry(),
        "model": get_model_status(),
        "workflow": get_workflow_public_ids(),
    }


@app.post("/api/generate-brand", response_model=BrandWorkflowResponse)
def generate_brand(payload: GenerateBrandRequest) -> dict[str, Any]:
    return handle_generate_brand(payload)


@app.post("/api/generate", response_model=BrandWorkflowResponse)
def generate_legacy(payload: GenerateBrandRequest) -> dict[str, Any]:
    return handle_generate_brand(payload)


def handle_generate_brand(payload: GenerateBrandRequest) -> dict[str, Any]:
    idea = payload.idea.strip()
    if not idea:
        raise HTTPException(status_code=400, detail="Startup idea is required.")

    try:
        result = generate_brand_workflow(
            idea=idea,
            answers=payload.answers,
            current_agent=payload.currentAgent,
        )
    except Exception as exc:
        logger.exception("Brand generation request failed.")
        raise HTTPException(status_code=500, detail="Brand generation failed.") from exc

    if result.get("status") == "error":
        logger.warning("Brand generation validation error: %s", result.get("error"))
        raise HTTPException(status_code=400, detail=result.get("error", "Invalid request."))

    return result


