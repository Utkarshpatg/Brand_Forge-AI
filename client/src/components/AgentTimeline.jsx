import React from "react";
import { Check,  Compass, Award, Eye, Settings } from "lucide-react";

export default function AgentTimeline({ currentAgent, answers }) {
  const steps = [
    {
      id: "Discovery",
      name: "Discovery Agent",
      role: "Audience & Research",
      desc: "Analyzing target demographics",
      icon: <Compass className="h-5 w-5" />,
      thinkingText: "Discovery Agent is analyzing target demographics...",
    },
    {
      id: "Strategy",
      name: "Strategy Agent",
      role: "Voice & Positioning",
      desc: "Defining brand characteristics",
      icon: <Award className="h-5 w-5" />,
      thinkingText: "Strategy Agent is defining positioning and voice...",
    },
    {
      id: "Visual",
      name: "Visual Agent",
      role: "Palette & Typography",
      desc: "Generating identity assets",
      icon: <Eye className="h-5 w-5" />,
      thinkingText: "Visual Agent is generating palettes and typography...",
    },
    {
      id: "Validator",
      name: "Validator Agent",
      role: "Consistency check",
      desc: "Ensuring alignment rules",
      icon: <Settings className="h-5 w-5" />,
      thinkingText: "Validator Agent is checking visual and conceptual consistency...",
    },
  ];

  // Helper to determine status of step
  const getStepStatus = (stepId, index) => {
    // If brand generation is completed
    if (currentAgent === "completed") {
      return "completed";
    }

    const agentOrder = ["Discovery", "Strategy", "Visual", "Validator"];
    const currentIndex = agentOrder.indexOf(currentAgent);
    const stepIndex = agentOrder.indexOf(stepId);

    if (stepIndex < currentIndex) {
      return "completed";
    } else if (stepIndex === currentIndex) {
      return "active";
    } else {
      return "upcoming";
    }
  };

  // Calculate percentage progress
  const getPercentage = () => {
    if (currentAgent === "completed") return 100;
    if (currentAgent === "Validator") return 75;
    if (currentAgent === "Visual") return 50;
    if (currentAgent === "Strategy") return 25;
    if (currentAgent === "Discovery") return 10;
    return 0;
  };

  const activeStep = steps.find(s => s.id === currentAgent) || steps[0];

  return (
    <div className="card-premium rounded-2xl p-6 flex flex-col h-full">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-sm font-bold text-brand-text-main uppercase tracking-wider flex items-center space-x-2">
          <span>Agent Timeline</span>
        </h3>
        <span className="text-xs font-mono font-bold bg-brand-primary/20 text-brand-primary border border-brand-primary/30 px-2 py-0.5 rounded-full">
          {getPercentage()}%
        </span>
      </div>

      <div className="w-full bg-brand-surface-light rounded-full h-1.5 mb-8 overflow-hidden border border-brand-border">
        <div 
          className="bg-gradient-to-r from-brand-primary to-brand-secondary h-1.5 rounded-full transition-all duration-700 ease-out" 
          style={{ width: `${getPercentage()}%` }}
        />
      </div>

      <div className="relative flex-grow flex flex-col justify-between space-y-6">
       
        <div className="absolute left-[18px] top-2 bottom-2 w-0.5 bg-brand-border" />

        {steps.map((step, idx) => {
          const stepStatus = getStepStatus(step.id, idx);
          const isCompleted = stepStatus === "completed";
          const isActive = stepStatus === "active";
          const answerVal = answers[step.id];

          return (
            <div key={step.id} className="relative flex items-start space-x-4">
            
              <div 
                className={`z-10 flex h-9 w-9 shrink-0 items-center justify-center rounded-full border transition-all duration-300 ${
                  isCompleted 
                    ? "bg-emerald-500/20 border-emerald-500 text-emerald-400 shadow-[0_0_10px_rgba(16,185,129,0.1)]" 
                    : isActive 
                    ? "bg-brand-primary/25 border-brand-primary text-brand-text-main glow-active" 
                    : "bg-brand-surface border-brand-border text-brand-text-muted/65"
                }`}
              >
                {isCompleted ? <Check className="h-4 w-4 stroke-[3]" /> : step.icon}
              </div>
              <div className="flex flex-col min-w-0">
                <span className={`text-xs font-semibold uppercase tracking-wider ${
                  isCompleted ? "text-emerald-400" : isActive ? "text-brand-secondary" : "text-brand-text-muted/65"
                }`}>
                  {step.name}
                </span>
                <span className="text-xs text-brand-text-muted font-light mt-0.5">{step.role}</span>
                {answerVal && isCompleted && (
                  <span className="mt-1 text-[11px] font-mono text-brand-text-muted bg-brand-surface-light border border-brand-border px-2 py-0.5 rounded italic">
                    "{answerVal}"
                  </span>
                )}

                {isActive && currentAgent !== "completed" && (
                  <span className="mt-1 text-[10px] text-brand-secondary animate-pulse">
                    Thinking...
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>
      {currentAgent !== "completed" && currentAgent && (
        <div className="mt-6 p-3 rounded-lg border border-brand-primary/20 bg-brand-primary/5 text-xs text-brand-secondary flex items-center space-x-2">
          <div className="flex space-x-1 shrink-0">
            <span className="h-1.5 w-1.5 rounded-full bg-brand-primary animate-bounce" style={{ animationDelay: '0ms' }} />
            <span className="h-1.5 w-1.5 rounded-full bg-brand-primary animate-bounce" style={{ animationDelay: '150ms' }} />
            <span className="h-1.5 w-1.5 rounded-full bg-brand-primary animate-bounce" style={{ animationDelay: '300ms' }} />
          </div>
          <p className="truncate font-mono">{activeStep.thinkingText}</p>
        </div>
      )}
    </div>
  );
}
