export default function LoadingSpinner({ label = "Loading" }) {
  return (
    <div className="flex flex-col items-center gap-3 py-10 text-field-900/60 dark:text-mist/60">
      <div className="relative h-9 w-9">
        <div className="absolute inset-0 rounded-full border-2 border-canopy/20" />
        <div className="absolute inset-0 rounded-full border-2 border-canopy border-t-transparent animate-spin" />
      </div>
      <span className="text-xs font-mono uppercase tracking-widest">{label}</span>
    </div>
  );
}
