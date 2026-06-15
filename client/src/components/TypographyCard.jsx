import React from "react";
import { Type, Eye } from "lucide-react";

export default function TypographyCard({ typography = ["Plus Jakarta Sans", "Inter"] }) {
  const fonts = Array.isArray(typography)
    ? typography
    : [typography?.headingFont, typography?.bodyFont].filter(Boolean);
  const safeFonts = fonts.length > 0 ? fonts : ["Plus Jakarta Sans", "Inter"];
  const headerFont = safeFonts[0];
  const bodyFont = safeFonts[1] || safeFonts[0];

  return (
    <div className="card-premium rounded-2xl p-6 flex flex-col justify-between h-full">
      <div>
        <div className="flex items-center space-x-2 text-brand-primary font-bold mb-4">
          <Type className="h-5 w-5" />
          <span className="text-xs uppercase tracking-wider font-mono">Typography Pairings</span>
        </div>


        <div className="flex flex-wrap gap-2 mb-4">
          {safeFonts.map((font, idx) => (
            <span
              key={idx}
              className="px-2.5 py-1 rounded-md text-xs font-semibold bg-brand-surface-light border border-brand-border text-brand-secondary"
            >
              {font} {idx === 0 ? "(Header)" : "(Body)"}
            </span>
          ))}
        </div>

  
        <div className="rounded-xl border border-brand-border bg-brand-surface-light p-4 space-y-3 relative overflow-hidden">
          <div className="absolute top-2 right-2 text-[9px] text-brand-text-muted uppercase font-mono flex items-center space-x-1">
            <Eye className="h-3 w-3" />
            <span>Live Preview</span>
          </div>


          <div>
            <span className="text-[9px] text-brand-text-muted font-bold uppercase tracking-widest block mb-0.5">Header Font Preview</span>
            <p 
              style={{ fontFamily: headerFont }} 
              className="text-lg font-bold text-brand-text-main tracking-tight"
            >
              Making Brands Legendary
            </p>
          </div>

          <div className="pt-1.5 border-t border-brand-border">
            <span className="text-[9px] text-brand-text-muted font-bold uppercase tracking-widest block mb-0.5">Body Font Preview</span>
            <p 
              style={{ fontFamily: bodyFont }} 
              className="text-xs text-brand-text-muted font-light leading-relaxed"
            >
              Curating high-performance experiences that build trust with customers, tailored for modern responsive digital layouts.
            </p>
          </div>
        </div>
      </div>

      <div className="mt-4 text-[10px] text-brand-text-muted font-light">
        Fonts are dynamically fetched from the Google Fonts library.
      </div>
    </div>
  );
}
