agents = {
    "discovery": {
        "id": "discovery",
        "name": "Discovery Agent",
        "role": "Target Audience & Market Research",
        "objective": "Identify the primary target audience, secondary audience, and customer pain points for the startup.",
        "input": "Startup idea and user response regarding target audience.",
        "outputSchema": {
            "industry": "string",
            "targetAudience": {"primary": "string", "secondary": "string"},
            "customerPainPoints": "array of strings",
            "mission": "string",
            "coreValues": "array of strings",
            "emotionalDrivers": "array of strings",
            "businessGoals": "array of strings",
            "marketPosition": "string"
        }
    },
    "strategy": {
        "id": "strategy",
        "name": "Strategy Agent",
        "role": "Brand Voice & Positioning",
        "objective": "Define the brand personality, voice, archetype, positioning statement, and value proposition.",
        "input": "Discovery outputs and user response regarding brand personality.",
        "outputSchema": {
            "brandPersonality": "array of strings",
            "brandArchetype": "string",
            "brandVoice": "array of strings",
            "brandTone": "array of strings",
            "positioningStatement": "string",
            "valueProposition": "string",
            "keyDifferentiators": "array of strings",
            "tagline": "string"
        }
    },
    "visualIdentity": {
        "id": "visualIdentity",
        "name": "Visual Identity Agent",
        "role": "Design Direction & Aesthetics",
        "objective": "Generate color palettes, typography guidelines, and detailed logo generation prompts.",
        "input": "Discovery outputs, strategy outputs, and user response regarding design style.",
        "outputSchema": {
            "brandName": "string",
            "designStyle": "string",
            "colorPalette": "array of objects containing hex and meaning",
            "typography": "object containing headingFont and bodyFont",
            "logoConcept": "string",
            "logoPrompt": "string"
        }
    },
    "validator": {
        "id": "validator",
        "name": "Consistency Validator Agent",
        "role": "Consistency & Alignment Check",
        "objective": "Audit all brand elements (audience, voice, colors, typography, USP) to ensure cross-brand coherence and output an alignment score.",
        "input": "Discovery outputs, strategy outputs, and visual identity outputs.",
        "outputSchema": {
            "coherenceScore": "integer",
            "status": "string",
            "passedChecks": "array of strings",
            "failedChecks": "array of strings",
            "improvementSuggestions": "array of strings",
            "finalSummary": "string"
        }
    }
}
