import { NavLink, useNavigate } from "react-router-dom";
import {
  LayoutDashboard,
  ScanLine,
  Camera,
  ClipboardList,
  History,
  BarChart3,
  MessageCircle,
  Settings as SettingsIcon,
  LogOut,
  Leaf,
  X,
  Droplets,
} from "lucide-react";
import { useAuth } from "../context/AuthContext";
import toast from "react-hot-toast";

const NAVIGATION_LINKS = [
  { to: "/app/dashboard", label: "Dashboard",          icon: LayoutDashboard },
  { to: "/app/diagnosis", label: "Plant Diagnosis",    icon: Camera },
  { to: "/app/predict",   label: "AI Prediction",      icon: ScanLine },
  { to: "/app/irrigation",label: "Irrigation AI",      icon: Droplets },
  { to: "/app/irrigation-history", label: "Irrigation History", icon: History },
  { to: "/app/recommendation", label: "AI Recommendation", icon: ClipboardList },
  { to: "/app/history",   label: "History",             icon: History },
  { to: "/app/analytics", label: "Analytics",           icon: BarChart3 },
  { to: "/app/assistant", label: "AI Assistant",        icon: MessageCircle },
  { to: "/app/settings",  label: "Settings",            icon: SettingsIcon },
];


export default function Sidebar({ onClose, isMobile = false }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    toast.success("Logged out");
    navigate("/login");
  };

  const handleLinkClick = () => {
    if (onClose) onClose();
  };

  return (
    <aside
      className={`${
        isMobile ? "flex h-full w-full" : "hidden md:flex w-64"
      } shrink-0 flex-col border-r border-field-900/10 bg-white dark:border-mist/10 dark:bg-field-950`}
    >
      <div className="flex items-center justify-between px-6 py-6">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-canopy/15 text-canopy">
            <Leaf size={18} />
          </div>
          <span className="font-display text-lg font-semibold">AgriShield</span>
        </div>
        {isMobile && onClose && (
          <button
            onClick={onClose}
            className="rounded-lg p-1.5 text-field-900/50 hover:bg-field-900/10 dark:text-mist/50 dark:hover:bg-mist/10"
            aria-label="Close menu"
          >
            <X size={18} />
          </button>
        )}
      </div>

      <nav className="flex-1 space-y-1 px-3">
        {NAVIGATION_LINKS.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            onClick={handleLinkClick}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition ${
                isActive
                  ? "bg-canopy/12 text-canopy-700 dark:text-canopy"
                  : "text-field-900/70 hover:bg-field-900/5 dark:text-mist/70 dark:hover:bg-mist/5"
              }`
            }
          >
            <Icon size={18} />
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="border-t border-field-900/10 px-4 py-4 dark:border-mist/10">
        <p className="truncate text-sm font-semibold">{user?.name || "Farmer"}</p>
        <p className="truncate text-xs text-field-900/50 dark:text-mist/50">{user?.location || "Field Station"}</p>
        <button onClick={handleLogout} className="btn-ghost mt-3 w-full !py-2 text-xs">
          <LogOut size={14} />
          Log out
        </button>
      </div>
    </aside>
  );
}
