const SIZES = {
  sm: "h-4 w-4 border-2",
  md: "h-8 w-8 border-2",
  lg: "h-12 w-12 border-[3px]",
};

export default function LoadingSpinner({ size = "md", className = "", label }) {
  return (
    <div className={`flex flex-col items-center justify-center gap-2 ${className}`}>
      <div
        role="status"
        aria-label={label || "Loading"}
        className={`animate-spin rounded-full border-primary-600 border-t-transparent ${SIZES[size]}`}
      />
      {label && <p className="text-xs text-slate-400">{label}</p>}
    </div>
  );
}
