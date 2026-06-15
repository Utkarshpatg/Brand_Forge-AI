import React, { useState } from "react";
import { Image, Copy, Check, Eye, Code, Loader2 } from "lucide-react";

export default function LogoPromptCard({ logoPrompt }) {
  const [copied, setCopied] = useState(false);
  const [activeTab, setActiveTab] = useState("prompt"); // "prompt" | "visualize"
  const [imgLoaded, setImgLoaded] = useState(false);
  const [imgError, setImgError] = useState(false);

  const copyToClipboard = () => {
    if (!logoPrompt) return;
    navigator.clipboard?.writeText?.(logoPrompt);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const defaultPrompt = "Minimal futuristic logo with fitness and AI elements...";
  const promptText = logoPrompt || defaultPrompt;

  // Use Pollinations AI free image generation URL with the customized prompt
  const imageUrl = `https://image.pollinations.ai/prompt/${encodeURIComponent(
    promptText + ", high quality vector logo, flat design, white background"
  )}?width=400&height=400&nologo=true&private=true&seed=99`;

  const handleTabChange = (tab) => {
    setActiveTab(tab);
    if (tab === "visualize") {
      setImgLoaded(false);
      setImgError(false);
    }
  };

  return (
    <div className="card-premium rounded-2xl p-6 flex flex-col justify-between h-full min-h-[360px]">
      <div>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2 text-brand-primary font-bold">
            <Image className="h-5 w-5" />
            <span className="text-xs uppercase tracking-wider font-mono">Logo Hub (Groq AI)</span>
          </div>

          {activeTab === "prompt" && (
            <button
              onClick={copyToClipboard}
              className="flex items-center space-x-1 px-2.5 py-1 text-xs rounded-md bg-brand-surface-light border border-brand-border text-brand-text-muted hover:text-brand-text-main transition cursor-pointer"
            >
              {copied ? (
                <>
                  <Check className="h-3.5 w-3.5 text-emerald-400" />
                  <span className="text-emerald-400 font-semibold">Copied</span>
                </>
              ) : (
                <>
                  <Copy className="h-3.5 w-3.5" />
                  <span>Copy Prompt</span>
                </>
              )}
            </button>
          )}
        </div>

        <div className="min-h-[190px] flex flex-col justify-center">
          {activeTab === "prompt" ? (
            /* Tab 1: Code prompt box */
            <div className="relative rounded-xl border border-brand-border bg-brand-surface-light p-4 font-mono text-xs text-brand-text-main leading-relaxed max-h-48 overflow-y-auto select-all w-full">
              <div className="flex items-center space-x-1.5 mb-2 border-b border-brand-border pb-1.5 text-[10px] text-brand-text-muted font-semibold uppercase select-none">
                <span className="h-2 w-2 rounded-full bg-red-500" />
                <span className="h-2 w-2 rounded-full bg-yellow-500" />
                <span className="h-2 w-2 rounded-full bg-green-500" />
                <span className="ml-2 font-mono">DALL-E / Midjourney Prompt</span>
              </div>
              <p className="whitespace-pre-wrap">{promptText}</p>
            </div>
          ) : (
            /* Tab 2: Visual image box */
            <div className="relative rounded-xl border border-brand-border bg-brand-surface-light overflow-hidden flex items-center justify-center h-44 w-full">
              {!imgLoaded && !imgError && (
                <div className="absolute inset-0 flex flex-col items-center justify-center bg-brand-surface/90 text-brand-text-muted z-10 space-y-2">
                  <Loader2 className="h-6 w-6 text-brand-primary animate-spin" />
                  <span className="text-[10px] font-mono tracking-widest text-brand-secondary">GROQ AI RENDERING...</span>
                </div>
              )}

              {imgError && (
                <div className="absolute inset-0 flex items-center justify-center bg-brand-surface text-xs text-rose-400 p-4 text-center">
                  Failed to render visual. Try toggling back to prompt or check your connection.
                </div>
              )}

              <img
                src={imageUrl}
                alt="AI Generated Brand Logo"
                onLoad={() => setImgLoaded(true)}
                onError={() => {
                  setImgLoaded(true);
                  setImgError(true);
                }}
                className={`max-h-full max-w-full object-contain rounded-lg transition-opacity duration-500 ${
                  imgLoaded && !imgError ? "opacity-100" : "opacity-0"
                }`}
              />
            </div>
          )}
        </div>
      </div>
      <div className="mt-5 pt-3 border-t border-brand-border">
        <div className="flex bg-brand-surface-light p-1 rounded-lg border border-brand-border">
          <button
            onClick={() => handleTabChange("prompt")}
            className={`flex-1 flex items-center justify-center space-x-1.5 py-1.5 rounded-md text-xs font-semibold tracking-wide transition-all cursor-pointer ${
              activeTab === "prompt"
                ? "bg-brand-primary text-white shadow-md"
                : "text-brand-text-muted hover:text-brand-text-main"
            }`}
          >
            <Code className="h-3.5 w-3.5" />
            <span>Prompt</span>
          </button>
          
          <button
            onClick={() => handleTabChange("visualize")}
            className={`flex-1 flex items-center justify-center space-x-1.5 py-1.5 rounded-md text-xs font-semibold tracking-wide transition-all cursor-pointer ${
              activeTab === "visualize"
                ? "bg-brand-primary text-white shadow-md"
                : "text-brand-text-muted hover:text-brand-text-main"
            }`}
          >
            <Eye className="h-3.5 w-3.5" />
            <span>Visualize</span>
          </button>
        </div>
      </div>
    </div>
  );
}
