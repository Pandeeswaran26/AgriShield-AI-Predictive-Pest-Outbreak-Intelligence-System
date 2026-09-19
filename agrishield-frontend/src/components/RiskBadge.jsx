const STYLES = {
  Low: "bg-canopy/15 text-canopy-700 dark:text-canopy border-canopy/30",
  Medium: "bg-clay/15 text-clay border-clay/30",
  High: "bg-alert/15 text-alert border-alert/30",
};

export default function RiskBadge({ level, risk, size = "md" }) {
  const currentLevel = level || risk || "Medium";
  const style = STYLES[currentLevel] || STYLES.Medium;
  const sizing = size === "sm" ? "text-[11px] px-2 py-0.5" : "text-xs px-2.5 py-1";
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full border font-semibold ${sizing} ${style}`}>
      <span className="h-1.5 w-1.5 rounded-full bg-current" />
      {currentLevel} risk
    </span>
  );
}
