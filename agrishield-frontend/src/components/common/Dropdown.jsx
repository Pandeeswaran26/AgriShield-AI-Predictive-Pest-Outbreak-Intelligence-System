import { useEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { ChevronDown } from "lucide-react";

/**
 * Generic dropdown menu.
 * items: [{ label, icon?: LucideIcon, onClick, danger?: boolean }]
 */
export default function Dropdown({ trigger, items, align = "right" }) {
  const [open, setOpen] = useState(false);
  const ref = useRef(null);

  useEffect(() => {
    const onClickOutside = (e) => {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false);
    };
    document.addEventListener("mousedown", onClickOutside);
    return () => document.removeEventListener("mousedown", onClickOutside);
  }, []);

  return (
    <div ref={ref} className="relative inline-block text-left">
      <button onClick={() => setOpen((v) => !v)} className="flex items-center gap-1">
        {trigger}
        <ChevronDown size={14} className={`transition-transform ${open ? "rotate-180" : ""}`} />
      </button>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: -6, scale: 0.97 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -6, scale: 0.97 }}
            transition={{ duration: 0.15 }}
            className={`glass-card absolute z-50 mt-2 w-48 !bg-white p-1.5 dark:!bg-surface-darkMuted ${
              align === "right" ? "right-0" : "left-0"
            }`}
          >
            {items.map(({ label, icon: Icon, onClick, danger }) => (
              <button
                key={label}
                onClick={() => {
                  onClick?.();
                  setOpen(false);
                }}
                className={`flex w-full items-center gap-2 rounded-lg px-3 py-2 text-left text-sm transition-colors ${
                  danger
                    ? "text-red-500 hover:bg-red-50 dark:hover:bg-red-500/10"
                    : "text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-white/5"
                }`}
              >
                {Icon && <Icon size={15} />}
                {label}
              </button>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
