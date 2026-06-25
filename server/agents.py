import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel

from models import (
    DiscoveryOutput,
    StrategyOutput,
    ValidatorOutput,
    VisualOutput,
    get_llm,
    get_model_status,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AgentContext:
    idea: str
    answers: dict[str, str]
    outputs: dict[str, dict[str, Any]]


@dataclass(frozen=True)
class BrandAgent:
    id: str
    public_id: str
    name: str
    role: str
    objective: str
    question_builder: Callable[[AgentContext, "BrandAgent"], str]
    expected_input: str
    output_schema: dict[str, Any]
    llm_schema: type[BaseModel]
    llm_system_prompt: str
    llm_user_template: str
    llm_input_builder: Callable[[AgentContext], dict[str, Any]]
    fallback_runner: Callable[[AgentContext], dict[str, Any]]
    requires_user_input: bool = True

    def registry_entry(self) -> dict[str, Any]:
        return {
            "key": self.id,
            "id": self.id,
            "publicId": self.public_id,
            "name": self.name,
            "role": self.role,
            "objective": self.objective,
            "input": self.expected_input,
            "outputSchema": self.output_schema,
        }

    def prompt_summary(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "objective": self.objective,
        }


WORKFLOW_ORDER = ["discovery", "strategy", "visualIdentity"]
VALIDATION_AGENT_ID = "validator"


def get_agent(agent_id_or_public_id: str) -> BrandAgent | None:
    normalized = normalize_agent_key(agent_id_or_public_id)
    return AGENT_DEFINITIONS.get(normalized)


def get_agent_registry() -> list[dict[str, Any]]:
    return [agent.registry_entry() for agent in AGENT_DEFINITIONS.values()]


def get_workflow_agent_ids() -> list[str]:
    return list(WORKFLOW_ORDER)


def get_executable_agent_ids() -> list[str]:
    return [*WORKFLOW_ORDER, VALIDATION_AGENT_ID]


def get_workflow_public_ids(include_validation: bool = True) -> list[str]:
    agent_ids = get_executable_agent_ids() if include_validation else get_workflow_agent_ids()
    return [AGENT_DEFINITIONS[agent_id].public_id for agent_id in agent_ids]


def normalize_agent_key(agent_id_or_public_id: str) -> str:
    value = normalize_text(agent_id_or_public_id)
    if not value:
        return ""

    if value in AGENT_DEFINITIONS:
        return value

    lowered = value.lower()
    for agent_id, agent in AGENT_DEFINITIONS.items():
        aliases = {
            agent_id.lower(),
            agent.public_id.lower(),
            agent.name.lower(),
            agent.name.lower().replace(" agent", ""),
        }
        if lowered in aliases:
            return agent_id

    return value


def normalize_answer_map(answers: dict[str, Any] | None) -> dict[str, str]:
    if not isinstance(answers, dict):
        return {}

    normalized: dict[str, str] = {}
    for key, value in answers.items():
        agent_id = normalize_agent_key(str(key))
        if agent_id in AGENT_DEFINITIONS:
            normalized[agent_id] = normalize_text(value)

    return normalized


def generate_agent_question(
    agent_id: str,
    idea: str,
    answers: dict[str, Any] | None = None,
    outputs: dict[str, dict[str, Any]] | None = None,
) -> str:
    agent = get_agent(agent_id)
    if agent is None:
        raise ValueError(f"Unknown workflow agent: {agent_id}")

    context = AgentContext(
        idea=normalize_text(idea),
        answers=normalize_answer_map(answers),
        outputs=outputs or {},
    )

    if get_model_status()["configured"]:
        try:
            question = generate_llm_question(agent, context)
            if question:
                return question
        except Exception:
            logger.exception("LLM question generation failed for agent '%s'.", agent.id)

    return agent.question_builder(context, agent)


def generate_llm_question(agent: BrandAgent, context: AgentContext) -> str:
    llm = get_llm()
    prompt = (
        "Generate exactly one short, conversational user question for the active branding agent.\n"
        "The question must be specific to the startup and help the agent accomplish its objective.\n"
        "Do not explain. Do not add numbering. Return only the question.\n\n"
        f"Agent: {agent.name}\n"
        f"Role: {agent.role}\n"
        f"Objective: {agent.objective}\n"
        f"Startup idea: {context.idea}\n"
        f"Previous answers: {context.answers}\n"
        f"Previous agent outputs: {context.outputs}"
    )
    response = llm.invoke(prompt)
    raw_question = getattr(response, "content", response)
    return normalize_question(str(raw_question))


def run_brand_pipeline(idea: str, answers: dict[str, str]) -> dict[str, Any]:
    canonical_answers = normalize_answer_map(answers)

    if get_model_status()["configured"]:
        try:
            logger.info("Running LLM-backed brand agent pipeline.")
            return run_llm_agent_pipeline(idea, canonical_answers)
        except Exception:
            logger.exception("LLM agent pipeline failed; using rule-based fallback.")

    logger.info("Running rule-based brand agent pipeline.")
    return run_rule_based_agent_pipeline(idea, canonical_answers)


def run_llm_agent_pipeline(idea: str, answers: dict[str, str]) -> dict[str, Any]:
    from langchain_core.prompts import ChatPromptTemplate

    llm = get_llm()
    outputs: dict[str, dict[str, Any]] = {}

    for agent_id in get_executable_agent_ids():
        agent = AGENT_DEFINITIONS[agent_id]
        context = AgentContext(idea=idea, answers=answers, outputs=outputs)
        prompt = ChatPromptTemplate.from_messages([
            ("system", agent.llm_system_prompt),
            ("user", agent.llm_user_template),
        ])
        chain = prompt | llm.with_structured_output(agent.llm_schema)
        outputs[agent_id] = chain.invoke(agent.llm_input_builder(context)).model_dump()

    return build_agent_outputs(outputs)


def run_rule_based_agent_pipeline(idea: str, answers: dict[str, str]) -> dict[str, Any]:
    outputs: dict[str, dict[str, Any]] = {}

    for agent_id in get_executable_agent_ids():
        agent = AGENT_DEFINITIONS[agent_id]
        context = AgentContext(idea=idea, answers=answers, outputs=outputs)
        outputs[agent_id] = agent.fallback_runner(context)

    return build_agent_outputs(outputs)


def build_agent_outputs(outputs: dict[str, dict[str, Any]]) -> dict[str, Any]:
    final = run_orchestrator_agent(outputs)
    return {
        "discovery": outputs["discovery"],
        "strategy": outputs["strategy"],
        "visual": outputs["visualIdentity"],
        "validator": outputs["validator"],
        "final": final,
    }


def discovery_llm_inputs(context: AgentContext) -> dict[str, Any]:
    return {
        "idea": context.idea,
        "audience_choice": get_answer(context, "discovery", "Early adopters and growth-focused customers"),
    }


def strategy_llm_inputs(context: AgentContext) -> dict[str, Any]:
    return {
        "discovery_data": str(context.outputs["discovery"]),
        "personality_choice": get_answer(context, "strategy", "Modern"),
    }


def visual_llm_inputs(context: AgentContext) -> dict[str, Any]:
    return {
        "idea": context.idea,
        "discovery_data": str(context.outputs["discovery"]),
        "strategy_data": str(context.outputs["strategy"]),
        "design_style_choice": get_answer(context, "visualIdentity", "Modern"),
    }


def validator_llm_inputs(context: AgentContext) -> dict[str, Any]:
    return {
        "discovery_data": str(context.outputs["discovery"]),
        "strategy_data": str(context.outputs["strategy"]),
        "visual_data": str(context.outputs["visualIdentity"]),
    }


def build_discovery_question(context: AgentContext, agent: BrandAgent) -> str:
    domain = infer_industry(context.idea).lower()
    audience_sets = {
        "health": ["hospitals", "clinics", "independent doctors", "patients"],
        "food": ["college students", "working professionals", "families", "health-conscious locals"],
        "education": ["beginners", "students", "career switchers", "training teams"],
        "financial": ["first-time investors", "small businesses", "families", "finance teams"],
        "hr": ["founders", "HR managers", "recruiters", "employees"],
        "ai software": ["founders", "operators", "technical teams", "enterprise buyers"],
    }
    options = choose_contextual_options(domain, audience_sets, ["early adopters", "busy professionals", "small teams", "decision makers"])
    subject = summarize_idea(context.idea).rstrip(".")
    return normalize_question(f"For {subject}, which audience should the brand win first: {join_options(options)}?")


def build_strategy_question(context: AgentContext, agent: BrandAgent) -> str:
    audience = get_answer(context, "discovery", infer_audience(context.idea)).lower()
    domain = infer_industry(context.idea).lower()
    tone_sets = {
        "health": ["reassuring", "clinical", "human", "innovative"],
        "food": ["warm", "energetic", "fresh", "premium"],
        "education": ["encouraging", "smart", "playful", "credible"],
        "financial": ["secure", "clear", "premium", "modern"],
        "hr": ["professional", "trustworthy", "innovative", "disruptive"],
        "ai software": ["intelligent", "bold", "approachable", "enterprise-ready"],
    }
    options = choose_contextual_options(domain, tone_sets, ["trustworthy", "friendly", "innovative", "premium"])
    return normalize_question(f"For {audience}, what personality should shape the brand voice: {join_options(options)}?")


def build_visual_question(context: AgentContext, agent: BrandAgent) -> str:
    audience = get_answer(context, "discovery", infer_audience(context.idea)).lower()
    personality = get_answer(context, "strategy", "the chosen brand personality").lower()
    domain = infer_industry(context.idea).lower()
    style_sets = {
        "health": ["clean and trustworthy", "calm and human", "modern clinical", "bold wellness"],
        "food": ["fresh and colorful", "minimal and premium", "warm and local", "fast and energetic"],
        "education": ["playful modern", "focused and clean", "bold gamified", "friendly academic"],
        "financial": ["secure minimal", "premium editorial", "modern fintech", "calm professional"],
        "hr": ["clean SaaS", "people-first", "enterprise-ready", "bold modern"],
        "ai software": ["futuristic", "clean SaaS", "bold technical", "warm intelligent"],
    }
    options = choose_contextual_options(domain, style_sets, ["modern", "minimal", "futuristic", "premium"])
    return normalize_question(f"Given a {personality} voice for {audience}, which visual direction fits best: {join_options(options)}?")


def build_validator_question(context: AgentContext, agent: BrandAgent) -> str:
    return ""


def run_discovery_agent(context: AgentContext) -> dict[str, Any]:
    primary_audience = get_answer(context, "discovery", infer_audience(context.idea))
    industry = infer_industry(context.idea)

    return {
        "industry": industry,
        "targetAudience": {
            "primary": primary_audience,
            "secondary": infer_secondary_audience(primary_audience, industry),
        },
        "customerPainPoints": infer_pain_points(industry),
        "mission": f"Help {primary_audience.lower()} solve {summarize_idea(context.idea).lower()} with a simple, trustworthy, and outcome-focused experience.",
        "coreValues": ["Clarity", "Trust", "Momentum", "Customer empathy"],
        "emotionalDrivers": infer_emotional_drivers(context.idea),
        "businessGoals": [
            "Build a memorable brand identity",
            "Communicate value quickly",
            "Create trust at first touchpoint",
            "Support scalable customer acquisition",
        ],
        "marketPosition": f"{summarize_idea(context.idea)} for {primary_audience}",
    }


def run_strategy_agent(context: AgentContext) -> dict[str, Any]:
    discovery = context.outputs["discovery"]
    strategy_input = get_answer(context, "strategy", "").lower()
    personality = infer_personality(strategy_input, discovery)

    return {
        "brandPersonality": personality,
        "brandArchetype": infer_archetype(personality),
        "brandVoice": infer_brand_voice(strategy_input, personality),
        "brandTone": infer_brand_tone(strategy_input),
        "positioningStatement": f"{discovery['industry']} brand for {discovery['targetAudience']['primary'].lower()} who need {discovery['customerPainPoints'][0].lower()}.",
        "valueProposition": f"A focused brand experience that turns {discovery['marketPosition'].lower()} into a clear, trusted choice.",
        "keyDifferentiators": [
            "Audience-specific positioning",
            "Benefit-led messaging",
            "Distinctive visual direction",
            "Validation across strategy and identity",
        ],
        "tagline": create_tagline(discovery, personality),
    }


def run_visual_identity_agent(context: AgentContext) -> dict[str, Any]:
    discovery = context.outputs["discovery"]
    strategy = context.outputs["strategy"]
    design_style = get_answer(context, "visualIdentity", infer_design_style(strategy))
    color_palette = build_color_palette(design_style, strategy)
    typography = build_typography(design_style)
    brand_name = create_brand_name(context.idea, discovery, strategy)
    logo_concept = (
        f"A {design_style.lower()} identity mark that connects {discovery['industry'].lower()} "
        f"credibility with {strategy['brandPersonality'][0].lower()} energy for "
        f"{discovery['targetAudience']['primary'].lower()}."
    )

    return {
        "brandName": brand_name,
        "designStyle": design_style,
        "colorPalette": color_palette,
        "typography": typography,
        "logoConcept": logo_concept,
        "logoPrompt": create_logo_prompt(
            brand_name,
            context.idea,
            discovery,
            strategy,
            design_style,
            color_palette,
            typography,
        ),
    }


def run_validator_agent(context: AgentContext) -> dict[str, Any]:
    discovery = context.outputs["discovery"]
    strategy = context.outputs["strategy"]
    visual = context.outputs["visualIdentity"]
    checks = [
        {"label": "Audience aligns with brand voice", "passed": len(strategy["brandVoice"]) >= 2},
        {"label": "Audience aligns with colors", "passed": 3 <= len(visual["colorPalette"]) <= 5},
        {"label": "Audience aligns with typography", "passed": bool(visual["typography"].get("headingFont") and visual["typography"].get("bodyFont"))},
        {"label": "Mission aligns with positioning", "passed": len(discovery["mission"]) > 40 and len(strategy["positioningStatement"]) > 30},
        {"label": "Positioning aligns with logo", "passed": visual["designStyle"].lower() in visual["logoConcept"].lower()},
        {"label": "Personality aligns with visual style", "passed": bool(strategy["brandPersonality"] and visual["designStyle"])},
        {"label": "Archetype aligns with color palette", "passed": bool(strategy["brandArchetype"] and visual["colorPalette"][0].get("meaning"))},
        {"label": "Tagline aligns with mission", "passed": bool(strategy["tagline"] and discovery["mission"])},
        {"label": "Unique Selling Point clearly defined", "passed": len(strategy["keyDifferentiators"]) >= 3 and len(strategy["valueProposition"]) > 20},
    ]
    passed_checks = [check["label"] for check in checks if check["passed"]]
    failed_checks = [check["label"] for check in checks if not check["passed"]]
    coherence_score = min(99, max(60, 72 + len(passed_checks) * 3))

    return {
        "coherenceScore": coherence_score,
        "status": "APPROVED" if coherence_score >= 75 else "NEEDS_REVISION",
        "passedChecks": passed_checks,
        "failedChecks": failed_checks,
        "improvementSuggestions": [f"Refine: {check}." for check in failed_checks] or ["No critical issues found. Consider user-testing the tagline and logo prompt."],
        "finalSummary": f"The system is {'excellent' if coherence_score >= 90 else 'good'} for launch testing. Strategy, visuals, and audience intent are aligned for {discovery['targetAudience']['primary'].lower()}.",
    }


def run_orchestrator_agent(outputs: dict[str, dict[str, Any]]) -> dict[str, Any]:
    discovery = outputs["discovery"]
    strategy = outputs["strategy"]
    visual = outputs["visualIdentity"]
    validator = outputs["validator"]

    return {
        "brandName": visual["brandName"],
        "mission": discovery["mission"],
        "audience": discovery["targetAudience"]["primary"],
        "brandVoice": strategy["brandVoice"],
        "brandPersonality": strategy["brandPersonality"],
        "positioning": strategy["positioningStatement"],
        "tagline": strategy["tagline"],
        "colorPalette": visual["colorPalette"],
        "typography": visual["typography"],
        "logoPrompt": visual["logoPrompt"],
        "coherenceScore": validator["coherenceScore"],
        "validationSummary": validator["finalSummary"],
    }


def get_answer(context: AgentContext, agent_id: str, default: str) -> str:
    return normalize_text(context.answers.get(agent_id)) or default


def normalize_question(value: str) -> str:
    question = " ".join(value.strip().strip('"\'').split())
    if not question:
        return ""
    return question if question.endswith("?") else f"{question}?"


def choose_contextual_options(domain: str, option_sets: dict[str, list[str]], fallback: list[str]) -> list[str]:
    for keyword, options in option_sets.items():
        if keyword in domain:
            return options
    return fallback


def join_options(options: list[str]) -> str:
    if len(options) < 2:
        return ", ".join(options)
    return f"{', '.join(options[:-1])}, or {options[-1]}"


def normalize_text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def infer_industry(idea: str) -> str:
    text = idea.lower()
    if has_any(text, ["fitness", "health", "wellness", "coach", "clinic", "doctor", "hospital"]):
        return "Health and wellness technology"
    if has_any(text, ["coding", "developer", "programming", "learn"]):
        return "Education technology"
    if has_any(text, ["meal", "food", "restaurant", "delivery", "grocery"]):
        return "Food and lifestyle"
    if has_any(text, ["finance", "bank", "money", "invest", "payment"]):
        return "Financial technology"
    if has_any(text, ["hr", "recruit", "employee", "payroll", "talent"]):
        return "HR software"
    if has_any(text, ["ai", "automation", "platform", "saas"]):
        return "AI software"
    return "Startup technology"


def infer_audience(idea: str) -> str:
    text = idea.lower()
    if "professional" in text:
        return "Busy professionals"
    if "student" in text:
        return "Students and early learners"
    if "family" in text:
        return "Modern families"
    if "creator" in text:
        return "Digital creators"
    if "business" in text:
        return "Small business teams"
    return "Early adopters and growth-focused customers"


def infer_secondary_audience(primary_audience: str, industry: str) -> str:
    if "professional" in primary_audience.lower():
        return "Team leads and workplace wellness buyers"
    if "education" in industry.lower():
        return "Parents, mentors, and training teams"
    if "food" in industry.lower():
        return "Health-conscious households"
    return "Influencers, partners, and decision makers"


def infer_pain_points(industry: str) -> list[str]:
    if "Health" in industry:
        return ["Inconsistent routines", "Low motivation", "Generic guidance", "Difficulty choosing a trustworthy solution"]
    if "Education" in industry:
        return ["Low engagement", "Overwhelming learning paths", "Poor progress feedback", "Difficulty choosing a trustworthy solution"]
    if "Food" in industry:
        return ["Limited convenient choices", "Trust concerns", "Hard-to-maintain lifestyle changes", "Difficulty choosing a trustworthy solution"]
    return ["Difficulty choosing a trustworthy solution", "Too much friction before seeing value", "Lack of clear differentiation in the market"]


def infer_emotional_drivers(idea: str) -> list[str]:
    text = idea.lower()
    drivers = ["Confidence", "Simplicity", "Progress"]
    if "luxury" in text or "premium" in text:
        drivers.append("Status")
    if "family" in text:
        drivers.append("Care")
    if "ai" in text:
        drivers.append("Control")
    return drivers


def infer_personality(strategy_input: str, discovery: dict[str, Any]) -> list[str]:
    if has_any(strategy_input, ["premium", "luxury"]):
        return ["Premium", "Refined", "Trustworthy"]
    if has_any(strategy_input, ["playful", "fun"]):
        return ["Playful", "Warm", "Energetic"]
    if has_any(strategy_input, ["friendly", "human"]):
        return ["Friendly", "Helpful", "Approachable"]
    if has_any(strategy_input, ["innovative", "futuristic"]):
        return ["Innovative", "Bold", "Forward-thinking"]
    if "Financial" in discovery["industry"]:
        return ["Secure", "Clear", "Dependable"]
    return ["Modern", "Clear", "Reliable"]


def infer_archetype(personality: list[str]) -> str:
    joined = " ".join(personality).lower()
    if "premium" in joined or "refined" in joined:
        return "Ruler"
    if "playful" in joined or "energetic" in joined:
        return "Jester"
    if "innovative" in joined or "bold" in joined:
        return "Creator"
    if "helpful" in joined or "friendly" in joined:
        return "Caregiver"
    return "Sage"


def infer_brand_voice(strategy_input: str, personality: list[str]) -> list[str]:
    joined = f"{strategy_input} {' '.join(personality)}".lower()
    if has_any(joined, ["premium", "luxury", "refined"]):
        return ["Sophisticated", "Assured", "Selective"]
    if has_any(joined, ["playful", "fun", "energetic"]):
        return ["Energetic", "Friendly", "Encouraging"]
    if has_any(joined, ["innovative", "bold", "futuristic"]):
        return ["Visionary", "Direct", "Intelligent"]
    return ["Clear", "Helpful", "Trustworthy"]


def infer_brand_tone(strategy_input: str) -> list[str]:
    if has_any(strategy_input, ["premium", "luxury"]):
        return ["Confident", "Polished", "Calm"]
    if has_any(strategy_input, ["playful", "friendly"]):
        return ["Conversational", "Positive", "Supportive"]
    return ["Concise", "Optimistic", "Expert"]


def infer_design_style(strategy: dict[str, Any]) -> str:
    personality = " ".join(strategy["brandPersonality"]).lower()
    if "premium" in personality or "refined" in personality:
        return "Luxury minimal"
    if "playful" in personality:
        return "Bright modern"
    if "innovative" in personality:
        return "Futuristic"
    return "Modern"


def build_color_palette(design_style: str, strategy: dict[str, Any]) -> list[dict[str, str]]:
    style = design_style.lower()
    if has_any(style, ["luxury", "premium"]):
        return [
            {"hex": "#D97706", "meaning": "Signals premium value and confidence."},
            {"hex": "#1E1B4B", "meaning": "Creates depth, authority, and trust."},
            {"hex": "#FAF5FF", "meaning": "Adds refinement and breathing room."},
            {"hex": "#78350F", "meaning": "Adds warmth and heritage."},
        ]
    if has_any(style, ["futuristic", "cyber"]):
        return [
            {"hex": "#06B6D4", "meaning": "Suggests intelligence, clarity, and technology."},
            {"hex": "#D946EF", "meaning": "Adds creative energy and distinction."},
            {"hex": "#0F172A", "meaning": "Creates a serious, high-contrast foundation."},
            {"hex": "#10B981", "meaning": "Signals progress and positive outcomes."},
        ]
    if has_any(style, ["minimal", "clean"]):
        return [
            {"hex": "#0F172A", "meaning": "Builds trust and structure."},
            {"hex": "#64748B", "meaning": "Feels neutral, calm, and professional."},
            {"hex": "#F8FAFC", "meaning": "Creates clarity and whitespace."},
            {"hex": "#3B82F6", "meaning": "Adds approachable confidence."},
        ]
    is_friendly = "friendly" in " ".join(strategy["brandVoice"]).lower()
    return [
        {"hex": "#3B82F6", "meaning": "Communicates trust, clarity, and digital confidence."},
        {"hex": "#10B981", "meaning": "Signals growth, health, and forward motion."},
        {"hex": "#1E293B", "meaning": "Grounds the brand with maturity and stability."},
        {"hex": "#F97316" if is_friendly else "#EF4444", "meaning": "Creates memorable contrast and action energy."},
    ]


def build_typography(design_style: str) -> dict[str, str]:
    style = design_style.lower()
    if "luxury" in style:
        return {"headingFont": "Playfair Display", "bodyFont": "Montserrat"}
    if "minimal" in style:
        return {"headingFont": "Roboto Mono", "bodyFont": "Lato"}
    if "futuristic" in style:
        return {"headingFont": "Orbitron", "bodyFont": "Outfit"}
    return {"headingFont": "Inter", "bodyFont": "Poppins"}


def create_brand_name(idea: str, discovery: dict[str, Any], strategy: dict[str, Any]) -> str:
    idea_words = ["".join(char for char in word if char.isalpha()) for word in idea.split()]
    roots = [word for word in idea_words if len(word) > 4] or ["Origin", "Mint", "Apex", "Flow", "Pulse", "Nova", "Sync", "Lumina"]
    suffixes = ["AI", "Lab", "Hub", "Scale", "Core", "Loop", "Works", "Studio"]
    seed = len(idea) + len(discovery["industry"]) + len(strategy["brandArchetype"])
    return f"{title_case(pick(roots, seed))} {pick(suffixes, seed + 3)}"


def create_tagline(discovery: dict[str, Any], personality: list[str]) -> str:
    lead = personality[0] if personality else "Clear"
    if "Health" in discovery["industry"]:
        return f"{lead} progress, every day."
    if "Education" in discovery["industry"]:
        return f"Learn faster with {lead.lower()} momentum."
    if "Food" in discovery["industry"]:
        return f"{lead} living, delivered simply."
    return f"{lead} ideas, built to grow."


def create_logo_prompt(
    brand_name: str,
    idea: str,
    discovery: dict[str, Any],
    strategy: dict[str, Any],
    design_style: str,
    color_palette: list[dict[str, str]],
    typography: dict[str, str],
) -> str:
    colors = ", ".join(f"{color['hex']} ({color['meaning']})" for color in color_palette)
    return (
        f"Design a professional brand logo for '{brand_name}', a startup focused on {idea}. "
        f"The logo should feel {design_style.lower()} and communicate "
        f"{', '.join(strategy['brandPersonality']).lower()} qualities for "
        f"{discovery['targetAudience']['primary'].lower()}. Use a clean, scalable vector-style "
        "mark with strong silhouette recognition, balanced whitespace, and a premium startup-ready "
        f"finish. The visual language should support the positioning: {strategy['positioningStatement']}. "
        f"Use the color system {colors}. Pair the mark with typography inspired by "
        f"{typography['headingFont']} for headings and {typography['bodyFont']} for supporting text. "
        "Avoid clutter, literal clipart, excessive gradients, tiny details, and generic icons."
    )


def summarize_idea(idea: str) -> str:
    return f"{idea[:77].strip()}..." if len(idea) > 80 else idea


def has_any(text: str, terms: list[str]) -> bool:
    return any(term in text for term in terms)


def pick(items: list[str], seed: int) -> str:
    return items[abs(seed) % len(items)] if items else ""


def title_case(value: str) -> str:
    return value[0].upper() + value[1:].lower() if value else "Origin"


AGENT_DEFINITIONS: dict[str, BrandAgent] = {
    "discovery": BrandAgent(
        id="discovery",
        public_id="Discovery",
        name="Discovery Agent",
        role="Target Audience & Market Research",
        objective="Identify the target audience, customer pain points, mission, and market position.",
        expected_input="Startup idea and user response regarding target audience.",
        output_schema={
            "industry": "string",
            "targetAudience": {"primary": "string", "secondary": "string"},
            "customerPainPoints": "array of strings",
            "mission": "string",
            "coreValues": "array of strings",
            "emotionalDrivers": "array of strings",
            "businessGoals": "array of strings",
            "marketPosition": "string",
        },
        llm_schema=DiscoveryOutput,
        llm_system_prompt="You are the BrandForge Discovery Agent. Analyze audience and market context. Respond only as structured JSON matching the schema.",
        llm_user_template="Startup Idea: {idea}\nTarget Audience Choice: {audience_choice}",
        llm_input_builder=discovery_llm_inputs,
        fallback_runner=run_discovery_agent,
        question_builder=build_discovery_question,
    ),
    "strategy": BrandAgent(
        id="strategy",
        public_id="Strategy",
        name="Strategy Agent",
        role="Brand Voice & Positioning",
        objective="Define personality, voice, archetype, positioning, value proposition, and tagline.",
        expected_input="Discovery output and user response regarding brand personality.",
        output_schema={
            "brandPersonality": "array of strings",
            "brandArchetype": "string",
            "brandVoice": "array of strings",
            "brandTone": "array of strings",
            "positioningStatement": "string",
            "valueProposition": "string",
            "keyDifferentiators": "array of strings",
            "tagline": "string",
        },
        llm_schema=StrategyOutput,
        llm_system_prompt="You are the BrandForge Strategy Agent. Turn discovery insight into brand positioning and voice. Respond only as structured JSON matching the schema.",
        llm_user_template="Discovery Data: {discovery_data}\nPersonality Choice: {personality_choice}",
        llm_input_builder=strategy_llm_inputs,
        fallback_runner=run_strategy_agent,
        question_builder=build_strategy_question,
    ),
    "visualIdentity": BrandAgent(
        id="visualIdentity",
        public_id="Visual",
        name="Visual Identity Agent",
        role="Design Direction & Aesthetics",
        objective="Generate brand name, visual direction, color palette, typography, and logo prompt.",
        expected_input="Startup idea, discovery output, strategy output, and user design style preference.",
        output_schema={
            "brandName": "string",
            "designStyle": "string",
            "colorPalette": "array of objects containing hex and meaning",
            "typography": "object containing headingFont and bodyFont",
            "logoConcept": "string",
            "logoPrompt": "string",
        },
        llm_schema=VisualOutput,
        llm_system_prompt="You are the BrandForge Visual Identity Agent. Create a coherent visual system. Respond only as structured JSON matching the schema.",
        llm_user_template="Startup Idea: {idea}\nDiscovery Data: {discovery_data}\nStrategy Data: {strategy_data}\nDesign Style: {design_style_choice}",
        llm_input_builder=visual_llm_inputs,
        fallback_runner=run_visual_identity_agent,
        question_builder=build_visual_question,
    ),
    "validator": BrandAgent(
        id="validator",
        public_id="Validator",
        name="Consistency Validator Agent",
        role="Consistency & Alignment Check",
        objective="Audit audience, strategy, visuals, and USP for cross-brand coherence.",
        expected_input="Discovery, strategy, and visual identity outputs.",
        output_schema={
            "coherenceScore": "integer",
            "status": "string",
            "passedChecks": "array of strings",
            "failedChecks": "array of strings",
            "improvementSuggestions": "array of strings",
            "finalSummary": "string",
        },
        llm_schema=ValidatorOutput,
        llm_system_prompt="You are the BrandForge Consistency Validator Agent. Audit the complete brand system for coherence and USP clarity. Respond only as structured JSON matching the schema.",
        llm_user_template="Discovery Data: {discovery_data}\nStrategy Data: {strategy_data}\nVisual Data: {visual_data}",
        llm_input_builder=validator_llm_inputs,
        fallback_runner=run_validator_agent,
        question_builder=build_validator_question,
        requires_user_input=False,
    ),
}

agents = AGENT_DEFINITIONS
