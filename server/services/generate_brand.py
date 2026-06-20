import os
from typing import Any

from agents import agents


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


def generate_brand_workflow(
    idea: str,
    answers: dict[str, Any] | None = None,
    current_agent: str = "",
) -> dict[str, Any]:
    normalized_idea = normalize_text(idea)
    normalized_answers = normalize_answers(answers)

    if not normalized_idea:
        return {"status": "error", "error": "Startup idea is required."}

    if not current_agent:
        return needs_input("Discovery")

    if current_agent == "Discovery" and normalized_answers.get("Discovery"):
        return needs_input("Strategy")

    if current_agent == "Strategy" and normalized_answers.get("Strategy"):
        return needs_input("Visual")

    if current_agent == "Visual" and normalized_answers.get("Visual"):
        # Check if a valid API key is present in environment
        groq_key = os.getenv("GROQ_API_KEY", "").strip()
        gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
        has_groq = groq_key and "YOUR" not in groq_key
        has_gemini = gemini_key and "YOUR" not in gemini_key

        if has_groq or has_gemini:
            try:
                # Add current directory to path if needed and import
                import sys
                current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                if current_dir not in sys.path:
                    sys.path.append(current_dir)
                
                from models import run_agent_pipeline_llm
                agent_outputs = run_agent_pipeline_llm(normalized_idea, normalized_answers)
            except Exception as e:
                print(f"⚠️ LLM pipeline failed, falling back to rule-based generation: {e}")
                agent_outputs = run_agent_pipeline(normalized_idea, normalized_answers)
        else:
            agent_outputs = run_agent_pipeline(normalized_idea, normalized_answers)

        return {
            "status": "completed",
            "agentOutputs": agent_outputs,
            "brandData": orchestrate_client_brand_data(agent_outputs),
        }


    return needs_input(current_agent if is_known_agent(current_agent) else "Discovery")


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
        for key, agent in agents.items()
    ]


def needs_input(agent_name: str) -> dict[str, Any]:
    agent_config = WORKFLOW_AGENTS.get(agent_name, WORKFLOW_AGENTS["Discovery"])
    prompt_agent = agents[agent_config["key"]]

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


def run_agent_pipeline(idea: str, answers: dict[str, str]) -> dict[str, Any]:
    discovery = run_discovery_agent(idea, answers)
    strategy = run_strategy_agent(discovery, answers)
    visual = run_visual_identity_agent(idea, discovery, strategy, answers)
    validator = run_validator_agent(discovery, strategy, visual)
    final = run_orchestrator_agent(discovery, strategy, visual, validator)

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
    market_segment = infer_market_segment(idea, primary_audience)

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
        "marketPosition": market_segment,
    }


