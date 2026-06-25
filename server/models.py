import importlib.util
import logging
import os
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class TargetAudience(BaseModel):
    primary: str = Field(description="Primary target audience.")
    secondary: str = Field(description="Secondary audience or key decision makers.")


class DiscoveryOutput(BaseModel):
    industry: str = Field(description="Detected industry.")
    targetAudience: TargetAudience
    customerPainPoints: list[str] = Field(description="Key target audience pain points.")
    mission: str = Field(description="Concise mission statement.")
    coreValues: list[str] = Field(description="Core brand values.")
    emotionalDrivers: list[str] = Field(description="Emotional drivers.")
    businessGoals: list[str] = Field(description="Business goals.")
    marketPosition: str = Field(description="Market position.")


class StrategyOutput(BaseModel):
    brandPersonality: list[str] = Field(description="Brand personality adjectives.")
    brandArchetype: str = Field(description="Primary brand archetype.")
    brandVoice: list[str] = Field(description="Brand voice descriptors.")
    brandTone: list[str] = Field(description="Brand tone descriptors.")
    positioningStatement: str = Field(description="Positioning statement.")
    valueProposition: str = Field(description="Value proposition.")
    keyDifferentiators: list[str] = Field(description="Key differentiators.")
    tagline: str = Field(description="Brand tagline.")


class ColorEntry(BaseModel):
    hex: str = Field(description="Hex color code including '#'.")
    meaning: str = Field(description="Design meaning behind this color.")


class TypographyPair(BaseModel):
    headingFont: str = Field(description="Heading font name.")
    bodyFont: str = Field(description="Body font name.")


class VisualOutput(BaseModel):
    brandName: str = Field(description="Generated or detected brand name.")
    designStyle: str = Field(description="Design style.")
    colorPalette: list[ColorEntry] = Field(description="Brand color palette.")
    typography: TypographyPair
    logoConcept: str = Field(description="Logo concept.")
    logoPrompt: str = Field(description="Logo generation prompt.")


class ValidatorOutput(BaseModel):
    coherenceScore: int = Field(description="Consistency score from 0 to 100.")
    status: str = Field(description="APPROVED or NEEDS_REVISION.")
    passedChecks: list[str] = Field(description="Checks that passed.")
    failedChecks: list[str] = Field(description="Checks that failed.")
    improvementSuggestions: list[str] = Field(description="Suggested improvements.")
    finalSummary: str = Field(description="Validation summary.")


def get_model_status() -> dict[str, Any]:
    groq_key = os.getenv("GROQ_API_KEY", "").strip()
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
    has_groq = bool(groq_key and "YOUR" not in groq_key.upper())
    has_gemini = bool(gemini_key and "YOUR" not in gemini_key.upper())
    groq_available = importlib.util.find_spec("langchain_groq") is not None
    gemini_available = importlib.util.find_spec("langchain_google_genai") is not None

    if has_groq and groq_available:
        return {
            "provider": "groq",
            "model": "llama3-70b-8192",
            "mode": "llm",
            "configured": True,
        }

    if has_gemini and gemini_available:
        return {
            "provider": "gemini",
            "model": "gemini-1.5-flash",
            "mode": "llm",
            "configured": True,
        }

    missing = []
    if has_groq and not groq_available:
        missing.append("langchain-groq")
    if has_gemini and not gemini_available:
        missing.append("langchain-google-genai")

    return {
        "provider": "rule-based",
        "model": "local fallback",
        "mode": "fallback",
        "configured": False,
        "reason": "Missing optional LLM package(s): " + ", ".join(missing) if missing else "No valid LLM API key configured.",
    }


def get_llm() -> Any:
    model_status = get_model_status()

    if model_status["provider"] == "groq":
        logger.info("Using Groq model: %s", model_status["model"])
        from langchain_groq import ChatGroq

        return ChatGroq(
            model_name=model_status["model"],
            groq_api_key=os.getenv("GROQ_API_KEY", "").strip(),
            temperature=0.7,
        )

    if model_status["provider"] == "gemini":
        logger.info("Using Gemini model: %s", model_status["model"])
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(
            model=model_status["model"],
            google_api_key=os.getenv("GEMINI_API_KEY", "").strip(),
            temperature=0.7,
        )

    raise ValueError(
        "No valid API keys configured. Provide GROQ_API_KEY or GEMINI_API_KEY."
    )



