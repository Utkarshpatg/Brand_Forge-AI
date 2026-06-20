import os
from typing import Any, Dict, List
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

# =====================================================================
# 1. Pydantic Structured Output Schemas
# =====================================================================

class TargetAudience(BaseModel):
    primary: str = Field(description="Primary target audience (e.g. college students, busy professionals)")
    secondary: str = Field(description="Secondary target audience or key decision makers")

class DiscoveryOutput(BaseModel):
    industry: str = Field(description="Detected industry (e.g., EdTech, HealthTech, FinTech)")
    targetAudience: TargetAudience
    customerPainPoints: List[str] = Field(description="Exactly 3 key pain points of the target audience")
    mission: str = Field(description="A concise mission statement starting with 'Help [audience] solve [problem]'")
    coreValues: List[str] = Field(description="Exactly 3-4 core values for the brand")
    emotionalDrivers: List[str] = Field(description="List of emotional drivers (e.g. Simplicity, Progress, Confidence)")
    businessGoals: List[str] = Field(description="Exactly 4 business goals for this brand")
    marketPosition: str = Field(description="A concise description of the market position")

class StrategyOutput(BaseModel):
    brandPersonality: List[str] = Field(description="3 adjectives describing the brand personality")
    brandArchetype: str = Field(description="The primary brand archetype (e.g., Sage, Creator, Ruler, Jester, Caregiver, Explorer)")
    brandVoice: List[str] = Field(description="3 descriptors of the brand's voice (e.g. Sophisticated, Visionary, Direct)")
    brandTone: List[str] = Field(description="3 descriptors of the brand's tone (e.g. Conversational, Polite, Authoritative)")
    positioningStatement: str = Field(description="A professional positioning statement matching the industry and audience")
    valueProposition: str = Field(description="A clear and unique value proposition")
    keyDifferentiators: List[str] = Field(description="Exactly 4 key differentiators of this brand")
    tagline: str = Field(description="A short, catchy, and memorable brand tagline")

class ColorEntry(BaseModel):
    hex: str = Field(description="Hex color code including '#' (e.g. #06B6D4)")
    meaning: str = Field(description="The psychological/design meaning behind selecting this color")

class TypographyPair(BaseModel):
    headingFont: str = Field(description="Name of heading font from Google Fonts (e.g., Orbitron, Playfair Display, Inter)")
    bodyFont: str = Field(description="Name of body font from Google Fonts (e.g., Outfit, Montserrat, Poppins)")

class VisualOutput(BaseModel):
    brandName: str = Field(description="A creative, 1-2 word brand name generated dynamically based on the startup idea")
    designStyle: str = Field(description="The chosen design style (e.g., modern, futuristic, minimalist, luxury)")
    colorPalette: List[ColorEntry] = Field(description="Exactly 4 colors (primary, secondary, neutral/background, accent)")
    typography: TypographyPair
    logoConcept: str = Field(description="A short description of the visual logo mark concept")
    logoPrompt: str = Field(description="A detailed logo generation prompt for DALL-E or Midjourney")

class ValidatorOutput(BaseModel):
    coherenceScore: int = Field(description="Consistency score from 0 to 100")
    status: str = Field(description="APPROVED if score >= 75 else NEEDS_REVISION")
    passedChecks: List[str] = Field(description="List of checks that passed (e.g. 'Audience aligns with voice')")
    failedChecks: List[str] = Field(description="List of checks that failed or need improvement")
    improvementSuggestions: List[str] = Field(description="List of actionable suggestions for improvement")
    finalSummary: str = Field(description="Overall validation report summary")

# =====================================================================
# 2. LLM Client Initialization
# =====================================================================

def get_llm() -> Any:
    # Read keys (making sure empty placeholders are ignored)
    groq_key = os.getenv("GROQ_API_KEY", "").strip()
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()

    if groq_key and "YOUR" not in groq_key:
        print("⚡ [BrandForge AI] Using Groq API for multi-agent generation.")
        from langchain_groq import ChatGroq
        return ChatGroq(model_name="llama3-70b-8192", groq_api_key=groq_key, temperature=0.7)
    
    elif gemini_key and "YOUR" not in gemini_key:
        print("⚡ [BrandForge AI] Using Google Gemini API for multi-agent generation.")
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=gemini_key, temperature=0.7)
    
    else:
        raise ValueError(
            "No valid API keys configured in .env. "
            "Please provide a valid GROQ_API_KEY or GEMINI_API_KEY."
        )

# =====================================================================
# 3. Sequential Multi-Agent Workflow Implementation
# =====================================================================