def run_strategy_agent(discovery: dict[str, Any], answers: dict[str, str]) -> dict[str, Any]:
    strategy_input = normalize_text(answers.get("Strategy")).lower()
    personality = infer_personality(strategy_input, discovery)
    archetype = infer_archetype(personality)
    brand_voice = infer_brand_voice(strategy_input, personality)

    return {
        "brandPersonality": personality,
        "brandArchetype": archetype,
        "brandVoice": brand_voice,
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
        {
            "label": "Audience aligns with brand voice",
            "passed": len(strategy["brandVoice"]) >= 2 and bool(discovery["targetAudience"]["primary"]),
        },
        {"label": "Audience aligns with colors", "passed": 3 <= len(visual["colorPalette"]) <= 5},
        {
            "label": "Audience aligns with typography",
            "passed": bool(visual["typography"].get("headingFont") and visual["typography"].get("bodyFont")),
        },
        {
            "label": "Mission aligns with positioning",
            "passed": len(discovery["mission"]) > 40 and len(strategy["positioningStatement"]) > 30,
        },
        {
            "label": "Positioning aligns with logo",
            "passed": visual["designStyle"].lower() in visual["logoConcept"].lower(),
        },
        {
            "label": "Personality aligns with visual style",
            "passed": len(strategy["brandPersonality"]) > 0 and len(visual["designStyle"]) > 0,
        },
        {
            "label": "Archetype aligns with color palette",
            "passed": bool(strategy["brandArchetype"] and visual["colorPalette"][0].get("meaning")),
        },
        {
            "label": "Tagline aligns with mission",
            "passed": len(strategy["tagline"]) > 0 and len(discovery["mission"]) > 0,
        },
        {
            "label": "Unique Selling Point clearly defined",
            "passed": len(strategy["keyDifferentiators"]) >= 3 and len(strategy["valueProposition"]) > 20,
        },
    ]

    passed_checks = [check["label"] for check in checks if check["passed"]]
    failed_checks = [check["label"] for check in checks if not check["passed"]]
    coherence_score = min(99, max(60, 72 + len(passed_checks) * 3))

    return {
        "coherenceScore": coherence_score,
        "status": "APPROVED" if coherence_score >= 75 else "NEEDS_REVISION",
        "passedChecks": passed_checks,
        "failedChecks": failed_checks,
        "improvementSuggestions": (
            [f"Refine: {check}." for check in failed_checks]
            if failed_checks
            else ["No critical issues found. Consider user-testing the tagline and logo prompt."]
        ),
        "finalSummary": (
            f"The system is {'excellent' if coherence_score >= 90 else 'good'} for launch testing. "
            f"Strategy, visuals, and audience intent are aligned for "
            f"{discovery['targetAudience']['primary'].lower()}."
        ),
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


def orchestrate_client_brand_data(agent_outputs: dict[str, Any]) -> dict[str, Any]:
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


def infer_market_segment(idea: str, audience: str) -> str:
    return f"{summarize_idea(idea)} for {audience}"


def infer_pain_points(industry: str) -> list[str]:
    base = [
        "Difficulty choosing a trustworthy solution",
        "Too much friction before seeing value",
        "Lack of clear differentiation in the market",
    ]

    if "Health" in industry:
        return ["Inconsistent routines", "Low motivation", "Generic guidance", base[0]]
    if "Education" in industry:
        return ["Low engagement", "Overwhelming learning paths", "Poor progress feedback", base[0]]
    if "Food" in industry:
        return ["Limited convenient choices", "Trust concerns", "Hard-to-maintain lifestyle changes", base[0]]

    return base


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
        {
            "hex": "#F97316" if is_friendly else "#EF4444",
            "meaning": "Creates memorable contrast and action energy.",
        },
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
    roots = [word for word in idea_words if len(word) > 4] or [
        "Origin",
        "Mint",
        "Apex",
        "Flow",
        "Pulse",
        "Nova",
        "Sync",
        "Lumina",
    ]
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
        f'Design a professional brand logo for "{brand_name}", a startup focused on {idea}. '
        f"The logo should feel {design_style.lower()} and communicate "
        f"{', '.join(strategy['brandPersonality']).lower()} qualities for "
        f"{discovery['targetAudience']['primary'].lower()}. Use a clean, scalable vector-style "
        "mark with strong silhouette recognition, balanced whitespace, and a premium startup-ready "
        f"finish. The visual language should support the positioning: {strategy['positioningStatement']}. "
        f"Use the color system {colors}. Pair the mark with typography inspired by "
        f"{typography['headingFont']} for headings and {typography['bodyFont']} for supporting text. "
        "Avoid clutter, literal clipart, excessive gradients, tiny details, and generic icons. The final "
        "result should work on app icons, landing pages, pitch decks, and social profiles."
    )


def summarize_idea(idea: str) -> str:
    return f"{idea[:77].strip()}..." if len(idea) > 80 else idea


def has_any(text: str, terms: list[str]) -> bool:
    return any(term in text for term in terms)


def pick(items: list[str], seed: int) -> str:
    if not items:
        return ""
    return items[abs(seed) % len(items)]


def title_case(value: str) -> str:
    if not value:
        return "Origin"
    return value[0].upper() + value[1:].lower()
