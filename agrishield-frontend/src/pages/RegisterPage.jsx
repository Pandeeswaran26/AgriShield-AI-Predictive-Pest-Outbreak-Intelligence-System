import { useForm } from "react-hook-form";
import { Link, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Leaf, Loader2 } from "lucide-react";
import toast from "react-hot-toast";
import authService from "../services/authService";
import { useAuth } from "../context/AuthContext";

export default function RegisterPage() {
  const { login } = useAuth();
  const navigate = useNavigate();

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting },
  } = useForm();

  const onSubmit = async (values) => {
    try {
      const data = await authService.register(values);
      login({ user: { ...data.user, role: "farmer" }, token: data.token });
      toast.success("Account created — welcome to AgriShield AI!");
      navigate("/dashboard", { replace: true });
    } catch (err) {
      toast.error(err.message || "Registration failed. Please try again.");
    }
  };

  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden bg-surface-muted px-4 py-12 dark:bg-surface-dark">
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

        <h1 className="text-center text-2xl font-bold">Create your account</h1>
        <p className="mt-1 text-center text-sm text-slate-500 dark:text-slate-400">
          Start predicting pest risk for your fields in minutes.
        </p>

        <form onSubmit={handleSubmit(onSubmit)} className="mt-6 space-y-4">
          <div>
            <label className="mb-1.5 block text-sm font-medium">Full name</label>
            <input
              placeholder="Jane Farmer"
              className="input-field"
              {...register("name", { required: "Name is required" })}
            />
            {errors.name && <p className="mt-1 text-xs text-red-500">{errors.name.message}</p>}
          </div>

          <div>
            <label className="mb-1.5 block text-sm font-medium">Email</label>
            <input
              type="email"
              placeholder="you@example.com"
              className="input-field"
              {...register("email", { required: "Email is required" })}
            />
            {errors.email && <p className="mt-1 text-xs text-red-500">{errors.email.message}</p>}
          </div>

          <div>
            <label className="mb-1.5 block text-sm font-medium">Farm location</label>
            <input
              placeholder="e.g. Coimbatore"
              className="input-field"
              {...register("location", { required: "Location is required" })}
            />
            {errors.location && (
              <p className="mt-1 text-xs text-red-500">{errors.location.message}</p>
            )}
          </div>

          <div>
            <label className="mb-1.5 block text-sm font-medium">Password</label>
            <input
              type="password"
              placeholder="••••••••"
              className="input-field"
              {...register("password", {
                required: "Password is required",
                minLength: { value: 8, message: "At least 8 characters" },
              })}
            />
            {errors.password && (
              <p className="mt-1 text-xs text-red-500">{errors.password.message}</p>
            )}
          </div>

          <div>
            <label className="mb-1.5 block text-sm font-medium">Confirm password</label>
            <input
              type="password"
              placeholder="••••••••"
              className="input-field"
              {...register("confirmPassword", {
                required: "Please confirm your password",
                validate: (v) => v === watch("password") || "Passwords do not match",
              })}
            />
            {errors.confirmPassword && (
              <p className="mt-1 text-xs text-red-500">{errors.confirmPassword.message}</p>
            )}
          </div>

          <button type="submit" disabled={isSubmitting} className="btn-primary w-full py-2.5">
            {isSubmitting ? <Loader2 size={18} className="animate-spin" /> : "Create account"}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-slate-500 dark:text-slate-400">
          Already have an account?{" "}
          <Link to="/login" className="font-semibold text-primary-600 hover:underline">
            Log in
          </Link>
        </p>
      </motion.div>
    </div>
  );
}
