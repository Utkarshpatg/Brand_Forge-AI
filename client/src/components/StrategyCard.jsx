import React from "react";
import { TrendingUp, CheckCircle } from "lucide-react";

export default function StrategyCard({ voice, positioning, consistencyScore = 95 }) {
  const voiceTags = Array.isArray(voice)
    ? voice
    : voice
      ? voice.split(",").map((v) => v.trim())
      : ["Friendly", "Expert", "Bold"];

  // Radial configurations for the consistency score circular gauge
  const radius = 28;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (consistencyScore / 100) * circumference;

  return (
    <div className="card-premium rounded-2xl p-6 flex flex-col justify-between h-full">
      <div>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2 text-brand-primary font-bold">
            <TrendingUp className="h-5 w-5" />
            <span className="text-xs uppercase tracking-wider font-mono">Brand Strategy</span>
          </div>

          <div className="flex items-center space-x-1 px-2.5 py-0.5 rounded-full bg-brand-primary/10 text-brand-secondary border border-brand-primary/20 text-[10px] font-mono">
            <CheckCircle className="shrink-0 h-3 w-3" />
            <span>Aligned</span>
          </div>
        </div>

        <div className="space-y-4">
          <div>
            <span className="text-xs text-brand-text-muted font-medium uppercase tracking-wider block mb-2">Brand Voice</span>
            <div className="flex flex-wrap gap-2">
              {voiceTags.map((tag, i) => (
                <span
                  key={i}
                  className="px-2.5 py-1 rounded-md text-xs font-semibold bg-brand-surface-light border border-brand-border text-brand-secondary"
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>
          <div>
            <span className="text-xs text-brand-text-muted font-medium uppercase tracking-wider block">Brand Positioning</span>
            <p className="text-sm text-brand-text-muted font-light mt-1.5 leading-relaxed italic">
              "{positioning}"
            </p>
          </div>
        </div>
      </div>

      <div className="mt-6 pt-4 border-t border-brand-border flex items-center justify-between">
        <div>
          <h4 className="text-xs font-semibold text-brand-text-main">Consistency Score</h4>
          <p className="text-[10px] text-brand-text-muted font-light mt-0.5">Calculated across agents</p>
        </div>

        <div className="relative flex items-center justify-center h-16 w-16 shrink-0">
          <svg className="h-16 w-16 -rotate-90">
            <circle
              className="text-brand-surface-light"
              strokeWidth="4"
              stroke="currentColor"
              fill="transparent"
              r={radius}
              cx="32"
              cy="32"
            />
            <circle
              className="text-brand-secondary transition-all duration-1000 ease-out"
              strokeWidth="4"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              strokeLinecap="round"
              stroke="currentColor"
              fill="transparent"
              r={radius}
              cx="32"
              cy="32"
            />
          </svg>
          <div className="absolute flex flex-col items-center">
            <span className="text-sm font-extrabold font-mono text-brand-text-main">{consistencyScore}%</span>
          </div>
        </div>
      </div>
    </div>
  );
}
