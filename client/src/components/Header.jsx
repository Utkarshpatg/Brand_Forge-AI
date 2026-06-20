import React, { useState } from "react";
import { Cpu, History, Moon, Sun } from "lucide-react";

export default function Header({ 
  recentSearches = [], 
  onSelectSearch, 
  demoMode, 
  setDemoMode,
  darkMode,
  setDarkMode
}) {
  const [dropdownOpen, setDropdownOpen] = useState(false);

  return (
    <header className="sticky top-3 mx-auto max-w-7xl w-[calc(100%-24px)] z-40 navbar-glass">
      <div className="mx-auto flex max-w-7xl h-16 items-center justify-between px-4 sm:px-6 lg:px-8">
        <div className="flex items-center space-x-3 cursor-pointer" onClick={() => window.location.reload()}>
          <div>
            <h1 className="text-xl font-jakarta font-extrabold tracking-tight bg-gradient-to-r from-brand-primary via-amber-500 to-brand-secondary bg-clip-text text-transparent">
              BrandForge AI
            </h1>
            <p className="text-[10px] text-brand-text-muted tracking-wider font-semibold uppercase">Multi-Agent Brand Engine</p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
         
          <div className="hidden md:flex items-center space-x-2 bg-brand-surface border border-brand-border rounded-lg p-1">
            <button
              onClick={() => setDemoMode(false)}
              className={`px-3 py-1 text-xs font-semibold rounded-md transition-all cursor-pointer ${
                !demoMode 
                  ? "bg-brand-primary text-white shadow" 
                  : "text-brand-text-muted hover:text-brand-text-main"
              }`}
            >
              Backend API
            </button>
            <button
              onClick={() => setDemoMode(true)}
              className={`px-3 py-1 text-xs font-semibold rounded-md transition-all cursor-pointer ${
                demoMode 
                  ? "bg-brand-primary text-white shadow" 
                  : "text-brand-text-muted hover:text-brand-text-main"
              }`}
            >
              Demo Mode
            </button>
          </div>

          <div className="relative">
            <button
              onClick={() => setDropdownOpen(!dropdownOpen)}
              className="flex items-center space-x-1 px-3 py-2 rounded-lg bg-brand-surface hover:bg-brand-surface-light border border-brand-border text-brand-text-muted hover:text-brand-text-main transition text-sm font-medium cursor-pointer"
            >
              <History className="h-4 w-4" />
              <span className="hidden sm:inline">Recent</span>
              {recentSearches.length > 0 && (
                <span className="ml-1 px-1.5 py-0.2 text-[10px] font-bold bg-brand-primary/20 text-brand-primary rounded-full border border-brand-primary/30">
                  {recentSearches.length}
                </span>
              )}
            </button>

            {dropdownOpen && (
              <div className="absolute right-0 mt-2 w-64 origin-top-right rounded-xl border border-brand-border bg-brand-surface p-2 shadow-2xl focus:outline-none z-50">
                <div className="px-2 py-1.5 text-xs font-semibold text-brand-text-muted border-b border-brand-border mb-1 flex items-center justify-between">
                  <span>HISTORY</span>
                  <span>{recentSearches.length} Saved</span>
                </div>
                
                {recentSearches.length === 0 ? (
                  <p className="px-3 py-4 text-center text-xs text-brand-text-muted">No brand identities found yet.</p>
                ) : (
                  <div className="max-h-60 overflow-y-auto space-y-1">
                    {recentSearches.map((item, index) => (
                      <button
                        key={index}
                        onClick={() => {
                          onSelectSearch(item);
                          setDropdownOpen(false);
                        }}
                        className="w-full text-left px-3 py-2 rounded-lg hover:bg-brand-surface-light/80 transition flex flex-col cursor-pointer"
                      >
                        <div className="flex items-center justify-between">
                          <span className="text-sm font-semibold text-brand-primary">{item.brandName}</span>
                          <span className="text-[10px] bg-brand-surface-light text-brand-secondary font-mono px-1.5 py-0.5 rounded">Score: {item.brandConsistencyScore}</span>
                        </div>
                        <span className="text-xs text-brand-text-muted truncate max-w-full font-light mt-0.5">"{item.idea}"</span>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>

          <button
            onClick={() => setDarkMode(!darkMode)}
            className="p-2 rounded-lg bg-brand-surface hover:bg-brand-surface-light border border-brand-border text-brand-text-muted hover:text-brand-text-main transition cursor-pointer"
            aria-label="Toggle Dark Mode"
          >
            {darkMode ? <Sun className="h-4 w-4 text-amber-400" /> : <Moon className="h-4 w-4" />}
          </button>

        </div>
      </div>
    </header>
  );
}
