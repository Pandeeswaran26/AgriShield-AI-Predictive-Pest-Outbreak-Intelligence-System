import { useState } from "react";
import { useForm } from "react-hook-form";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Leaf, Mail, Lock, Eye, EyeOff, Loader2 } from "lucide-react";
import toast from "react-hot-toast";
import authService from "../services/authService";
import { useAuth } from "../context/AuthContext";

export default function LoginPage() {
  const [role, setRole] = useState("farmer");
  const [showPassword, setShowPassword] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm();

  const onSubmit = async (values) => {
    try {
      const call = role === "admin" ? authService.loginAdmin : authService.loginFarmer;
      const data = await call(values);
      login({ user: { ...data.user, role }, token: data.token });
      toast.success(`Welcome back, ${data.user?.name || "there"}!`);
      navigate(location.state?.from?.pathname || "/dashboard", { replace: true });
    } catch (err) {
      toast.error(err.message || "Login failed. Check your credentials.");
    }
  };

  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden bg-surface-muted px-4 dark:bg-surface-dark">
      <div className="absolute inset-0 bg-field-grid bg-grid opacity-40 [mask-image:radial-gradient(ellipse_60%_60%_at_50%_0%,black,transparent)]" />

      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-card relative w-full max-w-md p-8"
      >
        <Link to="/" className="mb-8 flex items-center justify-center gap-2 font-display text-lg font-bold">
          <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary-600 text-white">
            <Leaf size={18} />
          </span>
          AgriShield <span className="text-primary-600">AI</span>
        </Link>

        <h1 className="text-center text-2xl font-bold">Welcome back</h1>
        <p className="mt-1 text-center text-sm text-slate-500 dark:text-slate-400">
          Log in to view field predictions and analytics.
        </p>

        <div className="mt-6 grid grid-cols-2 rounded-xl bg-slate-100 p-1 dark:bg-white/5">
          {["farmer", "admin"].map((r) => (
            <button
              key={r}
              type="button"
              onClick={() => setRole(r)}
              className={`rounded-lg py-2 text-sm font-semibold capitalize transition-colors ${
                role === r
                  ? "bg-white text-primary-700 shadow-sm dark:bg-surface-darkMuted dark:text-primary-400"
                  : "text-slate-500 dark:text-slate-400"
              }`}
            >
              {r} login
            </button>
          ))}
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="mt-6 space-y-4">
          <div>
            <label className="mb-1.5 block text-sm font-medium">Email</label>
            <div className="relative">
              <Mail size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="email"
                placeholder="you@example.com"
                className="input-field pl-10"
                {...register("email", { required: "Email is required" })}
              />
            </div>
            {errors.email && <p className="mt-1 text-xs text-red-500">{errors.email.message}</p>}
          </div>

          <div>
            <label className="mb-1.5 block text-sm font-medium">Password</label>
            <div className="relative">
              <Lock size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type={showPassword ? "text" : "password"}
                placeholder="••••••••"
                className="input-field px-10"
                {...register("password", { required: "Password is required" })}
              />
              <button
                type="button"
                onClick={() => setShowPassword((v) => !v)}
                className="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-400"
              >
                {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
            {errors.password && (
              <p className="mt-1 text-xs text-red-500">{errors.password.message}</p>
            )}
          </div>

          <button type="submit" disabled={isSubmitting} className="btn-primary w-full py-2.5">
            {isSubmitting ? <Loader2 size={18} className="animate-spin" /> : `Log in as ${role}`}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-slate-500 dark:text-slate-400">
          Don't have an account?{" "}
          <Link to="/register" className="font-semibold text-primary-600 hover:underline">
            Register
          </Link>
        </p>
      </motion.div>
    </div>
  );
}
