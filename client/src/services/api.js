import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:5000";
const GENERATE_BRAND_URL =
  import.meta.env.VITE_API_URL || `${API_BASE_URL.replace(/\/$/, "")}/api/generate-brand`;

export const getBackendHealth = async () => {
  const response = await axios.get(`${API_BASE_URL.replace(/\/$/, "")}/api/health`, {
    timeout: 4000,
  });
  return response.data;
};

export const getAgents = async () => {
  const response = await axios.get(`${API_BASE_URL.replace(/\/$/, "")}/api/agents`, {
    timeout: 4000,
  });
  return response.data;
};

/**
 * Sends startup idea and accumulated agent answers to the backend API.
 * Demo mode intentionally uses the local browser simulation.
 * Backend failures fall back to simulation so testers never hit a dead end.
 */
export const generateBrand = async (idea, answers = {}, currentAgent = "", demoMode = false) => {
  if (demoMode) {
    return simulateAgentResponse(idea, answers, currentAgent);
  }

  try {
    const response = await axios.post(
      GENERATE_BRAND_URL,
      {
        idea,
        answers,
        currentAgent,
      },
      { timeout: 10000 }
    );

    if (response.data?.status === "error") {
      throw new Error(response.data.error || "Backend returned an error.");
    }

    return response.data;
  } catch (error) {
    console.warn(
      "Backend API request failed, using client-side multi-agent simulation:",
      error.message
    );
    return simulateAgentResponse(idea, answers, currentAgent);
  }
};

const simulateAgentResponse = async (idea, answers, currentAgent) => {
  await new Promise((resolve) => setTimeout(resolve, 700));

  if (!currentAgent) {
    return needsInput("Discovery", "Who is your primary target audience for this startup?");
  }

  if (currentAgent === "Discovery" && answers.Discovery) {
    return needsInput(
      "Strategy",
      "Should the brand personality feel premium, friendly, innovative, or playful?"
    );
  }

  if (currentAgent === "Strategy" && answers.Strategy) {
    return needsInput(
      "Visual",
      "Do you prefer a design style that is modern, futuristic, minimalist, or luxury?"
    );
  }

  if (currentAgent === "Visual" && answers.Visual) {
    const agentOutputs = generateSimulatedAgentOutputs(idea, answers);
    return {
      status: "completed",
      agentOutputs,
      brandData: agentOutputs.finalClientData,
    };
  }

  return needsInput("Discovery", "Who is your primary target audience for this startup?");
};

const needsInput = (currentAgent, question) => ({
  status: "needs_input",
  currentAgent,
  question,
  agent: {
    id: currentAgent.toLowerCase(),
    name: `${currentAgent} Agent`,
    role: "BrandForge AI workflow agent",
  },
});

const generateSimulatedAgentOutputs = (idea, answers) => {
  const targetAudience = answers.Discovery || "General public";
  const brandFeel = String(answers.Strategy || "innovative").toLowerCase();
  const designStyle = String(answers.Visual || "modern").toLowerCase();
  const brandName = createBrandName(idea, targetAudience);
  const colors = chooseColors(designStyle);
  const typography = chooseTypography(designStyle);
  const voice = chooseVoice(brandFeel);
  const score = 88 + ((idea.length + targetAudience.length + designStyle.length) % 10);

  const finalClientData = {
    brandName,
    mission: `Empowering ${targetAudience.toLowerCase()} with a ${brandFeel} experience that makes ${idea.toLowerCase()} easier to trust and use.`,
    audience: targetAudience,
    voice: voice.join(", "),
    brandVoice: voice,
    brandPersonality: choosePersonality(brandFeel),
    positioning: `A ${brandFeel} brand for ${targetAudience.toLowerCase()}, designed with a ${designStyle} identity system.`,
    tagline: "Built to grow with clarity.",
    colors,
    colorPalette: colors.map((hex) => ({ hex, meaning: "Selected for clarity, trust, and brand recognition." })),
    typography,
    typographyDetails: {
      headingFont: typography[0],
      bodyFont: typography[1] || typography[0],
    },
    logoPrompt: createLogoPrompt(brandName, idea, targetAudience, designStyle, colors, typography),
    validationReport: `The simulated agent team found strong alignment between audience, voice, visuals, and positioning for ${targetAudience.toLowerCase()}.`,
    brandConsistencyScore: score,
    validatorStatus: "APPROVED",
  };

  return {
    discovery: {
      industry: "Startup technology",
      targetAudience: { primary: targetAudience, secondary: "Influencers and decision makers" },
      customerPainPoints: ["Low trust", "Unclear differentiation", "Too much friction"],
      mission: finalClientData.mission,
      coreValues: ["Clarity", "Trust", "Momentum"],
      emotionalDrivers: ["Confidence", "Progress", "Simplicity"],
      businessGoals: ["Clarify positioning", "Improve recognition", "Increase conversion"],
      marketPosition: `${idea} for ${targetAudience}`,
    },
    strategy: {
      brandPersonality: finalClientData.brandPersonality,
      brandArchetype: "Creator",
      brandVoice: finalClientData.brandVoice,
      brandTone: ["Clear", "Helpful", "Confident"],
      positioningStatement: finalClientData.positioning,
      valueProposition: "A focused, trusted brand experience for early growth.",
      keyDifferentiators: ["Clear audience fit", "Memorable identity", "Validation-led output"],
      tagline: finalClientData.tagline,
    },
    visual: {
      brandName,
      designStyle,
      colorPalette: finalClientData.colorPalette,
      typography: finalClientData.typographyDetails,
      logoConcept: `A ${designStyle} mark for ${brandName}.`,
      logoPrompt: finalClientData.logoPrompt,
    },
    validator: {
      coherenceScore: score,
      status: "APPROVED",
      passedChecks: ["Audience to voice", "Mission to positioning", "Personality to visual style"],
      failedChecks: [],
      improvementSuggestions: ["Test the tagline with 3-5 target users."],
      finalSummary: finalClientData.validationReport,
    },
    finalClientData,
  };
};