def run_agent_pipeline_llm(idea: str, answers: Dict[str, str]) -> Dict[str, Any]:
    llm = get_llm()

    # --- Step 1: Discovery Agent ---
    discovery_prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are the BrandForge Discovery Agent. Your role is Target Audience & Market Research.\n"
            "Analyze the startup idea and user response regarding target audience to produce the output details.\n"
            "Respond ONLY as a structured JSON object matching the requested schema."
        )),
        ("user", "Startup Idea: {idea}\nUser's Target Audience Choice: {audience_choice}")
    ])
    discovery_chain = discovery_prompt | llm.with_structured_output(DiscoveryOutput)
    audience_choice = answers.get("Discovery") or "Early adopters and growth-focused customers"
    
    print("🤖 Agent 1 [Discovery] is analyzing idea & audience...")
    discovery_res = discovery_chain.invoke({"idea": idea, "audience_choice": audience_choice})
    discovery = discovery_res.model_dump()

    # --- Step 2: Strategy Agent ---
    strategy_prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are the BrandForge Strategy Agent. Your role is Brand Voice & Positioning.\n"
            "Based on the Discovery analysis and the user's brand personality preference, establish the brand strategy details.\n"
            "Respond ONLY as a structured JSON object matching the requested schema."
        )),
        ("user", "Discovery Data: {discovery_data}\nUser's Brand Personality Choice: {personality_choice}")
    ])
    strategy_chain = strategy_prompt | llm.with_structured_output(StrategyOutput)
    personality_choice = answers.get("Strategy") or "Modern"
    
    print("🤖 Agent 2 [Strategy] is defining personality & positioning...")
    strategy_res = strategy_chain.invoke({
        "discovery_data": str(discovery),
        "personality_choice": personality_choice
    })
    strategy = strategy_res.model_dump()

    # --- Step 3: Visual Identity Agent ---
    visual_prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are the BrandForge Visual Identity Agent. Your role is Design Direction & Aesthetics.\n"
            "Based on the startup idea, Discovery outputs, Strategy outputs, and user design style preference, generate visual design guidelines.\n"
            "Note: If the startup already has a distinct, defined name in the startup idea, use that. Otherwise, generate a creative 1-2 word brand name.\n"
            "Respond ONLY as a structured JSON object matching the requested schema."
        )),
        ("user", (
            "Startup Idea: {idea}\n"
            "Discovery Data: {discovery_data}\n"
            "Strategy Data: {strategy_data}\n"
            "User's Design Style Choice: {design_style_choice}"
        ))
    ])
    visual_chain = visual_prompt | llm.with_structured_output(VisualOutput)
    design_style_choice = answers.get("Visual") or "Modern"
    
    print("🤖 Agent 3 [Visual Identity] is choosing brand name, colors, and typography...")
    visual_res = visual_chain.invoke({
        "idea": idea,
        "discovery_data": str(discovery),
        "strategy_data": str(strategy),
        "design_style_choice": design_style_choice
    })
    visual = visual_res.model_dump()

    # --- Step 4: Consistency Validator Agent ---
    validator_prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are the BrandForge Consistency Validator Agent. Your role is Brand Coherence Audit.\n"
            "Evaluate alignment between the Discovery data, Strategy data, and Visual Identity details.\n"
            "Verify that the brand has a clear Unique Selling Point (USP) — what sets it apart from competitors — and check that this USP is logically reflected in the value proposition and key differentiators.\n"
            "Calculate a coherence score (0-100) based on how well the colors, typography, brand name, "
            "tagline, and USP fit the target audience, mission, and voice.\n"
            "Respond ONLY as a structured JSON object matching the requested schema."
        )),
        ("user", (
            "Discovery Data: {discovery_data}\n"
            "Strategy Data: {strategy_data}\n"
            "Visual Data: {visual_data}"
        ))
    ])
    validator_chain = validator_prompt | llm.with_structured_output(ValidatorOutput)
    
    print("🤖 Agent 4 [Validator] is performing consistency audit...")
    validator_res = validator_chain.invoke({
        "discovery_data": str(discovery),
        "strategy_data": str(strategy),
        "visual_data": str(visual)
    })
    validator = validator_res.model_dump()

    # --- Step 5: Final Orchestration ---
    final = {
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

    print("✅ Multi-agent pipeline generation completed successfully!")
    return {
        "discovery": discovery,
        "strategy": strategy,
        "visual": visual,
        "validator": validator,
        "final": final,
    }
