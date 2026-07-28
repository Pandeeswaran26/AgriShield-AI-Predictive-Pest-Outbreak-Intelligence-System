import { useState } from "react";
import { useForm } from "react-hook-form";
import { Moon, Sun, Bell, Globe, User, Save } from "lucide-react";
import toast from "react-hot-toast";
import { useAuth } from "../context/AuthContext";
import { useTheme } from "../context/ThemeContext";

const LANGUAGES = ["English", "Tamil", "Hindi", "Telugu", "Kannada"];

export default function SettingsPage() {
  const { user } = useAuth();
  const { theme, setTheme } = useTheme();
  const [notifications, setNotifications] = useState({
    highRiskAlerts: true,
    weeklyDigest: true,
    productUpdates: false,
  });
  const [language, setLanguage] = useState("English");

  const { register, handleSubmit, formState: { isSubmitting } } = useForm({
    defaultValues: { name: user?.name || "", email: user?.email || "", location: user?.location || "" },
  });

  const onSaveProfile = async () => {
    // Wire this up to a PATCH /users/me call once the endpoint is available.
    toast.success("Profile updated");
  };

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <form onSubmit={handleSubmit(onSaveProfile)} className="glass-card space-y-4 p-6">
        <div className="flex items-center gap-2">
          <User size={18} className="text-primary-600" />
          <h3 className="font-display font-semibold">Profile</h3>
        </div>
        <div>
          <label className="mb-1.5 block text-sm font-medium">Full name</label>
          <input className="input-field" {...register("name")} />
        </div>
        <div>
          <label className="mb-1.5 block text-sm font-medium">Email</label>
          <input type="email" className="input-field" {...register("email")} />
        </div>
        <div>
          <label className="mb-1.5 block text-sm font-medium">Farm location</label>
          <input className="input-field" {...register("location")} />
        </div>
        <button type="submit" disabled={isSubmitting} className="btn-primary">
          <Save size={16} /> Save profile
        </button>
      </form>

      <div className="space-y-6">
        <div className="glass-card p-6">
          <div className="flex items-center gap-2">
            {theme === "dark" ? <Moon size={18} className="text-primary-600" /> : <Sun size={18} className="text-primary-600" />}
            <h3 className="font-display font-semibold">Theme</h3>
          </div>
          <div className="mt-4 grid grid-cols-2 gap-3">
            {["light", "dark"].map((t) => (
              <button
                key={t}
                onClick={() => setTheme(t)}
                className={`rounded-xl border px-4 py-3 text-sm font-medium capitalize transition-colors ${
                  theme === t
                    ? "border-primary-500 bg-primary-50 text-primary-700 dark:bg-primary-500/10 dark:text-primary-400"
                    : "border-surface-border text-slate-500 dark:border-surface-darkBorder"
                }`}
              >
                {t} mode
              </button>
            ))}
          </div>
        </div>

        <div className="glass-card p-6">
          <div className="flex items-center gap-2">
            <Bell size={18} className="text-primary-600" />
            <h3 className="font-display font-semibold">Notifications</h3>
          </div>
          <div className="mt-4 space-y-3">
            {[
              { key: "highRiskAlerts", label: "High-risk field alerts" },
              { key: "weeklyDigest", label: "Weekly prediction digest" },
              { key: "productUpdates", label: "Product updates" },
            ].map((item) => (
              <label key={item.key} className="flex items-center justify-between text-sm">
                {item.label}
                <input
                  type="checkbox"
                  checked={notifications[item.key]}
                  onChange={(e) =>
                    setNotifications((prev) => ({ ...prev, [item.key]: e.target.checked }))
                  }
                  className="h-4 w-4 accent-primary-600"
                />
              </label>
            ))}
          </div>
        </div>

        <div className="glass-card p-6">
          <div className="flex items-center gap-2">
            <Globe size={18} className="text-primary-600" />
            <h3 className="font-display font-semibold">Language</h3>
          </div>
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            className="input-field mt-4"
          >
            {LANGUAGES.map((lang) => (
              <option key={lang} value={lang}>
                {lang}
              </option>
            ))}
          </select>
        </div>
      </div>
    </div>
  );
}
