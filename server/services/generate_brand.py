import logging
from typing import Any

from agents import AGENTS, run_brand_pipeline

logger = logging.getLogger(__name__)

WORKFLOW_AGENTS = {
    "Discovery": {
        "key": "discovery",
        "question": "Who is your primary target audience for this startup?",
    },
    "Strategy": {
        "key": "strategy",
        "question": "Should the brand personality feel premium, friendly, innovative, or playful?",
    },
    "Visual": {
        "key": "visualIdentity",
        "question": "Do you prefer a design style that is modern, futuristic, minimalist, or luxury?",
    },
}

WORKFLOW_ORDER = ["Discovery", "Strategy", "Visual"]


def generate_brand_workflow(
    idea: str,
    answers: dict[str, Any] | None = None,
    current_agent: str = "",
) -> dict[str, Any]:
    normalized_idea = normalize_text(idea)
    normalized_answers = normalize_answers(answers)
    normalized_agent = normalize_text(current_agent)

    logger.info("Brand workflow request received for agent '%s'.", normalized_agent or "start")

    if not normalized_idea:
        return {"status": "error", "error": "Startup idea is required."}

    if not normalized_agent:
        return needs_input("Discovery")

    if normalized_agent == "Discovery" and normalized_answers.get("Discovery"):
        return needs_input("Strategy")

    if normalized_agent == "Strategy" and normalized_answers.get("Strategy"):
        return needs_input("Visual")

    if normalized_agent == "Visual" and normalized_answers.get("Visual"):
        agent_outputs = run_brand_pipeline(normalized_idea, normalized_answers)
        return {
            "status": "completed",
            "agentOutputs": agent_outputs,
            "brandData": build_client_brand_data(agent_outputs),
        }

    return needs_input(normalized_agent if is_known_agent(normalized_agent) else "Discovery")


def get_agent_registry() -> list[dict[str, Any]]:
    return [
        {
            "key": key,
            "id": agent["id"],
            "name": agent["name"],
            "role": agent["role"],
            "objective": agent["objective"],
            "input": agent["input"],
            "outputSchema": agent["outputSchema"],
        }
        for key, agent in AGENTS.items()
    ]


def needs_input(agent_name: str) -> dict[str, Any]:
    agent_config = WORKFLOW_AGENTS.get(agent_name, WORKFLOW_AGENTS["Discovery"])
    prompt_agent = AGENTS[agent_config["key"]]

    return {
        "status": "needs_input",
        "currentAgent": agent_name,
        "question": agent_config["question"],
        "agent": {
            "id": prompt_agent["id"],
            "name": prompt_agent["name"],
            "role": prompt_agent["role"],
            "objective": prompt_agent["objective"],
        },
    }


def build_client_brand_data(agent_outputs: dict[str, Any]) -> dict[str, Any]:
    discovery = agent_outputs["discovery"]
    strategy = agent_outputs["strategy"]
    visual = agent_outputs["visual"]
    validator = agent_outputs["validator"]
    final = agent_outputs["final"]
    colors = [color["hex"] for color in visual["colorPalette"]]
    typography = [
        value
        for value in [visual["typography"].get("headingFont"), visual["typography"].get("bodyFont")]
        if value
    ]

    return {
        "brandName": final["brandName"],
        "mission": final["mission"],
        "audience": final["audience"],
        "voice": ", ".join(final["brandVoice"]),
        "brandVoice": final["brandVoice"],
        "brandPersonality": final["brandPersonality"],
        "positioning": final["positioning"],
        "tagline": final["tagline"],
        "colors": colors,
        "colorPalette": final["colorPalette"],
        "typography": typography,
        "typographyDetails": final["typography"],
        "logoConcept": visual["logoConcept"],
        "logoPrompt": final["logoPrompt"],
        "validationReport": final["validationSummary"],
        "brandConsistencyScore": final["coherenceScore"],
        "validatorStatus": validator["status"],
        "discovery": discovery,
        "strategy": strategy,
        "visual": visual,
        "validator": validator,
    }


def normalize_answers(answers: dict[str, Any] | None) -> dict[str, str]:
    if not isinstance(answers, dict):
        return {}

    return {
        "Discovery": normalize_text(answers.get("Discovery")),
        "Strategy": normalize_text(answers.get("Strategy")),
        "Visual": normalize_text(answers.get("Visual")),
    }


def normalize_text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def is_known_agent(agent_name: str) -> bool:
    return agent_name in WORKFLOW_AGENTS
