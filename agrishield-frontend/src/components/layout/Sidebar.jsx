import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  ScanLine,
  Sparkles,
  History,
  BarChart3,
  Settings,
  Leaf,
  LogOut,
} from "lucide-react";
import { useAuth } from "../../context/AuthContext";

const LINKS = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/predict", label: "AI Prediction", icon: ScanLine },
  { to: "/recommendation", label: "Recommendation", icon: Sparkles },
  { to: "/history", label: "Prediction History", icon: History },
  { to: "/analytics", label: "Analytics", icon: BarChart3 },
  { to: "/settings", label: "Settings", icon: Settings },
];

export default function Sidebar({ open, onClose }) {
  const { user, logout } = useAuth();

  return (
    <>
      {open && (
        <div
          className="fixed inset-0 z-30 bg-black/40 lg:hidden"
          onClick={onClose}
        />
      )}
      <aside
        className={`fixed inset-y-0 left-0 z-40 flex w-64 flex-col border-r border-surface-border bg-white transition-transform dark:border-surface-darkBorder dark:bg-surface-darkMuted lg:translate-x-0 ${
          open ? "translate-x-0" : "-translate-x-full"
        } lg:static`}
      >
        <div className="flex items-center gap-2 px-6 py-5 font-display text-lg font-bold">
          <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary-600 text-white">
            <Leaf size={18} />
          </span>
          AgriShield <span className="text-primary-600">AI</span>
        </div>

        <nav className="flex-1 space-y-1 px-3">
          {LINKS.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              onClick={onClose}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-primary-50 text-primary-700 dark:bg-primary-500/10 dark:text-primary-400"
                    : "text-slate-600 hover:bg-slate-50 dark:text-slate-300 dark:hover:bg-white/5"
                }`
              }
            >
              <Icon size={18} />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="border-t border-surface-border p-4 dark:border-surface-darkBorder">
          <div className="flex items-center gap-3 rounded-xl px-2 py-2">
            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-primary-100 font-display text-sm font-semibold text-primary-700 dark:bg-primary-500/10 dark:text-primary-400">
              {user?.name?.[0]?.toUpperCase() || "F"}
            </div>
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-semibold">
                {user?.name || "Farmer Account"}
              </p>
              <p className="truncate text-xs text-slate-400">
                {user?.role || "farmer"}
              </p>
            </div>
            <button
              onClick={logout}
              aria-label="Log out"
              className="rounded-lg p-2 text-slate-400 hover:bg-red-50 hover:text-red-500 dark:hover:bg-red-500/10"
            >
              <LogOut size={16} />
            </button>
          </div>
        </div>
      </aside>
    </>
  );
}
