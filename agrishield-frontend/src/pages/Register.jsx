import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import toast from "react-hot-toast";
import { Leaf, Loader2, AlertCircle, Eye, EyeOff } from "lucide-react";
import * as authService from "../services/authService";
import { useAuth } from "../context/AuthContext";

export default function Register() {
  const navigate = useNavigate();
  const { verifyOtp } = useAuth();
  const [step, setStep] = useState("form"); // "form" | "otp"
  const [email, setEmail] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [otp, setOtp] = useState("");
  const [resending, setResending] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm();

  const clearError = () => {
    if (errorMessage) {
      setErrorMessage(null);
    }
  };

  const onSubmit = async (values) => {
    setErrorMessage(null);

    // Verify password confirmation before submission
    if (values.password !== values.confirm_password) {
      const mismatchMsg = "Passwords do not match.";
      setErrorMessage(mismatchMsg);
      toast.error(mismatchMsg);
      return;
    }

    setSubmitting(true);
    try {
      const data = await authService.register(values);
      setEmail(data.email);
      setStep("otp");
      setErrorMessage(null);
      toast.success("OTP sent to your email");
    } catch (err) {
      console.error("Registration error:", err);
      let friendlyMessage = "Registration could not be completed. Please try again later.";

      if (!err.response) {
        friendlyMessage = "Unable to connect to the server. Please try again.";
      } else if (err.response.status === 409) {
        const detail = err.response.data?.detail;
        friendlyMessage =
          typeof detail === "string" && detail.trim()
            ? detail
            : "An account with this email already exists. Please log in.";
      } else if (err.response.status === 400) {
        const detail = err.response.data?.detail;
        friendlyMessage =
          typeof detail === "string" && detail.trim()
            ? detail
            : "Please check the information entered.";
      } else if (err.response.status === 422) {
        friendlyMessage = "Please check the information entered.";
      } else if (err.response.status >= 500) {
        friendlyMessage = "Registration could not be completed. Please try again later.";
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

  const onVerify = async (e) => {
    e.preventDefault();
    setErrorMessage(null);
    setSubmitting(true);
    try {
      await verifyOtp(email, otp);
      toast.success("Account verified");
      navigate("/app/dashboard", { replace: true });
    } catch (err) {
      let friendlyMessage = "Invalid or expired OTP.";
      if (!err.response) {
        friendlyMessage = "Unable to connect to the server. Please try again.";
      } else {
        const detail = err.response?.data?.detail;
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

  const onResend = async () => {
    setErrorMessage(null);
    setResending(true);
    try {
      await authService.resendOtp({ email, purpose: "register" });
      toast.success("OTP resent to your email");
    } catch (err) {
      let msg = "Could not resend OTP. Please try again later.";
      if (!err.response) {
        msg = "Unable to connect to the server. Please try again.";
      } else if (err.response?.data?.detail) {
        msg = err.response.data.detail;
      }
      setErrorMessage(msg);
      toast.error(msg);
    } finally {
      setResending(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-field-950 px-6 py-12 text-mist">
      <div className="w-full max-w-sm">
        <Link to="/" className="mb-8 flex items-center justify-center gap-2">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-canopy/15 text-canopy">
            <Leaf size={18} />
          </div>
          <span className="font-display text-lg font-semibold">AgriShield</span>
        </Link>

        <div className="rounded-2xl border border-mist/10 bg-field-900 p-7">
          {step === "form" ? (
            <>
              <h1 className="font-display text-xl font-semibold">Create your account</h1>
              <p className="mt-1 text-sm text-mist/55">Start scoring pest risk for your fields.</p>

              {errorMessage && (
                <div
                  id="register-error-alert"
                  role="alert"
                  className="mt-4 flex items-start gap-2.5 rounded-lg border border-alert/30 bg-alert/10 p-3 text-xs text-alert"
                >
                  <AlertCircle size={16} className="mt-0.5 shrink-0" />
                  <span className="leading-relaxed">{errorMessage}</span>
                </div>
              )}

              <form onSubmit={handleSubmit(onSubmit)} className="mt-6 space-y-4">
                <div>
                  <label className="label !text-mist/60">Full name</label>
                  <input
                    className="input !bg-field-950 !border-mist/15 !text-mist"
                    placeholder="Ravi Kumar"
                    {...register("name", {
                      required: "Name is required",
                      minLength: { value: 2, message: "Too short" },
                      onChange: clearError,
                    })}
                  />
                  {errors.name && <p className="mt-1 text-xs text-alert">{errors.name.message}</p>}
                </div>

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
                  <label className="label !text-mist/60">Phone</label>
                  <input
                    className="input !bg-field-950 !border-mist/15 !text-mist"
                    placeholder="9876543210"
                    {...register("phone", {
                      required: "Phone is required",
                      minLength: { value: 10, message: "Enter a valid phone number" },
                      onChange: clearError,
                    })}
                  />
                  {errors.phone && <p className="mt-1 text-xs text-alert">{errors.phone.message}</p>}
                </div>

                <div>
                  <label className="label !text-mist/60">Location</label>
                  <input
                    className="input !bg-field-950 !border-mist/15 !text-mist"
                    placeholder="Coimbatore, Tamil Nadu"
                    {...register("location", {
                      required: "Location is required",
                      onChange: clearError,
                    })}
                  />
                  {errors.location && <p className="mt-1 text-xs text-alert">{errors.location.message}</p>}
                </div>

                <div>
                  <label className="label !text-mist/60">Password</label>
                  <div className="relative">
                    <input
                      type={showPassword ? "text" : "password"}
                      className="input !bg-field-950 !border-mist/15 !text-mist pr-10"
                      placeholder="At least 6 characters"
                      {...register("password", {
                        required: "Password is required",
                        minLength: { value: 6, message: "Minimum 6 characters" },
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

                <div>
                  <label className="label !text-mist/60">Confirm password</label>
                  <div className="relative">
                    <input
                      type={showConfirmPassword ? "text" : "password"}
                      className="input !bg-field-950 !border-mist/15 !text-mist pr-10"
                      placeholder="Repeat password"
                      {...register("confirm_password", {
                        required: "Please confirm your password",
                        validate: (v) => v === watch("password") || "Passwords do not match",
                        onChange: clearError,
                      })}
                    />
                    <button
                      type="button"
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-mist/40 hover:text-mist focus:outline-none"
                      aria-label={showConfirmPassword ? "Hide confirm password" : "Show confirm password"}
                    >
                      {showConfirmPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                    </button>
                  </div>
                  {errors.confirm_password && (
                    <p className="mt-1 text-xs text-alert">{errors.confirm_password.message}</p>
                  )}
                </div>

                <button type="submit" disabled={submitting} className="btn-primary w-full">
                  {submitting && <Loader2 size={16} className="animate-spin" />}
                  {submitting ? "Creating account..." : "Create account"}
                </button>
              </form>
            </>
          ) : (
            <>
              <h1 className="font-display text-xl font-semibold">Verify your email</h1>
              <p className="mt-1 text-sm text-mist/55">
                Enter the 6-digit code sent to <span className="text-mist">{email}</span>.
              </p>

              {errorMessage && (
                <div
                  id="otp-error-alert"
                  role="alert"
                  className="mt-4 flex items-start gap-2.5 rounded-lg border border-alert/30 bg-alert/10 p-3 text-xs text-alert"
                >
                  <AlertCircle size={16} className="mt-0.5 shrink-0" />
                  <span className="leading-relaxed">{errorMessage}</span>
                </div>
              )}

              <form onSubmit={onVerify} className="mt-6 space-y-4">
                <div>
                  <label className="label !text-mist/60">OTP code</label>
                  <input
                    className="input !bg-field-950 !border-mist/15 !text-mist tracking-[0.4em]"
                    placeholder="000000"
                    maxLength={6}
                    value={otp}
                    onChange={(e) => {
                      clearError();
                      setOtp(e.target.value.replace(/\D/g, ""));
                    }}
                    required
                  />
                </div>

                <button type="submit" disabled={submitting || otp.length < 4} className="btn-primary w-full">
                  {submitting && <Loader2 size={16} className="animate-spin" />}
                  {submitting ? "Verifying..." : "Verify & continue"}
                </button>

                <button
                  type="button"
                  onClick={onResend}
                  disabled={resending}
                  className="btn-ghost w-full !border-mist/15 !text-mist"
                >
                  {resending ? "Resending…" : "Resend code"}
                </button>
              </form>
            </>
          )}

          <p className="mt-6 text-center text-sm text-mist/55">
            Already have an account?{" "}
            <Link to="/login" className="font-semibold text-canopy hover:underline">
              Log in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
