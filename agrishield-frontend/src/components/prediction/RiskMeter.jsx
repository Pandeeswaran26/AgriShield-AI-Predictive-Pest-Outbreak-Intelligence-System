import { motion } from "framer-motion";
import { riskColor } from "../../utils/risk";

// score: 0-100. level: "Low" | "Medium" | "High"
export default function RiskMeter({ score = 0, level = "Low" }) {
  const radius = 90;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;
  const color = riskColor(level);

  return (
    <div className="relative flex h-56 w-56 items-center justify-center">
      <svg width="224" height="224" viewBox="0 0 224 224" className="-rotate-90">
        <circle
          cx="112"
          cy="112"
          r={radius}
          fill="none"
          stroke="currentColor"
          className="text-slate-100 dark:text-white/5"
          strokeWidth="14"
        />
        <motion.circle
          cx="112"
          cy="112"
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth="14"
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1.1, ease: "easeOut" }}
        />
      </svg>
      <div className="absolute flex flex-col items-center">
        <span className="font-mono text-4xl font-bold" style={{ color }}>
          {Math.round(score)}%
        </span>
        <span className="mt-1 text-sm font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
          {level} risk
        </span>
      </div>
    </div>
  );
}
