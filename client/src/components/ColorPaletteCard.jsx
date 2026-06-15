import React, { useState } from "react";
import { Palette, Copy, Check } from "lucide-react";

export default function ColorPaletteCard({ colors = [] }) {
  const [copiedIndex, setCopiedIndex] = useState(null);

  const copyToClipboard = (color, index) => {
    navigator.clipboard?.writeText?.(color);
    setCopiedIndex(index);
    setTimeout(() => {
      setCopiedIndex(null);
    }, 2000);
  };

  // Safe check if colors is empty
  const colorList = (colors.length > 0 ? colors : ["#D97706", "#F59E0B", "#0F1117", "#171A23", "#F8FAFC"])
    .map((color) => (typeof color === "string" ? color : color?.hex))
    .filter(Boolean);

  return (
    <div className="card-premium rounded-2xl p-6 flex flex-col justify-between h-full">
      <div>
        <div className="flex items-center space-x-2 text-brand-primary font-bold mb-5">
          <Palette className="h-5 w-5" />
          <span className="text-xs uppercase tracking-wider font-mono">Color Palette</span>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-3.5">
          {colorList.map((color, idx) => (
            <div 
              key={idx} 
              className="flex flex-col items-center p-2 rounded-xl bg-brand-surface-light border border-brand-border hover:border-brand-primary/20 transition group relative"
            >
              <div
                style={{ backgroundColor: color }}
                className="w-full h-14 sm:h-16 rounded-lg shadow-inner transition duration-300 group-hover:scale-[1.03]"
              />
              <span className="text-[10px] font-mono text-brand-text-muted font-semibold mt-2 select-all">
                {color.toUpperCase()}
              </span>
              <button
                onClick={() => copyToClipboard(color, idx)}
                className="absolute top-3 right-3 p-1 rounded-md bg-brand-surface/95 text-brand-text-main hover:text-white border border-brand-border opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer"
                title="Copy Hex Code"
              >
                {copiedIndex === idx ? (
                  <Check className="h-3 w-3 text-emerald-400" />
                ) : (
                  <Copy className="h-3 w-3" />
                )}
              </button>
              <button
                onClick={() => copyToClipboard(color, idx)}
                className="mt-1.5 w-full flex items-center justify-center space-x-1 py-1 rounded bg-brand-surface-light hover:bg-brand-surface border border-brand-border text-[9px] text-brand-text-muted transition sm:hidden cursor-pointer"
              >
                {copiedIndex === idx ? (
                  <>
                    <Check className="h-3.5 w-3.5 text-emerald-400" />
                    <span>Copied</span>
                  </>
                ) : (
                  <>
                    <Copy className="h-3.5 w-3.5" />
                    <span>Copy</span>
                  </>
                )}
              </button>
            </div>
          ))}
        </div>
      </div>

      <div className="mt-5 text-[10px] text-brand-text-muted font-light flex items-center justify-between">
        <span>Hover color chips to quickly copy hex codes.</span>
      </div>
    </div>
  );
}
