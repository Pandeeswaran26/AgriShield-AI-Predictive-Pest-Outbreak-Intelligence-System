export default function StatCard({ label, value, sublabel, accent = "canopy" }) {
  const accentClass = {
    canopy: "text-canopy",
    clay: "text-clay",
    alert: "text-alert",
    sky: "text-sky",
  }[accent];

  return (
    <div className="card p-5 animate-rise">
      <p className="label mb-2">{label}</p>
      <p className={`font-display text-3xl font-semibold ${accentClass}`}>{value}</p>
      {sublabel && <p className="mt-1 text-xs text-field-900/50 dark:text-mist/50">{sublabel}</p>}
    </div>
  );
}
