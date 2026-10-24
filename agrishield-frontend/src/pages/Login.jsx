import { useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { useForm } from "react-hook-form";
import toast from "react-hot-toast";
import { Leaf, Loader2, Eye, EyeOff, AlertCircle } from "lucide-react";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [submitting, setSubmitting] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm();

  const clearError = () => {
    if (errorMessage) {
      setErrorMessage(null);
    }
  };

  const handleLoginSubmit = async (email, password) => {
    setErrorMessage(null);
    setSubmitting(true);
    try {
      await login(email, password);
      toast.success("Welcome back");
      navigate(location.state?.from?.pathname || "/app/dashboard", { replace: true });
    } catch (err) {
      console.error("Login attempt failed:", err);
      let friendlyMessage = "Invalid email or password.";

      if (!err.response) {
        friendlyMessage = "Unable to connect to the server. Please try again.";
      } else if (err.response.status === 429) {
        friendlyMessage = "Too many login attempts. Please try again later.";
      } else if (err.response.status === 422) {
        friendlyMessage = "Please enter a valid email and password.";
      } else if (err.response.status === 401) {
        const detail = err.response.data?.detail;
        if (typeof detail === "string" && detail.trim()) {
          friendlyMessage = detail;
        } else {
          friendlyMessage = "Invalid email or password.";
        }
      } else if (err.response.status === 403) {
        const detail = err.response.data?.detail;
        friendlyMessage =
          typeof detail === "string" && detail.trim()
            ? detail
            : "Account is not verified. Please verify OTP first.";
      } else if (err.response.status >= 500) {
        friendlyMessage = "Unable to connect to the server. Please try again.";
      } else {
        const detail = err.response.data?.detail;
        if (typeof detail === "string" && detail.trim()) {
          friendlyMessage = detail;
        }
      }

      setErrorMessage(friendlyMessage);
      toast.error(friendlyMessage);
    } finally {
      setSubmitting(false);
    }
  };

  const onSubmit = async (values) => {
    await handleLoginSubmit(values.email, values.password);
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

          {errorMessage && (
            <div
              id="login-error-alert"
              role="alert"
              className="mt-4 flex items-start gap-2.5 rounded-lg border border-alert/30 bg-alert/10 p-3 text-xs text-alert"
            >
              <AlertCircle size={16} className="mt-0.5 shrink-0" />
              <span className="leading-relaxed">{errorMessage}</span>
            </div>
          )}

          <form onSubmit={handleSubmit(onSubmit)} className="mt-6 space-y-4">
            <div>
              <label className="label !text-mist/60">Email</label>
              <input
                type="email"
                className="input !bg-field-950 !border-mist/15 !text-mist"
                placeholder="you@farm.com"
                {...register("email", {
                  required: "Email is required",
                  onChange: clearError,
                })}
              />
              {errors.email && <p className="mt-1 text-xs text-alert">{errors.email.message}</p>}
            </div>

            <div>
              <label className="label !text-mist/60">Password</label>
              <div className="relative">
                <input
                  type={showPassword ? "text" : "password"}
                  className="input !bg-field-950 !border-mist/15 !text-mist pr-10"
                  placeholder="••••••••"
                  {...register("password", {
                    required: "Password is required",
                    onChange: clearError,
                  })}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-mist/40 hover:text-mist focus:outline-none"
                  aria-label={showPassword ? "Hide password" : "Show password"}
                >
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
              {errors.password && <p className="mt-1 text-xs text-alert">{errors.password.message}</p>}
            </div>

            <button type="submit" disabled={submitting} className="btn-primary w-full">
              {submitting && <Loader2 size={16} className="animate-spin" />}
              {submitting ? "Logging in..." : "Log in"}
            </button>
          </form>

          <p className="mt-5 text-center text-sm text-mist/55">
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
