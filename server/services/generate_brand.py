import logging
from typing import Any

from agents import (
    generate_agent_question,
    get_agent,
    get_agent_registry as get_registered_agents,
    get_workflow_agent_ids,
    normalize_agent_key,
    normalize_answer_map,
    run_brand_pipeline,
)

logger = logging.getLogger(__name__)


def generate_brand_workflow(
    idea: str,
    answers: dict[str, Any] | None = None,
    current_agent: str = "",
) -> dict[str, Any]:
    normalized_idea = normalize_text(idea)
    normalized_answers = normalize_answer_map(answers)
    current_agent_id = normalize_agent_key(current_agent)

    logger.info("Brand workflow request received for agent '%s'.", current_agent_id or "start")

    if not normalized_idea:
        return {"status": "error", "error": "Startup idea is required."}

    workflow_agent_ids = get_workflow_agent_ids()
    if not workflow_agent_ids:
        return {"status": "error", "error": "No workflow agents are configured."}

    if not current_agent_id:
        return needs_input(workflow_agent_ids[0], normalized_idea, normalized_answers)

    if current_agent_id not in workflow_agent_ids:
        logger.warning("Unknown workflow agent '%s'; restarting workflow.", current_agent_id)
        return needs_input(workflow_agent_ids[0], normalized_idea, normalized_answers)

    if not normalized_answers.get(current_agent_id):
        return needs_input(current_agent_id, normalized_idea, normalized_answers)

    next_agent_id = get_next_agent_id(current_agent_id, workflow_agent_ids)
    if next_agent_id:
        return needs_input(next_agent_id, normalized_idea, normalized_answers)

    agent_outputs = run_brand_pipeline(normalized_idea, normalized_answers)
    return {
        "status": "completed",
        "agentOutputs": agent_outputs,
        "brandData": build_client_brand_data(agent_outputs),
    }


def get_agent_registry() -> list[dict[str, Any]]:
    return get_registered_agents()


def needs_input(agent_id: str, idea: str, answers: dict[str, str]) -> dict[str, Any]:
    agent = get_agent(agent_id)
    if agent is None:
        raise ValueError(f"Unknown workflow agent: {agent_id}")

    return {
        "status": "needs_input",
        "currentAgent": agent.public_id,
        "question": generate_agent_question(agent_id, idea, answers),
        "agent": agent.prompt_summary(),
    }


def get_next_agent_id(current_agent_id: str, workflow_agent_ids: list[str]) -> str | None:
    current_index = workflow_agent_ids.index(current_agent_id)
    next_index = current_index + 1
    return workflow_agent_ids[next_index] if next_index < len(workflow_agent_ids) else None


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


def normalize_text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""
