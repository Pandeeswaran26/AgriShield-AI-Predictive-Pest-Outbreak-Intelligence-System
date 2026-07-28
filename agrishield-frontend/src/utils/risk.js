// Shared helpers for turning a raw model risk score/label into UI-ready values.

export const RISK_LEVELS = {
  LOW: "Low",
  MEDIUM: "Medium",
  HIGH: "High",
};

export function riskColor(level) {
  switch ((level || "").toLowerCase()) {
    case "high":
      return "#EF4444";
    case "medium":
      return "#F59E0B";
    case "low":
    default:
      return "#22C55E";
  }
}

export function riskBadgeClasses(level) {
  switch ((level || "").toLowerCase()) {
    case "high":
      return "bg-red-50 text-red-700 border-red-200 dark:bg-red-500/10 dark:text-red-400 dark:border-red-500/20";
    case "medium":
      return "bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-500/10 dark:text-amber-400 dark:border-amber-500/20";
    case "low":
    default:
      return "bg-primary-50 text-primary-700 border-primary-200 dark:bg-primary-500/10 dark:text-primary-400 dark:border-primary-500/20";
  }
}

export function formatPercent(value, digits = 1) {
  if (value === null || value === undefined || Number.isNaN(value)) return "—";
  return `${Number(value).toFixed(digits)}%`;
}
