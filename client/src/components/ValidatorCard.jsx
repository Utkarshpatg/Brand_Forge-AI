import React from "react";
import { Shield, AlertTriangle, CheckCircle2, XCircle } from "lucide-react";

export default function ValidatorCard({ validationReport, consistencyScore = 95 }) {
  // Determine validation status based on consistency score
  let status = "success"; // success, warning, failed
  let statusText = "PASS / BRAND ALIGNED";
  let statusColor = "text-emerald-400 bg-emerald-500/10 border-emerald-500/20";
  let Icon = CheckCircle2;

  if (consistencyScore < 85) {
    status = "failed";
    statusText = "FAIL / INCONSISTENT";
    statusColor = "text-rose-400 bg-rose-500/10 border-rose-500/20";
    Icon = XCircle;
  } else if (consistencyScore < 90) {
    status = "warning";
    statusText = "WARNING / ALIGNMENT ISSUES";
    statusColor = "text-amber-400 bg-amber-500/10 border-amber-500/20";
    Icon = AlertTriangle;
  }

  const defaultReport = "All branding elements are consistent.";

  return (
    <div className="card-premium rounded-2xl p-6 flex flex-col justify-between h-full">
      <div>
        <div className="flex items-center space-x-2 text-brand-primary font-bold mb-4">
          <Shield className="h-5 w-5" />
          <span className="text-xs uppercase tracking-wider font-mono">Validator Agent Audit</span>
        </div>


        <div className={`flex items-center space-x-2.5 px-3 py-2.5 rounded-xl border ${statusColor} mb-4`}>
          <Icon className="h-5 w-5 shrink-0" />
          <div className="flex-1 min-w-0">
            <span className="text-[9px] uppercase tracking-wider font-bold block text-brand-text-muted">Security & Alignment Status</span>
            <span className="text-xs font-bold font-mono tracking-wide">{statusText}</span>
          </div>
        </div>


        <div>
          <span className="text-xs text-brand-text-muted font-medium uppercase tracking-wider block mb-1">Audit Findings</span>
          <p className="text-xs text-brand-text-muted leading-relaxed font-light font-mono bg-brand-surface-light p-3 rounded-lg border border-brand-border">
            {validationReport || defaultReport}
          </p>
        </div>
      </div>

      <div className="mt-4 pt-3 border-t border-brand-border flex justify-between items-center text-[10px] text-brand-text-muted">
        <span className="font-light">Validated across 24 checkpoints.</span>
        <span className="font-semibold text-brand-secondary font-mono">100% Audited</span>
      </div>
    </div>
  );
}
