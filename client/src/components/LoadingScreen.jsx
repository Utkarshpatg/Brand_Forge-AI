import React from "react";
import { FiCheck, FiLoader } from "react-icons/fi";

export default function LoadingScreen({ currentAgent = "Discovery" }) {
  const steps = [
    { label: "Discovery Agent", id: "Discovery" },
    { label: "Strategy Agent", id: "Strategy" },
    { label: "Visual Identity Agent", id: "Visual" },
    { label: "Validator Agent", id: "Validator" },
  ];

  const getStatusIcon = (stepId) => {
    const agentOrder = ["Discovery", "Strategy", "Visual", "Validator"];
    const currentIdx = agentOrder.indexOf(currentAgent);
    const stepIdx = agentOrder.indexOf(stepId);

    if (stepIdx < currentIdx || currentAgent === "completed") {
      return <FiCheck className="h-4 w-4 text-emerald-400 font-bold" />;
    }
    if (stepIdx === currentIdx) {
      return <FiLoader className="h-4 w-4 text-indigo-400 animate-spin" />;
    }
    return <span className="h-1.5 w-1.5 rounded-full bg-slate-700" />;
  };

  return (
    <div className="flex flex-col items-center justify-center p-8 bg-slate-900/40 border border-slate-800/80 rounded-2xl backdrop-blur-sm shadow-xl max-w-md mx-auto text-center">
      <div className="relative mb-6">
        <div className="h-16 w-16 rounded-full border-4 border-indigo-500/10 border-t-indigo-500 animate-spin" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 h-10 w-10 rounded-full bg-indigo-500/20 flex items-center justify-center">
          <span className="h-2 w-2 rounded-full bg-indigo-400 animate-ping" />
        </div>
      </div>

      <h3 className="text-lg font-bold text-slate-100 font-outfit">AI Agents Working...</h3>
      <p className="text-xs text-slate-400 mt-1 font-light max-w-[280px]">
        Orchestrating multi-agent context analysis and identity drafting.
      </p>

      <div className="w-full mt-6 space-y-3 bg-slate-950 p-4 rounded-xl border border-slate-900 text-left">
        {steps.map((step) => (
          <div key={step.id} className="flex items-center justify-between text-xs">
            <span className={`font-semibold ${
              currentAgent === step.id ? "text-indigo-400 animate-pulse" : "text-slate-400"
            }`}>
              {step.label}
            </span>
            <div className="flex h-6 w-6 items-center justify-center rounded-lg bg-slate-900 border border-slate-800">
              {getStatusIcon(step.id)}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
