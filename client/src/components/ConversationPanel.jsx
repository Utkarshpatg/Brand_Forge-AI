import React, { useState, useEffect, useRef } from "react";
import { Send, User, ArrowLeft } from "lucide-react";

export default function ConversationPanel({
  agentHistory = [],
  currentAgent,
  question,
  onSendAnswer,
  onResetStep,
  loading,
}) {
  const [inputValue, setInputValue] = useState("");
  const chatEndRef = useRef(null);

  // Auto-scroll to bottom of chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [agentHistory, question, loading]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!inputValue.trim() || loading) return;
    onSendAnswer(inputValue.trim());
    setInputValue("");
  };

  // Get avatar label/icon based on agent name
  const getAgentInfo = (agentName) => {
    switch (agentName) {
      case "Discovery":
        return { label: "D", color: "from-amber-600 to-amber-500", name: "Discovery Agent" };
      case "Strategy":
        return { label: "S", color: "from-orange-600 to-orange-500", name: "Strategy Agent" };
      case "Visual":
        return { label: "V", color: "from-yellow-600 to-yellow-500", name: "Visual Agent" };
      case "Validator":
        return { label: "OK", color: "from-amber-700 to-amber-600", name: "Validator Agent" };
      default:
        return { label: "AI", color: "from-zinc-700 to-zinc-600", name: "AI Orchestrator" };
    }
  };

  return (
    <div className="card-premium rounded-2xl flex flex-col h-[500px] overflow-hidden">
      <div className="bg-brand-surface-light/60 px-4 py-3 border-b border-brand-border flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <span className="flex h-2.5 w-2.5 rounded-full bg-emerald-500 animate-pulse" />
          <span className="text-xs font-bold text-brand-text-main tracking-wide uppercase">Agent Interaction Panel</span>
        </div>
        {agentHistory.length > 1 && currentAgent !== "completed" && (
          <button
            onClick={onResetStep}
            className="flex items-center space-x-1 text-[11px] font-semibold text-brand-text-muted hover:text-brand-primary transition cursor-pointer"
            title="Edit previous answer"
          >
            <ArrowLeft className="h-3.5 w-3.5" />
            <span>Go Back / Edit</span>
          </button>
        )}
      </div>
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {agentHistory.map((msg, index) => {
          const isUser = msg.role === "user";
          const agentInfo = !isUser ? getAgentInfo(msg.agent) : null;

          return (
            <div
              key={index}
              className={`flex items-start gap-3 max-w-[85%] ${
                isUser ? "ml-auto flex-row-reverse" : "mr-auto"
              }`}
            >
              <div
                className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-sm shadow-md ${
                  isUser 
                    ? "bg-brand-surface-light text-brand-secondary border border-brand-border" 
                    : `bg-gradient-to-br ${agentInfo.color} text-white`
                }`}
              >
                {isUser ? <User className="h-4 w-4" /> : agentInfo.label}
              </div>

              <div className="flex flex-col">
                <span className={`text-[10px] font-semibold text-brand-text-muted mb-0.5 ${isUser ? "text-right" : "text-left"}`}>
                  {isUser ? "You" : agentInfo.name}
                </span>
                <div
                  className={`rounded-xl px-3.5 py-2 text-sm shadow-sm leading-relaxed ${
                    isUser
                      ? "bg-brand-primary text-white rounded-tr-none"
                      : "bg-brand-surface-light text-brand-text-main rounded-tl-none border border-brand-border"
                  }`}
                >
                  {msg.text}
                </div>
              </div>
            </div>
          );
        })}
        {loading && currentAgent !== "completed" && (
          <div className="flex items-start gap-3 max-w-[85%] mr-auto">
            <div className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-sm bg-gradient-to-br ${getAgentInfo(currentAgent).color} text-white`}>
              {getAgentInfo(currentAgent).label}
            </div>
            <div className="flex flex-col">
              <span className="text-[10px] font-semibold text-brand-text-muted mb-0.5">
                {getAgentInfo(currentAgent).name}
              </span>
              <div className="bg-brand-surface-light rounded-xl rounded-tl-none px-4 py-2.5 text-brand-text-muted border border-brand-border flex items-center space-x-2">
                <div className="flex space-x-1">
                  <span className="h-1.5 w-1.5 rounded-full bg-brand-primary animate-bounce" style={{ animationDelay: '0ms' }} />
                  <span className="h-1.5 w-1.5 rounded-full bg-brand-primary animate-bounce" style={{ animationDelay: '150ms' }} />
                  <span className="h-1.5 w-1.5 rounded-full bg-brand-primary animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
                <span className="text-xs font-mono italic">thinking...</span>
              </div>
            </div>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>
      <div className="border-t border-brand-border bg-brand-surface p-3">
        {currentAgent === "completed" ? (
          <div className="text-center py-2 text-xs text-brand-text-muted font-mono flex items-center justify-center space-x-1">
            <span className="text-emerald-500 font-bold">OK</span>
            <span>Branding cycle completed successfully. Report generated.</span>
          </div>
        ) : question && !loading ? (
          <form onSubmit={handleSubmit} className="flex gap-2 items-center">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder={`Answer ${getAgentInfo(currentAgent).name}...`}
              className="flex-1 rounded-lg border border-brand-border bg-brand-surface-light/40 p-2.5 text-xs text-brand-text-main placeholder-brand-text-muted/50 focus:border-brand-primary/50 focus:outline-none focus:ring-1 focus:ring-brand-primary/30"
              required
            />
            <button
              type="submit"
              disabled={!inputValue.trim() || loading}
              className="flex h-9 w-9 items-center justify-center rounded-lg btn-primary-warm text-white hover:bg-brand-secondary disabled:opacity-50 transition shrink-0 shadow-lg cursor-pointer"
            >
              <Send className="h-4 w-4" />
            </button>
          </form>
        ) : (
          <div className="text-center py-2 text-xs text-brand-text-muted font-mono">
            Waiting for startup idea definition...
          </div>
        )}
      </div>
    </div>
  );
}

