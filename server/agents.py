import logging
from typing import Any


from models import (
    DiscoveryOutput,
    StrategyOutput,
    ValidatorOutput,
    VisualOutput,
    get_llm,
    get_model_status,
)

logger = logging.getLogger(__name__)

AGENTS = {
    "discovery": {
        "id": "discovery",
        "name": "Discovery Agent",
        "role": "Target Audience & Market Research",
        "objective": "Identify the target audience, customer pain points, mission, and market position.",
        "input": "Startup idea and user response regarding target audience.",
        "outputSchema": {
            "industry": "string",
            "targetAudience": {"primary": "string", "secondary": "string"},
            "customerPainPoints": "array of strings",
            "mission": "string",
            "coreValues": "array of strings",
            "emotionalDrivers": "array of strings",
            "businessGoals": "array of strings",
            "marketPosition": "string",
        },
    },
    "strategy": {
        "id": "strategy",
        "name": "Strategy Agent",
        "role": "Brand Voice & Positioning",
        "objective": "Define personality, voice, archetype, positioning, value proposition, and tagline.",
        "input": "Discovery output and user response regarding brand personality.",
        "outputSchema": {
            "brandPersonality": "array of strings",
            "brandArchetype": "string",
            "brandVoice": "array of strings",
            "brandTone": "array of strings",
            "positioningStatement": "string",
            "valueProposition": "string",
            "keyDifferentiators": "array of strings",
            "tagline": "string",
        },
    },
    "visualIdentity": {
        "id": "visualIdentity",
        "name": "Visual Identity Agent",
        "role": "Design Direction & Aesthetics",
        "objective": "Generate brand name, visual direction, color palette, typography, and logo prompt.",
        "input": "Startup idea, discovery output, strategy output, and user design style preference.",
        "outputSchema": {
            "brandName": "string",
            "designStyle": "string",
            "colorPalette": "array of objects containing hex and meaning",
            "typography": "object containing headingFont and bodyFont",
            "logoConcept": "string",
            "logoPrompt": "string",
        },
    },
    "validator": {
        "id": "validator",
        "name": "Consistency Validator Agent",
        "role": "Consistency & Alignment Check",
        "objective": "Audit audience, strategy, visuals, and USP for cross-brand coherence.",
        "input": "Discovery, strategy, and visual identity outputs.",
        "outputSchema": {
            "coherenceScore": "integer",
            "status": "string",
            "passedChecks": "array of strings",
            "failedChecks": "array of strings",
            "improvementSuggestions": "array of strings",
            "finalSummary": "string",
        },
    },
}

agents = AGENTS


def run_brand_pipeline(idea: str, answers: dict[str, str]) -> dict[str, Any]:
    if get_model_status()["configured"]:
        try:
            logger.info("Running LLM-backed brand agent pipeline.")
            return run_llm_agent_pipeline(idea, answers)
        except Exception:
            logger.exception("LLM agent pipeline failed; using rule-based fallback.")

    logger.info("Running rule-based brand agent pipeline.")
    return run_rule_based_agent_pipeline(idea, answers)


def run_llm_agent_pipeline(idea: str, answers: dict[str, str]) -> dict[str, Any]:
    llm = get_llm()

    discovery_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are the BrandForge Discovery Agent. Respond only as structured JSON matching the schema."),
        ("user", "Startup Idea: {idea}\nTarget Audience Choice: {audience_choice}"),
    ])
    discovery_chain = discovery_prompt | llm.with_structured_output(DiscoveryOutput)
    discovery = discovery_chain.invoke({
        "idea": idea,
        "audience_choice": answers.get("Discovery") or "Early adopters and growth-focused customers",
    }).model_dump()

    strategy_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are the BrandForge Strategy Agent. Respond only as structured JSON matching the schema."),
        ("user", "Discovery Data: {discovery_data}\nPersonality Choice: {personality_choice}"),
    ])
    strategy_chain = strategy_prompt | llm.with_structured_output(StrategyOutput)
    strategy = strategy_chain.invoke({
        "discovery_data": str(discovery),
        "personality_choice": answers.get("Strategy") or "Modern",
    }).model_dump()

    visual_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are the BrandForge Visual Identity Agent. Respond only as structured JSON matching the schema."),
        (
            "user",
            "Startup Idea: {idea}\nDiscovery Data: {discovery_data}\nStrategy Data: {strategy_data}\nDesign Style: {design_style_choice}",
        ),
    ])
    visual_chain = visual_prompt | llm.with_structured_output(VisualOutput)
    visual = visual_chain.invoke({
        "idea": idea,
        "discovery_data": str(discovery),
        "strategy_data": str(strategy),
        "design_style_choice": answers.get("Visual") or "Modern",
    }).model_dump()

    validator_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are the BrandForge Consistency Validator Agent. Respond only as structured JSON matching the schema."),
        ("user", "Discovery Data: {discovery_data}\nStrategy Data: {strategy_data}\nVisual Data: {visual_data}"),
    ])
    validator_chain = validator_prompt | llm.with_structured_output(ValidatorOutput)
    validator = validator_chain.invoke({
        "discovery_data": str(discovery),
        "strategy_data": str(strategy),
        "visual_data": str(visual),
    }).model_dump()

    final = run_orchestrator_agent(discovery, strategy, visual, validator)
    return build_agent_outputs(discovery, strategy, visual, validator, final)


