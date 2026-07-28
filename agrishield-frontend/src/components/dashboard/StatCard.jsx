import { motion } from "framer-motion";

export default function StatCard({ icon: Icon, label, value, tone = "primary", loading }) {
  const toneClasses = {
    primary: "bg-primary-50 text-primary-600 dark:bg-primary-500/10 dark:text-primary-400",
    accent: "bg-accent-50 text-accent-600 dark:bg-accent-500/10 dark:text-accent-400",
    high: "bg-red-50 text-red-600 dark:bg-red-500/10 dark:text-red-400",
    medium: "bg-amber-50 text-amber-600 dark:bg-amber-500/10 dark:text-amber-400",
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -4 }}
      className="glass-card p-5"
    >
      <div className="flex items-center justify-between">
        <p className="text-sm font-medium text-slate-500 dark:text-slate-400">{label}</p>
        <span className={`flex h-9 w-9 items-center justify-center rounded-lg ${toneClasses[tone]}`}>
          <Icon size={18} />
        </span>
      </div>
      {loading ? (
        <div className="skeleton mt-3 h-8 w-20" />
      ) : (
        <p className="mt-2 font-display text-3xl font-bold">{value}</p>
      )}
    </motion.div>
  );
}
