import React from "react";
import { Award, Compass, Target } from "lucide-react";

export default function BrandOverviewCard({ brandName, mission, audience }) {
  return (
    <div className="card-premium rounded-2xl p-6 relative overflow-hidden">
      <div className="absolute top-0 right-0 h-16 w-16 bg-gradient-to-br from-brand-primary/10 to-brand-secondary/15 rounded-bl-3xl" />
      
      <div className="flex items-center space-x-2 text-brand-primary font-bold mb-4">
        <Award className="h-5 w-5" />
        <span className="text-xs uppercase tracking-wider font-mono">Brand Overview</span>
      </div>

      <div className="space-y-4">
        <div>
          <span className="text-xs text-brand-text-muted font-medium uppercase tracking-wider block">Identity Name</span>
          <h3 className="text-2xl sm:text-3xl font-jakarta font-extrabold text-brand-text-main tracking-tight mt-1">
            {brandName}
          </h3>
        </div>
        <div>
          <span className="text-xs text-brand-text-muted font-medium uppercase tracking-wider block">Core Mission</span>
          <p className="text-sm text-brand-text-muted font-light mt-1.5 leading-relaxed">
            {mission}
          </p>
        </div>
        <div className="pt-2">
          <span className="text-xs text-brand-text-muted font-medium uppercase tracking-wider block mb-1.5">Target Audience</span>
          <div className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-brand-surface-light border border-brand-border text-xs text-brand-text-muted font-medium">
            <Target className="text-brand-secondary shrink-0 h-4 w-4" />
            <span>{audience}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