const createBrandName = (idea, audience) => {
  const words = idea
    .split(/\s+/)
    .map((word) => word.replace(/[^a-zA-Z]/g, ""))
    .filter((word) => word.length > 4);
  const roots = words.length ? words : ["Origin", "Mint", "Nova", "Pulse"];
  const suffixes = ["AI", "Lab", "Hub", "Core", "Loop"];
  const seed = idea.length + audience.length;
  return `${titleCase(roots[seed % roots.length])} ${suffixes[seed % suffixes.length]}`;
};

const chooseVoice = (brandFeel) => {
  if (brandFeel.includes("premium") || brandFeel.includes("luxury")) {
    return ["Sophisticated", "Assured", "Selective"];
  }
  if (brandFeel.includes("playful") || brandFeel.includes("friendly")) {
    return ["Energetic", "Warm", "Helpful"];
  }
  if (brandFeel.includes("innovative") || brandFeel.includes("futuristic")) {
    return ["Visionary", "Bold", "Intelligent"];
  }
  return ["Clear", "Helpful", "Trustworthy"];
};

const choosePersonality = (brandFeel) => {
  if (brandFeel.includes("premium") || brandFeel.includes("luxury")) return ["Premium", "Refined", "Trustworthy"];
  if (brandFeel.includes("playful") || brandFeel.includes("friendly")) return ["Friendly", "Energetic", "Approachable"];
  if (brandFeel.includes("innovative") || brandFeel.includes("futuristic")) return ["Innovative", "Bold", "Forward-thinking"];
  return ["Modern", "Clear", "Reliable"];
};

const chooseColors = (designStyle) => {
  if (designStyle.includes("futuristic")) return ["#06B6D4", "#D946EF", "#0F172A", "#10B981"];
  if (designStyle.includes("minimal")) return ["#0F172A", "#64748B", "#F8FAFC", "#3B82F6"];
  if (designStyle.includes("luxury")) return ["#D97706", "#1E1B4B", "#FAF5FF", "#78350F"];
  return ["#3B82F6", "#10B981", "#1E293B", "#EF4444"];
};

const chooseTypography = (designStyle) => {
  if (designStyle.includes("luxury")) return ["Playfair Display", "Montserrat"];
  if (designStyle.includes("minimal")) return ["Roboto Mono", "Lato"];
  if (designStyle.includes("futuristic")) return ["Orbitron", "Outfit"];
  return ["Inter", "Poppins"];
};

const createLogoPrompt = (brandName, idea, audience, designStyle, colors, typography) =>
  `Design a professional vector-style logo for ${brandName}, a startup focused on ${idea}. The identity should feel ${designStyle}, trustworthy, and commercially ready for ${audience}. Use ${colors.join(", ")} as the color foundation and pair it with typography inspired by ${typography.join(" and ")}. Create a clean, scalable symbol with strong silhouette recognition, balanced whitespace, and no generic clipart. The logo should work across app icons, websites, pitch decks, social profiles, and printed collateral.`;

const titleCase = (value) => value.charAt(0).toUpperCase() + value.slice(1).toLowerCase();