def run_rule_based_agent_pipeline(idea: str, answers: dict[str, str]) -> dict[str, Any]:
    discovery = run_discovery_agent(idea, answers)
    strategy = run_strategy_agent(discovery, answers)
    visual = run_visual_identity_agent(idea, discovery, strategy, answers)
    validator = run_validator_agent(discovery, strategy, visual)
    final = run_orchestrator_agent(discovery, strategy, visual, validator)
    return build_agent_outputs(discovery, strategy, visual, validator, final)


def build_agent_outputs(
    discovery: dict[str, Any],
    strategy: dict[str, Any],
    visual: dict[str, Any],
    validator: dict[str, Any],
    final: dict[str, Any],
) -> dict[str, Any]:
    return {
        "discovery": discovery,
        "strategy": strategy,
        "visual": visual,
        "validator": validator,
        "final": final,
    }


def run_discovery_agent(idea: str, answers: dict[str, str]) -> dict[str, Any]:
    primary_audience = normalize_text(answers.get("Discovery")) or infer_audience(idea)
    industry = infer_industry(idea)

    return {
        "industry": industry,
        "targetAudience": {
            "primary": primary_audience,
            "secondary": infer_secondary_audience(primary_audience, industry),
        },
        "customerPainPoints": infer_pain_points(industry),
        "mission": f"Help {primary_audience.lower()} solve {summarize_idea(idea).lower()} with a simple, trustworthy, and outcome-focused experience.",
        "coreValues": ["Clarity", "Trust", "Momentum", "Customer empathy"],
        "emotionalDrivers": infer_emotional_drivers(idea),
        "businessGoals": [
            "Build a memorable brand identity",
            "Communicate value quickly",
            "Create trust at first touchpoint",
            "Support scalable customer acquisition",
        ],
        "marketPosition": f"{summarize_idea(idea)} for {primary_audience}",
    }


def run_strategy_agent(discovery: dict[str, Any], answers: dict[str, str]) -> dict[str, Any]:
    strategy_input = normalize_text(answers.get("Strategy")).lower()
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


def run_visual_identity_agent(
    idea: str,
    discovery: dict[str, Any],
    strategy: dict[str, Any],
    answers: dict[str, str],
) -> dict[str, Any]:
    design_style = normalize_text(answers.get("Visual")) or infer_design_style(strategy)
    color_palette = build_color_palette(design_style, strategy)
    typography = build_typography(design_style)
    brand_name = create_brand_name(idea, discovery, strategy)
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
            idea,
            discovery,
            strategy,
            design_style,
            color_palette,
            typography,
        ),
    }


def run_validator_agent(
    discovery: dict[str, Any],
    strategy: dict[str, Any],
    visual: dict[str, Any],
) -> dict[str, Any]:
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


def run_orchestrator_agent(
    discovery: dict[str, Any],
    strategy: dict[str, Any],
    visual: dict[str, Any],
    validator: dict[str, Any],
) -> dict[str, Any]:
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


def normalize_text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def infer_industry(idea: str) -> str:
    text = idea.lower()
    if has_any(text, ["fitness", "health", "wellness", "coach"]):
        return "Health and wellness technology"
    if has_any(text, ["coding", "developer", "programming", "learn"]):
        return "Education technology"
    if has_any(text, ["meal", "food", "restaurant", "delivery"]):
        return "Food and lifestyle"
    if has_any(text, ["finance", "bank", "money", "invest"]):
        return "Financial technology"
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


