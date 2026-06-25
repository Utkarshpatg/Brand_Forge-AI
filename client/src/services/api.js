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

export const getSystemStatus = async () => {
  const response = await axios.get(`${API_BASE_URL.replace(/\/$/, "")}/api/system`, {
    timeout: 4000,
  });
  return response.data;
};
/**
 * Sends startup idea and accumulated agent answers to the backend API.
 * The backend is the only source of workflow questions.
 */
export const generateBrand = async (idea, answers = {}, currentAgent = "", demoMode = false) => {
  void demoMode;

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
    console.warn("Backend API request failed:", error.message);
    throw error;
  }
};
