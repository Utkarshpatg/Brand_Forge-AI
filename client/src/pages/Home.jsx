import React, { useState, useEffect } from "react";
import { generateBrand, getSystemStatus } from "../services/api";
import Hero from "../components/Hero";
import IdeaInput from "../components/IdeaInput";
import BrandOverviewCard from "../components/BrandOverviewCard";
import StrategyCard from "../components/StrategyCard";
import ColorPaletteCard from "../components/ColorPaletteCard";
import TypographyCard from "../components/TypographyCard";
import LogoPromptCard from "../components/LogoPromptCard";
import ValidatorCard from "../components/ValidatorCard";
import AgentTimeline from "../components/AgentTimeline";
import ConversationPanel from "../components/ConversationPanel";
import Header from "../components/Header";
import { Download, Share2, RefreshCw, ArrowLeft, Layers } from "lucide-react";
import { jsPDF } from "jspdf";
import html2canvas from "html2canvas";

export default function Home() {
  // Main state hooks
  const [idea, setIdea] = useState("");
  const [loading, setLoading] = useState(false);
  const [currentAgent, setCurrentAgent] = useState(""); // Discovery, Strategy, Visual, Validator, completed
  const [question, setQuestion] = useState("");
  const [agentHistory, setAgentHistory] = useState([]);
  const [answers, setAnswers] = useState({});
  const [brandData, setBrandData] = useState(null);
  const [error, setError] = useState("");
  
  // Theme & Dev flags
  const [demoMode, setDemoMode] = useState(false);
  const [darkMode, setDarkMode] = useState(true);
  const [recentSearches, setRecentSearches] = useState([]);
  const [showShareToast, setShowShareToast] = useState(false);
  const [systemStatus, setSystemStatus] = useState(null);

  useEffect(() => {
    let cancelled = false;

    getSystemStatus()
      .then((status) => {
        if (!cancelled) setSystemStatus(status);
      })
      .catch((err) => {
        console.warn("Backend system status unavailable:", err.message);
        if (!cancelled) {
          setSystemStatus({
            ok: false,
            agents: [],
            model: { provider: "offline", model: "client simulation", mode: "demo", configured: false },
            workflow: ["Discovery", "Strategy", "Visual", "Validator"],
          });
        }
      });

    return () => {
      cancelled = true;
    };
  }, []);

  // Load recent searches from localStorage
  useEffect(() => {
    const saved = localStorage.getItem("BrandForge_brands");
    if (saved) {
      try {
        setRecentSearches(JSON.parse(saved));
      } catch (e) {
        console.error("Failed to parse recent searches", e);
      }
    }
  }, []);

  // Update dark mode classes
  useEffect(() => {
    const root = window.document.documentElement;
    if (darkMode) {
      root.classList.add("dark");
      root.style.backgroundColor = "#0F1117";
    } else {
      root.classList.remove("dark");
      root.style.backgroundColor = "#F7F7F5";
    }
  }, [darkMode]);

  // Save brand to recent list
  const saveBrandToHistory = (newBrand) => {
    const existing = [...recentSearches];
    // Remove if duplicates exist
    const filtered = existing.filter((b) => b.brandName !== newBrand.brandName);
    const updated = [newBrand, ...filtered].slice(0, 10); // keep last 10
    setRecentSearches(updated);
    localStorage.setItem("BrandForge_brands", JSON.stringify(updated));
  };

  // Select brand from history dropdown
  const handleSelectHistoryBrand = (selectedBrand) => {
    setIdea(selectedBrand.idea);
    setAnswers(selectedBrand.answers || {});
    setBrandData(selectedBrand);
    setCurrentAgent("completed");
    setQuestion("");
    setAgentHistory([
      { role: "user", text: selectedBrand.idea },
      { role: "agent", agent: "Validator", text: "Saved brand report loaded from history." }
    ]);
  };

  // Phase 1: Submit Startup Idea
  const handleStartWorkflow = async () => {
    if (!idea.trim()) return;
    setLoading(true);
    setError("");
    setBrandData(null);
    setAnswers({});
    
    // Add initial user entry to message feed
    setAgentHistory([{ role: "user", text: idea }]);

    try {
      const res = await generateBrand(idea, {}, "", demoMode);
      
      if (res.status === "needs_input") {
        setCurrentAgent(res.currentAgent);
        setQuestion(res.question);
        
        // Add Agent question to message feed
        setAgentHistory((prev) => [
          ...prev,
          { role: "agent", agent: res.currentAgent, text: res.question }
        ]);
      } else if (res.status === "completed") {
        // Direct generation completed (unlikely on first request in multi-agent flow, but possible if API skips)
        setBrandData(res.brandData);
        setCurrentAgent("completed");
        saveBrandToHistory({ ...res.brandData, idea, answers: {} });
      }
    } catch (err) {
      setError("Failed to initialize agent workflow. Please check your backend connection or use Demo Mode.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Phase 2: Send answer to next agent
  const handleSendAnswer = async (answerText) => {
    setLoading(true);
    setError("");
    
    // 1. Save answer in local answers state
    const updatedAnswers = { ...answers, [currentAgent]: answerText };
    setAnswers(updatedAnswers);

    // 2. Add user answer to chat logs
    setAgentHistory((prev) => [...prev, { role: "user", text: answerText }]);

    try {
      // Send accumulated answers to next step
      const res = await generateBrand(idea, updatedAnswers, currentAgent, demoMode);

      if (res.status === "needs_input") {
        setCurrentAgent(res.currentAgent);
        setQuestion(res.question);
        
        // Add next agent's question to chat logs
        setAgentHistory((prev) => [
          ...prev,
          { role: "agent", agent: res.currentAgent, text: res.question }
        ]);
      } else if (res.status === "completed") {
        // Transition state to Validator for a short visual pause
        setCurrentAgent("Validator");
        setQuestion("");
        
        // Simulate Validator running a validation pass
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // Complete workflow
        setBrandData(res.brandData);
        setCurrentAgent("completed");
        
        // Add final validation check to history logs
        setAgentHistory((prev) => [
          ...prev,
          { 
            role: "agent", 
            agent: "Validator", 
            text: `Validator Review: Brand consistency is ${res.brandData.brandConsistencyScore}%. Visuals align with audience '${res.brandData.audience}'. All checks verified.` 
          }
        ]);

        // Save generated brand data to LocalStorage searches
        saveBrandToHistory({ ...res.brandData, idea, answers: updatedAnswers });
      }
    } catch (err) {
      setError("Failed to communicate with AI Agents. Please try again or toggle Demo Mode.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // WOW Feature: Go back/Edit previous answer
  const handleResetStep = () => {
    if (agentHistory.length < 3) return; // Need at least one agent exchange to step back
    
    // Find index of last user answer
    const historyCopy = [...agentHistory];
    
    // Pop last agent question and user answer
    historyCopy.pop(); // User's last answer message
    const poppedAgentMsg = historyCopy.pop(); // Agent's question message
    
    // Set active agent back to the one we just popped
    const prevAgent = poppedAgentMsg.agent;
    setCurrentAgent(prevAgent);
    setQuestion(poppedAgentMsg.text);
    
    // Clean answers map
    const answersCopy = { ...answers };
    delete answersCopy[prevAgent];
    setAnswers(answersCopy);
    
    setAgentHistory([...historyCopy, poppedAgentMsg]);
  };

  // WOW Feature: Download Brand Report as PDF
  const handleDownloadPDF = async () => {
    const reportNode = document.getElementById("brand-report-container");
    if (!reportNode) return;

    try {
      setLoading(true);
      // Wait a tiny moment for layout safety
      await new Promise((resolve) => setTimeout(resolve, 300));
      
      const canvas = await html2canvas(reportNode, {
        scale: 2,
        useCORS: true,
        backgroundColor: darkMode ? "#0F1117" : "#F8FAFC",
      });

      const imgData = canvas.toDataURL("image/png");
      const pdf = new jsPDF("p", "mm", "a4");
      
      const pdfWidth = pdf.internal.pageSize.getWidth();
      const pdfHeight = pdf.internal.pageSize.getHeight();
      
      const imgWidth = pdfWidth;
      const imgHeight = (canvas.height * pdfWidth) / canvas.width;
      
      let heightLeft = imgHeight;
      let position = 0;

      // Add to page
      pdf.addImage(imgData, "PNG", 0, position, imgWidth, imgHeight);
      heightLeft -= pdfHeight;

      while (heightLeft >= 0) {
        position = heightLeft - imgHeight;
        pdf.addPage();
        pdf.addImage(imgData, "PNG", 0, position, imgWidth, imgHeight);
        heightLeft -= pdfHeight;
      }

      pdf.save(`${brandData?.brandName.replace(/\s+/g, "-")}-Brand-Booklet.pdf`);
    } catch (err) {
      console.error("PDF generation failed", err);
      alert("Failed to render PDF report. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  // WOW Feature: Share Brand Summary Text
  const handleShareBrand = () => {
    if (!brandData) return;

    const summary = `
BrandForge AI BRAND REPORT
---------------------------------------------
Brand Name: ${brandData.brandName}
Target Audience: ${brandData.audience}
Mission: ${brandData.mission}
Brand Voice: ${brandData.voice}
Positioning: ${brandData.positioning}
Primary Colors: ${brandData.colors.join(", ")}
Typography Pairing: ${brandData.typography.join(" + ")}
Consistency Score: ${brandData.brandConsistencyScore}/100
---------------------------------------------
Generated by BrandForge AI. Define your startup idea and get your brand identity.
    `;
    
    navigator.clipboard?.writeText?.(summary.trim());
    setShowShareToast(true);
    setTimeout(() => setShowShareToast(false), 3000);
  };

  // WOW Feature: Regenerate Output (randomize values)
  const handleRegenerateOutput = async () => {
    if (!idea) return;
    setLoading(true);
    try {
      // Force visual simulation completion with new values
      const res = await generateBrand(idea, answers, "Visual", demoMode);
      if (res.status === "completed") {
        setBrandData(res.brandData);
        // Update history logs last entry
        setAgentHistory((prev) => {
          const c = [...prev];
          if (c[c.length - 1]?.agent === "Validator") {
            c[c.length - 1].text = `Validator Review: Brand consistency is ${res.brandData.brandConsistencyScore}%. Visuals aligned. Regenerated.`;
          }
          return c;
        });
        saveBrandToHistory({ ...res.brandData, idea, answers });
      }
    } catch (e) {
      console.error("Regeneration failed", e);
    } finally {
      setLoading(false);
    }
  };

  // Restart / Reset state
  const handleStartOver = () => {
    setIdea("");
    setAnswers({});
    setBrandData(null);
    setCurrentAgent("");
    setQuestion("");
    setAgentHistory([]);
    setError("");
  };

  return (
    <div className={`min-h-screen font-sans transition-all duration-300 pb-20 ${
      darkMode ? "premium-bg text-brand-text-main" : "bg-slate-50 text-slate-900"
    }`}>
      

      <Header
        recentSearches={recentSearches}
        onSelectSearch={handleSelectHistoryBrand}
        demoMode={demoMode}
        setDemoMode={setDemoMode}
        darkMode={darkMode}
        setDarkMode={setDarkMode}
      />

  
      <main className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 pt-6">
        
     
        {showShareToast && (
          <div className="fixed bottom-5 right-5 z-50 rounded-xl bg-brand-surface border border-emerald-500/30 text-emerald-400 px-4 py-3 flex items-center space-x-2 shadow-2xl animate-bounce">
            <span>OK</span>
            <span className="text-xs font-semibold">Brand report summary copied to clipboard!</span>
          </div>
        )}

      
        {error && (
          <div className="mx-auto max-w-3xl mb-6 p-4 rounded-xl border border-red-500/20 bg-red-500/5 text-xs text-red-400 font-mono flex items-center justify-between">
            <span>{error}</span>
            <button onClick={() => setError("")} className="underline hover:text-white">dismiss</button>
          </div>
        )}

  
        {!currentAgent && !brandData && (
          <div className="space-y-6">
            <Hero />
            <IdeaInput
              idea={idea}
              setIdea={setIdea}
              onSubmit={handleStartWorkflow}
              loading={loading}
            />
          </div>
        )}

      
        {currentAgent && currentAgent !== "completed" && !brandData && (
          <div className="mt-8 space-y-6">
            
         
            <div className="text-center max-w-xl mx-auto">
              <h3 className="text-lg font-bold font-jakarta text-brand-secondary">
                Agent Collaboration Active
              </h3>
              <p className="text-xs text-brand-text-muted mt-1 font-light leading-relaxed">
                The agents are examining your idea: <span className="font-mono text-brand-primary">"{idea}"</span>. 
                Please answer their questions below to shape the strategy.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-stretch max-w-5xl mx-auto">
        
              <div className="md:col-span-1">
                <AgentTimeline
                  currentAgent={currentAgent}
                  answers={answers}
                />
              </div>

       
              <div className="md:col-span-2">
                <ConversationPanel
                  agentHistory={agentHistory}
                  currentAgent={currentAgent}
                  question={question}
                  onSendAnswer={handleSendAnswer}
                  onResetStep={handleResetStep}
                  loading={loading}
                />
              </div>
            </div>
          </div>
        )}

    
        {brandData && (
          <div className="mt-8 space-y-8 animate-fade-in">
            
         
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between border-b border-brand-border pb-5 gap-4">
              <div>
                <span className="text-xs font-mono font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 border border-emerald-500/20 rounded-full">
                  Branding Asset Package Ready
                </span>
                <h2 className="text-2xl font-jakarta font-extrabold text-brand-text-main tracking-tight mt-1.5 flex items-center space-x-2">
                  <Layers className="text-brand-primary h-5 w-5" />
                  <span>{brandData.brandName} Brand Hub</span>
                </h2>
                <p className="text-xs text-brand-text-muted mt-0.5 font-light truncate max-w-lg">
                  Original startup idea: "{idea}"
                </p>
              </div>

         
              <div className="flex flex-wrap items-center gap-2">
                <button
                  onClick={handleRegenerateOutput}
                  disabled={loading}
                  className="flex items-center space-x-1.5 px-3 py-2 rounded-lg bg-brand-surface hover:bg-brand-surface-light border border-brand-border text-xs font-semibold text-brand-text-muted hover:text-brand-text-main transition"
                  title="Randomize brand details"
                >
                  <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin' : ''}`} />
                  <span>Regenerate Variant</span>
                </button>
                
                <button
                  onClick={handleShareBrand}
                  className="flex items-center space-x-1.5 px-3 py-2 rounded-lg bg-brand-surface hover:bg-brand-surface-light border border-brand-border text-xs font-semibold text-brand-text-muted hover:text-brand-text-main transition"
                >
                  <Share2 className="h-3.5 w-3.5" />
                  <span>Share Summary</span>
                </button>

                <button
                  onClick={handleDownloadPDF}
                  disabled={loading}
                  className="flex items-center space-x-1.5 px-3.5 py-2 rounded-lg btn-primary-warm text-xs font-bold text-white shadow transition"
                >
                  <Download className="h-3.5 w-3.5" />
                  <span>Download Brand Book</span>
                </button>

                <button
                  onClick={handleStartOver}
                  className="flex items-center space-x-1 px-3 py-2 rounded-lg bg-brand-surface hover:bg-brand-surface-light border border-brand-border text-xs text-brand-primary hover:text-brand-secondary transition"
                >
                  <ArrowLeft className="h-3.5 w-3.5" />
                  <span>Start New</span>
                </button>
              </div>
            </div>

            <div id="brand-report-container" className="p-4 rounded-3xl border border-brand-border bg-brand-surface-light/40">
              
              <div className="text-center py-4 border-b border-brand-border mb-6 sm:hidden">
                <h1 className="text-xl font-extrabold text-brand-primary tracking-tight font-jakarta">{brandData.brandName}</h1>
                <p className="text-[10px] text-brand-text-muted font-mono mt-0.5">COMPREHENSIVE BRAND SPECIFICATION BOOKLET</p>
              </div>

          
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <BrandOverviewCard
                  brandName={brandData.brandName}
                  mission={brandData.mission}
                  audience={brandData.audience}
                />
                
                <StrategyCard
                  voice={brandData.voice}
                  positioning={brandData.positioning}
                  consistencyScore={brandData.brandConsistencyScore}
                />

                <ValidatorCard
                  validationReport={brandData.validationReport}
                  consistencyScore={brandData.brandConsistencyScore}
                />

                <ColorPaletteCard colors={brandData.colors} />

                <TypographyCard typography={brandData.typography} />

                <LogoPromptCard logoPrompt={brandData.logoPrompt} />
              </div>
            </div>

           
            <div className="max-w-4xl mx-auto mt-12 border-t border-brand-border pt-8">
              <div className="mb-4">
                <h3 className="text-sm font-bold text-brand-text-muted uppercase tracking-wider">Dialogue Log History</h3>
                <p className="text-xs text-brand-text-muted-more mt-1 font-light">
                  This chat record details the specific context exchange that established the branding guidelines above.
                </p>
              </div>
              <ConversationPanel
                agentHistory={agentHistory}
                currentAgent={currentAgent}
                question={question}
                onSendAnswer={handleSendAnswer}
                onResetStep={handleResetStep}
                loading={loading}
              />
            </div>

          </div>
        )}

      </main>
    </div>
  );
}
