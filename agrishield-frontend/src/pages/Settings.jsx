import { useEffect, useState } from "react";
import toast from "react-hot-toast";
import { Moon, Sun, User, MapPin, Mail, Phone, LogOut } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Settings() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [dark, setDark] = useState(() => localStorage.getItem("agrishield_theme") !== "light");

  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
    localStorage.setItem("agrishield_theme", dark ? "dark" : "light");
  }, [dark]);

  const handleLogout = async () => {
    await logout();
    toast.success("Logged out");
    navigate("/login");
  };

  return (
    <div className="max-w-xl space-y-6">
      <div>
        <h1 className="font-display text-2xl font-semibold">Settings</h1>
        <p className="mt-1 text-sm text-field-900/55 dark:text-mist/55">
          Your account and app preferences.
        </p>
      </div>

      <div className="card p-6">
        <h2 className="font-display text-base font-semibold">Account</h2>
        <div className="mt-4 space-y-3 text-sm">
          <InfoRow icon={User} label="Name" value={user?.name} />
          <InfoRow icon={Mail} label="Email" value={user?.email} />
          <InfoRow icon={Phone} label="Phone" value={user?.phone} />
          <InfoRow icon={MapPin} label="Location" value={user?.location} />
        </div>
      </div>

      <div className="card p-6">
        <h2 className="font-display text-base font-semibold">Appearance</h2>
        <div className="mt-4 flex items-center justify-between rounded-xl border border-field-900/10 p-4 dark:border-mist/10">
          <div className="flex items-center gap-3">
            {dark ? <Moon size={18} className="text-canopy" /> : <Sun size={18} className="text-clay" />}
            <div>
              <p className="text-sm font-medium">Dark mode</p>
              <p className="text-xs text-field-900/50 dark:text-mist/50">Applies across the dashboard</p>
            </div>
          </div>
          <button
            role="switch"
            aria-checked={dark}
            onClick={() => setDark((v) => !v)}
            className={`relative h-6 w-11 rounded-full transition ${dark ? "bg-canopy" : "bg-field-900/20"}`}
          >
            <span
              className={`absolute top-0.5 h-5 w-5 rounded-full bg-white transition ${
                dark ? "left-[22px]" : "left-0.5"
              }`}
            />
          </button>
        </div>
      </div>

      <div className="card p-6">
        <h2 className="font-display text-base font-semibold">Session</h2>
        <button onClick={handleLogout} className="btn-ghost mt-4 w-full">
          <LogOut size={15} /> Log out
        </button>
      </div>
    </div>
  );
}

function InfoRow({ icon: Icon, label, value }) {
  return (
    <div className="flex items-center gap-3 rounded-xl border border-field-900/10 px-4 py-3 dark:border-mist/10">
      <Icon size={16} className="text-field-900/40 dark:text-mist/40" />
      <div className="min-w-0">
        <p className="text-xs text-field-900/50 dark:text-mist/50">{label}</p>
        <p className="truncate font-medium">{value || "—"}</p>
      </div>
    </div>
  );
}
