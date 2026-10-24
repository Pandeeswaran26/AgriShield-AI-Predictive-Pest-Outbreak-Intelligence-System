import React from "react";
import RiskBadge from "./RiskBadge";
import { Bug } from "lucide-react";

export default function PestRankCard({ pest, rank, maxPestValue = 30 }) {
  const isTop = rank === 1;
  const pestVal = pest.pest_value || 0;
  const pct = Math.min(100, Math.max(8, (pestVal / Math.max(maxPestValue, 10)) * 100));

  const getBarColor = (risk) => {
    switch (risk?.toLowerCase()) {
      case "high":
        return "from-rose-500 to-red-600";
      case "medium":
        return "from-amber-400 to-orange-500";
      default:
        return "from-emerald-400 to-teal-500";
    }
  };

  return (
    <div
      className={`relative p-4 rounded-xl border transition-all duration-200 ${
        isTop
          ? "bg-emerald-950/20 border-emerald-500/40 shadow-lg shadow-emerald-950/20 ring-1 ring-emerald-500/30"
          : "bg-slate-900/60 border-slate-800 hover:border-slate-700"
      }`}
    >
      <div className="flex items-start justify-between gap-3 mb-2">
        <div className="flex items-center gap-3">
          <div
            className={`w-7 h-7 rounded-lg flex items-center justify-center text-xs font-bold ${
              isTop
                ? "bg-emerald-500 text-slate-950 shadow-md shadow-emerald-500/20"
                : "bg-slate-800 text-slate-400 border border-slate-700"
            }`}
          >
            #{rank}
          </div>
          <div>
            <h4 className="font-semibold text-slate-100 text-sm md:text-base flex items-center gap-1.5">
              {pest.pest_name_display || pest.pest_name}
              {isTop && (
                <span className="text-[10px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded bg-rose-500/20 text-rose-400 border border-rose-500/30">
                  Primary Threat
                </span>
              )}
            </h4>
            <p className="text-xs text-slate-400">
              Raw identifier: <span className="font-mono text-[11px] text-slate-400">{pest.pest_name}</span>
            </p>
          </div>
        </div>

        <RiskBadge risk={pest.risk_level} />
      </div>

      {/* Progress / Intensity Bar */}
      <div className="mt-3">
        <div className="flex justify-between text-xs mb-1">
          <span className="text-slate-400 flex items-center gap-1">
            <Bug className="w-3.5 h-3.5 text-slate-400" />
            Predicted Severity Index:
          </span>
          <span className="font-bold text-slate-200">
            {pestVal.toFixed(2)}{" "}
            <span className="text-slate-400 font-normal">
              ({pest.confidence ? `${pest.confidence}% confidence` : "calibrated index"})
            </span>
          </span>
        </div>
        <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
          <div
            className={`h-full rounded-full bg-gradient-to-r ${getBarColor(pest.risk_level)} transition-all duration-500`}
            style={{ width: `${pct}%` }}
          />
        </div>
      </div>
    </div>
  );
}
