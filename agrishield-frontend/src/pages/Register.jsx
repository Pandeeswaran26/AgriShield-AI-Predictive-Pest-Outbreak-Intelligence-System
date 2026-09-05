import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import toast from "react-hot-toast";
import { Leaf, Loader2 } from "lucide-react";
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

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm();

  const onSubmit = async (values) => {
    setSubmitting(true);
    try {
      const data = await authService.register(values);
      setEmail(data.email);
      setStep("otp");
      toast.success("OTP sent to your email");
    } catch (err) {
      const detail = err.response?.data?.detail;
      toast.error(typeof detail === "string" ? detail : "Registration failed");
    } finally {
      setSubmitting(false);
    }
  };

  const onVerify = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await verifyOtp(email, otp);
      toast.success("Account verified");
      navigate("/app/dashboard", { replace: true });
    } catch (err) {
      const detail = err.response?.data?.detail;
      toast.error(typeof detail === "string" ? detail : "Invalid OTP");
    } finally {
      setSubmitting(false);
    }
  };

  const onResend = async () => {
    setResending(true);
    try {
      await authService.resendOtp({ email, purpose: "register" });
      toast.success("OTP resent");
    } catch {
      toast.error("Could not resend OTP");
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

              <form onSubmit={handleSubmit(onSubmit)} className="mt-6 space-y-4">
                <div>
                  <label className="label !text-mist/60">Full name</label>
                  <input
                    className="input !bg-field-950 !border-mist/15 !text-mist"
                    placeholder="Ravi Kumar"
                    {...register("name", { required: "Name is required", minLength: { value: 2, message: "Too short" } })}
                  />
                  {errors.name && <p className="mt-1 text-xs text-alert">{errors.name.message}</p>}
                </div>

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
                  <label className="label !text-mist/60">Phone</label>
                  <input
                    className="input !bg-field-950 !border-mist/15 !text-mist"
                    placeholder="9876543210"
                    {...register("phone", {
                      required: "Phone is required",
                      minLength: { value: 10, message: "Enter a valid phone number" },
                    })}
                  />
                  {errors.phone && <p className="mt-1 text-xs text-alert">{errors.phone.message}</p>}
                </div>

                <div>
                  <label className="label !text-mist/60">Location</label>
                  <input
                    className="input !bg-field-950 !border-mist/15 !text-mist"
                    placeholder="Coimbatore, Tamil Nadu"
                    {...register("location", { required: "Location is required" })}
                  />
                  {errors.location && <p className="mt-1 text-xs text-alert">{errors.location.message}</p>}
                </div>

                <div>
                  <label className="label !text-mist/60">Password</label>
                  <input
                    type="password"
                    className="input !bg-field-950 !border-mist/15 !text-mist"
                    placeholder="At least 6 characters"
                    {...register("password", {
                      required: "Password is required",
                      minLength: { value: 6, message: "Minimum 6 characters" },
                    })}
                  />
                  {errors.password && <p className="mt-1 text-xs text-alert">{errors.password.message}</p>}
                </div>

                <div>
                  <label className="label !text-mist/60">Confirm password</label>
                  <input
                    type="password"
                    className="input !bg-field-950 !border-mist/15 !text-mist"
                    placeholder="Repeat password"
                    {...register("confirm_password", {
                      required: "Please confirm your password",
                      validate: (v) => v === watch("password") || "Passwords do not match",
                    })}
                  />
                  {errors.confirm_password && (
                    <p className="mt-1 text-xs text-alert">{errors.confirm_password.message}</p>
                  )}
                </div>

                <button type="submit" disabled={submitting} className="btn-primary w-full">
                  {submitting && <Loader2 size={16} className="animate-spin" />}
                  Create account
                </button>
              </form>
            </>
          ) : (
            <>
              <h1 className="font-display text-xl font-semibold">Verify your email</h1>
              <p className="mt-1 text-sm text-mist/55">
                Enter the 6-digit code sent to <span className="text-mist">{email}</span>.
              </p>

              <form onSubmit={onVerify} className="mt-6 space-y-4">
                <div>
                  <label className="label !text-mist/60">OTP code</label>
                  <input
                    className="input !bg-field-950 !border-mist/15 !text-mist tracking-[0.4em]"
                    placeholder="000000"
                    maxLength={6}
                    value={otp}
                    onChange={(e) => setOtp(e.target.value.replace(/\D/g, ""))}
                    required
                  />
                </div>

                <button type="submit" disabled={submitting || otp.length < 4} className="btn-primary w-full">
                  {submitting && <Loader2 size={16} className="animate-spin" />}
                  Verify & continue
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
