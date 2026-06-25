from typing import Any, Literal

from pydantic import BaseModel, Field


class GenerateBrandRequest(BaseModel):
    idea: str = Field(default="", description="Startup idea to brand.")
    answers: dict[str, Any] = Field(
        default_factory=dict,
        description="Answers keyed by agent ID or public workflow label.",
    )
    currentAgent: str = Field(
        default="",
        description="The workflow agent that just received an answer.",
    )


class AgentSummary(BaseModel):
    id: str
    name: str
    role: str
    objective: str | None = None
    input: str | None = None
    outputSchema: dict[str, Any] | None = None


class BrandWorkflowResponse(BaseModel):
    status: Literal["needs_input", "completed", "error"]
    currentAgent: str | None = None
    question: str | None = None
    agent: AgentSummary | None = None
    agentOutputs: dict[str, Any] | None = None
    brandData: dict[str, Any] | None = None
    error: str | None = None


class HealthResponse(BaseModel):
    ok: bool
    service: str
    port: int
    agents: int
    model: dict[str, Any]


class AgentsResponse(BaseModel):
    ok: bool
    agents: list[dict[str, Any]]


class ModelStatusResponse(BaseModel):
    ok: bool
    model: dict[str, Any]


class SystemStatusResponse(BaseModel):
    ok: bool
    agents: list[dict[str, Any]]
    model: dict[str, Any]
    workflow: list[str]

