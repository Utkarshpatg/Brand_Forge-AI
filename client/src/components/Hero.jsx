import React from "react";
import { Layers, Shield, Palette, Target } from "lucide-react";

export default function Hero() {
  const agents = [
    { icon: <Layers className="text-brand-secondary" />, label: "Discovery Agent", desc: "Audience Profiling" },
    { icon: <Target className="text-brand-primary" />, label: "Strategy Agent", desc: "Voice & Positioning" },
    { icon: <Palette className="text-brand-secondary" />, label: "Visual Agent", desc: "Colors & Typography" },
    { icon: <Shield className="text-brand-primary" />, label: "Validator Agent", desc: "Consistency Report" },
  ];

  return (
    <div className="relative overflow-hidden pt-12 pb-8 text-center">
  
      <div className="absolute top-0 left-1/2 -z-10 h-72 w-72 -translate-x-1/2 rounded-full bg-brand-primary/5 blur-[80px]" />
      <div className="absolute top-10 left-1/3 -z-10 h-48 w-48 rounded-full bg-brand-secondary/4 blur-[60px]" />

      <h2 className="mx-auto max-w-4xl text-4xl font-jakarta font-extrabold tracking-tight sm:text-6xl text-brand-text-main">
        BrandForge <span className="hero-gradient-text">AI</span>
      </h2>
      <p className="mx-auto mt-4 max-w-2xl text-xl sm:text-2xl font-jakarta font-bold tracking-tight text-brand-secondary/90">
        Turn Your Startup Idea Into A Complete Brand Identity
      </p>
      
      <p className="mx-auto mt-3 max-w-xl text-sm sm:text-base text-brand-text-muted leading-relaxed font-light">
        Deploy a collaborative team of intelligent AI Agents that ask context-aware questions, shape positioning, design typography and palettes, and validate compliance in real-time.
      </p>

      <div className="mx-auto mt-8 grid max-w-4xl grid-cols-2 gap-4 px-4 sm:grid-cols-4 sm:px-6">
        {agents.map((agent, i) => (
          <div 
            key={i} 
            className="flex items-center space-x-3 rounded-xl border border-brand-border bg-brand-surface/60 p-3 backdrop-blur-sm transition-all duration-300 hover:border-brand-primary/20 hover:bg-brand-surface text-left hover:translate-y-[-2px]"
          >
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-brand-surface-light text-lg flex items-center justify-center">
              {agent.icon}
            </div>
            <div>
              <h4 className="text-xs font-semibold text-brand-text-main">{agent.label}</h4>
              <p className="text-[10px] text-brand-text-muted">{agent.desc}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
