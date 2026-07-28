import { Menu, Moon, Sun, Bell, Settings, LogOut, User } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useTheme } from "../../context/ThemeContext";
import { useAuth } from "../../context/AuthContext";
import Dropdown from "../common/Dropdown";

export default function Topbar({ title, onMenuClick }) {
  const { theme, toggleTheme } = useTheme();
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <header className="flex items-center justify-between border-b border-surface-border bg-white/80 px-4 py-4 backdrop-blur-sm dark:border-surface-darkBorder dark:bg-surface-dark/80 sm:px-8">
      <div className="flex items-center gap-3">
        <button
          onClick={onMenuClick}
          className="rounded-lg p-2 text-slate-500 hover:bg-slate-100 dark:hover:bg-white/5 lg:hidden"
          aria-label="Open menu"
        >
          <Menu size={20} />
        </button>
        <h1 className="font-display text-xl font-bold">{title}</h1>
      </div>

      <div className="flex items-center gap-2">
        <button
          className="rounded-lg p-2 text-slate-500 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-white/5"
          aria-label="Notifications"
        >
          <Bell size={18} />
        </button>
        <button
          onClick={toggleTheme}
          className="rounded-lg p-2 text-slate-500 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-white/5"
          aria-label="Toggle dark mode"
        >
          {theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}
        </button>

        <Dropdown
          trigger={
            <span className="flex h-9 w-9 items-center justify-center rounded-full bg-primary-100 font-display text-sm font-semibold text-primary-700 dark:bg-primary-500/10 dark:text-primary-400">
              {user?.name?.[0]?.toUpperCase() || "F"}
            </span>
          }
          items={[
            { label: "Profile settings", icon: User, onClick: () => navigate("/settings") },
            { label: "Settings", icon: Settings, onClick: () => navigate("/settings") },
            { label: "Log out", icon: LogOut, onClick: logout, danger: true },
          ]}
        />
      </div>
    </header>
  );
}
