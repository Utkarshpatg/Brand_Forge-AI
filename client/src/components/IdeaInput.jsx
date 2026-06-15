import React from "react";
import { ArrowRight, Zap, BookOpen, Heart, Anchor } from "lucide-react";

export default function IdeaInput({ idea, setIdea, onSubmit, loading }) {
  const suggestions = [
    { text: "AI-powered fitness coach for busy professionals", icon: <Heart className="h-3.5 w-3.5 text-brand-primary" /> },
    { text: "An AI platform that teaches coding through gamification", icon: <BookOpen className="h-3.5 w-3.5 text-brand-secondary" /> },
    { text: "A luxury plant-based meal delivery service for families", icon: <Anchor className="h-3.5 w-3.5 text-amber-500" /> },
  ];

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (idea.trim()) onSubmit();
    }
  };

  return (
    <div className="mx-auto max-w-3xl px-4 sm:px-6">
      <div className="card-premium rounded-2xl p-6">
        <label htmlFor="startup-idea" className="block text-sm font-semibold text-brand-text-main mb-2 flex items-center space-x-1.5">
          <Zap className="h-4 w-4 text-brand-primary animate-pulse" style={{ animationDuration: '3s' }} />
          <span>Define Your Startup Idea</span>
        </label>
        
        <textarea
          id="startup-idea"
          rows="4"
          value={idea}
          onChange={(e) => setIdea(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={loading}
          className="w-full rounded-xl border border-brand-border bg-brand-surface-light/40 p-4 text-sm text-brand-text-main placeholder-brand-text-muted/40 focus:border-brand-primary/50 focus:outline-none focus:ring-1 focus:ring-brand-primary/30 transition-all disabled:opacity-50"
          placeholder="Describe your startup idea in detail..."
        />
        
        <div className="mt-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div className="flex flex-col space-y-1.5">
            <span className="text-xs font-semibold text-brand-text-muted uppercase tracking-wider">Need inspiration? Try:</span>
            <div className="flex flex-wrap gap-2">
              {suggestions.map((s, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => setIdea(s.text)}
                  disabled={loading}
                  className="flex items-center space-x-1 px-3 py-1.5 rounded-lg border border-brand-border bg-brand-surface hover:bg-brand-surface-light text-xs text-brand-text-muted hover:text-brand-text-main transition duration-200 cursor-pointer"
                >
                  {s.icon}
                  <span className="truncate max-w-[200px] sm:max-w-[300px]">{s.text}</span>
                </button>
              ))}
            </div>
          </div>

          <div className="shrink-0 flex items-end justify-end">
            <button
              onClick={onSubmit}
              disabled={!idea.trim() || loading}
              className="w-full sm:w-auto relative inline-flex items-center justify-center space-x-2 rounded-xl btn-primary-warm px-5 py-3 text-sm font-bold text-white shadow-lg active:scale-[0.98] transition-all disabled:opacity-50 disabled:pointer-events-none disabled:shadow-none cursor-pointer"
            >
              {loading ? (
                <>
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  <span>Spawning Agents...</span>
                </>
              ) : (
                <>
                  <span>Generate Brand</span>
                  <ArrowRight className="h-4 w-4" />
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
