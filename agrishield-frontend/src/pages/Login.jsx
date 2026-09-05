import { useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { useForm } from "react-hook-form";
import toast from "react-hot-toast";
import { Leaf, Loader2 } from "lucide-react";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [submitting, setSubmitting] = useState(false);
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm();

  const onSubmit = async (values) => {
    setSubmitting(true);
    try {
      await login(values.email, values.password);
      toast.success("Welcome back");
      navigate(location.state?.from?.pathname || "/app/dashboard", { replace: true });
    } catch (err) {
      const detail = err.response?.data?.detail;
      toast.error(typeof detail === "string" ? detail : "Login failed");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-field-950 px-6 text-mist">
      <div className="w-full max-w-sm">
        <Link to="/" className="mb-8 flex items-center justify-center gap-2">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-canopy/15 text-canopy">
            <Leaf size={18} />
          </div>
          <span className="font-display text-lg font-semibold">AgriShield</span>
        </Link>

        <div className="rounded-2xl border border-mist/10 bg-field-900 p-7">
          <h1 className="font-display text-xl font-semibold">Log in to your farm</h1>
          <p className="mt-1 text-sm text-mist/55">Track predictions and act on this week's risk.</p>

          <form onSubmit={handleSubmit(onSubmit)} className="mt-6 space-y-4">
            <div>
              <label className="label !text-mist/60">Email</label>
              <input
                type="email"
                className="input !bg-field-950 !border-mist/15 !text-mist"
                placeholder="you@farm.com"
                {...register("email", { required: "Email is required" })}
              />
              {errors.email && <p className="mt-1 text-xs text-alert">{errors.email.message}</p>}
            </div>

            <div>
              <label className="label !text-mist/60">Password</label>
              <input
                type="password"
                className="input !bg-field-950 !border-mist/15 !text-mist"
                placeholder="••••••••"
                {...register("password", { required: "Password is required" })}
              />
              {errors.password && <p className="mt-1 text-xs text-alert">{errors.password.message}</p>}
            </div>

            <button type="submit" disabled={submitting} className="btn-primary w-full">
              {submitting && <Loader2 size={16} className="animate-spin" />}
              Log in
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-mist/55">
            New here?{" "}
            <Link to="/register" className="font-semibold text-canopy hover:underline">
              Create an account
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
