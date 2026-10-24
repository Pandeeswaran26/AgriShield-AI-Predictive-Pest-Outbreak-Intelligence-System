import React, { useState } from "react";
import {
  ShieldAlert,
  Sprout,
  Bug,
  Droplets,
  CheckCircle2,
  AlertOctagon,
  Leaf,
  FlaskConical,
  Wind,
  ShieldCheck,
} from "lucide-react";

export default function SmartAdvisory({ advisory }) {
  const [activeTab, setActiveTab] = useState("pest");

  if (!advisory) return null;

  const {
    urgency,
    riskLevel,
    crop,
    targetPest,
    expectedYieldImpact,
    nutritionAdvisory = {},
    pestManagement = {},
    weatherGuidance = {},
  } = advisory;

  const isHighRisk = riskLevel === "High";

  return (
    <div className="bg-slate-900/70 rounded-2xl border border-slate-800 overflow-hidden shadow-xl">
      {/* Urgency Notification Header */}
      <div
        className={`px-5 py-3.5 flex items-start gap-3 border-b ${
          isHighRisk
            ? "bg-rose-950/40 border-rose-500/30 text-rose-200"
            : riskLevel === "Medium"
            ? "bg-amber-950/40 border-amber-500/30 text-amber-200"
            : "bg-emerald-950/40 border-emerald-500/30 text-emerald-200"
        }`}
      >
        <ShieldAlert className="w-5 h-5 mt-0.5 shrink-0" />
        <div className="text-xs md:text-sm">
          <p className="font-semibold">{urgency || "Action Required"}</p>
          <p className="text-xs opacity-80 mt-0.5">
            Projected Crop: <span className="font-bold underline">{crop}</span> • Target Pest:{" "}
            <span className="font-bold underline">{targetPest}</span> • Estimated Potential Yield Loss:{" "}
            <span className="font-bold">{expectedYieldImpact}%</span> if unmanaged
          </p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-800 bg-slate-950/40 px-4 pt-2 gap-2 overflow-x-auto">
        <button
          onClick={() => setActiveTab("pest")}
          className={`px-4 py-2.5 text-xs md:text-sm font-semibold rounded-t-lg transition-colors flex items-center gap-2 border-b-2 ${
            activeTab === "pest"
              ? "text-emerald-400 border-emerald-500 bg-slate-900/90"
              : "text-slate-400 border-transparent hover:text-slate-200"
          }`}
        >
          <Bug className="w-4 h-4" />
          Pest Control (IPM)
        </button>

        <button
          onClick={() => setActiveTab("nutrition")}
          className={`px-4 py-2.5 text-xs md:text-sm font-semibold rounded-t-lg transition-colors flex items-center gap-2 border-b-2 ${
            activeTab === "nutrition"
              ? "text-emerald-400 border-emerald-500 bg-slate-900/90"
              : "text-slate-400 border-transparent hover:text-slate-200"
          }`}
        >
          <Sprout className="w-4 h-4" />
          Fertilizer & Nutrition
        </button>

        <button
          onClick={() => setActiveTab("weather")}
          className={`px-4 py-2.5 text-xs md:text-sm font-semibold rounded-t-lg transition-colors flex items-center gap-2 border-b-2 ${
            activeTab === "weather"
              ? "text-emerald-400 border-emerald-500 bg-slate-900/90"
              : "text-slate-400 border-transparent hover:text-slate-200"
          }`}
        >
          <Droplets className="w-4 h-4" />
          Spray Timing & Weather
        </button>
      </div>

      {/* Tab Content */}
      <div className="p-5">
        {/* Tab 1: Pest Management */}
        {activeTab === "pest" && (
          <div className="space-y-5">
            {/* Immediate Actions */}
            <div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2.5 flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                Immediate Scouting & Cultural Actions
              </h4>
              <ul className="space-y-1.5">
                {(pestManagement.immediateActions || []).map((act, i) => (
                  <li key={i} className="text-xs md:text-sm text-slate-300 flex items-start gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 mt-2 shrink-0" />
                    <span>{act}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Organic & Biological */}
            <div className="p-3.5 bg-emerald-950/20 border border-emerald-500/30 rounded-xl">
              <h4 className="text-xs font-bold uppercase tracking-wider text-emerald-400 mb-2 flex items-center gap-2">
                <Leaf className="w-4 h-4 text-emerald-400" />
                Biological & Organic Alternatives
              </h4>
              <div className="grid sm:grid-cols-2 gap-2">
                {(pestManagement.biologicalSolutions || []).map((org, i) => (
                  <div
                    key={i}
                    className="bg-slate-900/80 px-3 py-2 rounded-lg border border-slate-800 text-xs text-slate-300 flex items-center gap-2"
                  >
                    <ShieldCheck className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                    {org}
                  </div>
                ))}
              </div>
            </div>

            {/* Chemical Control */}
            <div className="p-3.5 bg-slate-950/60 border border-slate-800 rounded-xl">
              <h4 className="text-xs font-bold uppercase tracking-wider text-amber-400 mb-2 flex items-center gap-2">
                <FlaskConical className="w-4 h-4 text-amber-400" />
                Registered Chemical Interventions (Targeted Spray)
              </h4>
              <ul className="space-y-1.5 mb-3">
                {(pestManagement.recommendedPesticides || []).map((pestChem, i) => (
                  <li
                    key={i}
                    className="text-xs md:text-sm text-slate-200 bg-slate-900/80 px-3 py-2 rounded-lg border border-slate-800 font-mono"
                  >
                    {pestChem}
                  </li>
                ))}
              </ul>
              <p className="text-[11px] text-amber-300/80 flex items-start gap-1.5 border-t border-slate-800 pt-2">
                <AlertOctagon className="w-3.5 h-3.5 text-amber-400 shrink-0 mt-0.5" />
                {pestManagement.safetyDisclaimer ||
                  "Ensure accurate dosage calibration, mandatory PPE (gloves/mask), and respect pre-harvest intervals."}
              </p>
            </div>
          </div>
        )}

        {/* Tab 2: Nutrition Advisory */}
        {activeTab === "nutrition" && (
          <div className="space-y-4">
            <div className="p-4 bg-slate-950/60 border border-slate-800 rounded-xl">
              <h4 className="text-xs font-bold uppercase tracking-wider text-emerald-400 mb-2 flex items-center gap-2">
                <Sprout className="w-4 h-4 text-emerald-400" />
                {nutritionAdvisory.title || "Crop Nutrition & Fertilizer Strategy"}
              </h4>
              <p className="text-xs md:text-sm text-slate-300 leading-relaxed">
                {nutritionAdvisory.strategy}
              </p>
            </div>

            {nutritionAdvisory.micronutrients && (
              <div className="p-4 bg-slate-950/60 border border-slate-800 rounded-xl">
                <h4 className="text-xs font-bold uppercase tracking-wider text-teal-400 mb-2 flex items-center gap-2">
                  <Leaf className="w-4 h-4 text-teal-400" />
                  Foliar Micronutrient Boost
                </h4>
                <p className="text-xs md:text-sm text-slate-300 leading-relaxed">
                  {nutritionAdvisory.micronutrients}
                </p>
              </div>
            )}

            <div className="p-3 bg-amber-950/20 border border-amber-500/30 rounded-xl text-xs text-amber-300/90 flex items-start gap-2">
              <AlertOctagon className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
              <span>
                <strong>Nutrition Safety Note:</strong> {nutritionAdvisory.caution}
              </span>
            </div>
          </div>
        )}

        {/* Tab 3: Weather Guidance */}
        {activeTab === "weather" && (
          <div className="space-y-4">
            <div
              className={`p-4 rounded-xl border flex items-start gap-3 ${
                weatherGuidance.sprayRecommended
                  ? "bg-emerald-950/30 border-emerald-500/40 text-emerald-200"
                  : "bg-rose-950/30 border-rose-500/40 text-rose-200"
              }`}
            >
              {weatherGuidance.sprayRecommended ? (
                <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
              ) : (
                <AlertOctagon className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
              )}
              <div>
                <p className="font-semibold text-sm">
                  {weatherGuidance.sprayRecommended
                    ? "Safe Spraying Window Active"
                    : "Foliar Spraying Not Recommended Today"}
                </p>
                <p className="text-xs opacity-80 mt-1">
                  Evaluated based on current wind velocity, precipitation probability, and canopy temperature.
                </p>
              </div>
            </div>

            <div className="p-4 bg-slate-950/60 border border-slate-800 rounded-xl space-y-2.5">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
                <Wind className="w-4 h-4 text-slate-400" />
                Environmental Decision Notes
              </h4>
              <ul className="space-y-2">
                {(weatherGuidance.guidanceNotes || []).map((note, idx) => (
                  <li key={idx} className="text-xs md:text-sm text-slate-300 flex items-start gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-slate-500 mt-2 shrink-0" />
                    <span>{note}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
