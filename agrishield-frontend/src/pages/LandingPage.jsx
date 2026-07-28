import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import {
  ScanLine,
  Brain,
  ShieldCheck,
  LineChart,
  Sprout,
  CloudSun,
  ArrowRight,
  CheckCircle2,
  Github,
  Mail,
  Cpu,
} from "lucide-react";

const FEATURES = [
  {
    icon: ScanLine,
    title: "Weekly field scans",
    desc: "Feed in standard-week weather and field readings and get an outbreak risk score before pests take hold.",
  },
  {
    icon: Brain,
    title: "Extra Trees model",
    desc: "A tuned ExtraTreesRegressor trained on multi-season crop and weather data predicts pest pressure, not just presence.",
  },
  {
    icon: ShieldCheck,
    title: "SHAP explanations",
    desc: "Every prediction ships with the exact factors that drove it, so agronomists can trust and act on the score.",
  },
  {
    icon: LineChart,
    title: "Trend-aware analytics",
    desc: "Track pest pressure, weather impact, and crop-level risk across seasons in one analytics workspace.",
  },
  {
    icon: Sprout,
    title: "Crop-specific guidance",
    desc: "Recommendations adapt to the crop and pest pair — prevention steps, pesticide options, and organic alternatives.",
  },
  {
    icon: CloudSun,
    title: "Weather-linked risk",
    desc: "Temperature, humidity, rainfall, wind, sunshine, and evaporation feed directly into the risk calculation.",
  },
];

const BENEFITS = [
  "Catch outbreak conditions before visible crop damage",
  "Cut unnecessary pesticide spend with targeted alerts",
  "Give every prediction a transparent, explainable reason",
  "Compare risk across fields, crops, and seasons at a glance",
];

const TECHNOLOGIES = [
  { label: "FastAPI", role: "Backend API" },
  { label: "Scikit-Learn", role: "Extra Trees model" },
  { label: "SHAP", role: "Explainability" },
  { label: "React 19", role: "Frontend" },
  { label: "Recharts", role: "Analytics" },
  { label: "Tailwind CSS", role: "Design system" },
];

const FAQS = [
  {
    q: "What data does a prediction need?",
    a: "Crop, pest, location, observation year and standard week, plus max/min temperature, two humidity readings, rainfall, wind speed, sunshine hours, and evaporation — the same feature set the Extra Trees model was trained on.",
  },
  {
    q: "How is the risk score calculated?",
    a: "The FastAPI backend runs your inputs through the trained ExtraTreesRegressor and converts the predicted pest value into a 0–100 risk score with a Low/Medium/High band.",
  },
  {
    q: "Can I see why a prediction was made?",
    a: "Yes — each prediction page includes a SHAP-based breakdown showing which inputs pushed the risk score up or down.",
  },
  {
    q: "Does it work for more than one crop?",
    a: "The model is trained across multiple crops and locations, and the prediction form lets you choose the crop and pest pair per field.",
  },
];

const fadeUp = {
  hidden: { opacity: 0, y: 20 },
  show: (i = 0) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.08, duration: 0.5, ease: "easeOut" },
  }),
};

export default function LandingPage() {
  return (
    <div>
      {/* ---------------- HERO ---------------- */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-field-grid bg-grid [mask-image:radial-gradient(ellipse_60%_60%_at_50%_0%,black,transparent)]" />
        <div className="absolute inset-x-0 top-0 h-px overflow-hidden">
          <div className="h-40 w-full animate-scan bg-gradient-to-b from-transparent via-primary-500/40 to-transparent" />
        </div>

        <div className="relative mx-auto max-w-5xl px-6 pb-24 pt-20 text-center sm:pt-28">
          <motion.span
            initial="hidden"
            animate="show"
            variants={fadeUp}
            className="section-eyebrow inline-flex items-center gap-2 rounded-full border border-primary-200 bg-primary-50 px-3 py-1 dark:border-primary-500/20 dark:bg-primary-500/10"
          >
            <Cpu size={12} /> Extra Trees + SHAP, in production
          </motion.span>

          <motion.h1
            initial="hidden"
            animate="show"
            variants={fadeUp}
            custom={1}
            className="mx-auto mt-6 max-w-3xl text-4xl font-bold leading-[1.1] tracking-tight sm:text-6xl"
          >
            Know a pest outbreak
            <span className="text-primary-600"> before the field does.</span>
          </motion.h1>

          <motion.p
            initial="hidden"
            animate="show"
            variants={fadeUp}
            custom={2}
            className="mx-auto mt-6 max-w-2xl text-lg text-slate-600 dark:text-slate-300"
          >
            AgriShield AI turns weekly weather and field readings into an
            explainable pest-risk score — so you can act on week 24, not
            week 30.
          </motion.p>

          <motion.div
            initial="hidden"
            animate="show"
            variants={fadeUp}
            custom={3}
            className="mt-10 flex flex-col items-center justify-center gap-3 sm:flex-row"
          >
            <Link to="/register" className="btn-primary px-6 py-3 text-base">
              Get started free <ArrowRight size={18} />
            </Link>
            <a href="#features" className="btn-secondary px-6 py-3 text-base">
              See how it works
            </a>
          </motion.div>

          <motion.div
            initial="hidden"
            animate="show"
            variants={fadeUp}
            custom={4}
            className="glass-card mx-auto mt-16 grid max-w-3xl grid-cols-2 gap-6 p-6 text-left sm:grid-cols-4"
          >
            {[
              ["13", "model input features"],
              ["5-fold", "cross validation"],
              ["Low/Med/High", "risk banding"],
              ["Weekly", "standard-week cadence"],
            ].map(([stat, label]) => (
              <div key={label}>
                <p className="font-mono text-xl font-bold text-primary-600">{stat}</p>
                <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">{label}</p>
              </div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* ---------------- FEATURES ---------------- */}
      <section id="features" className="mx-auto max-w-7xl px-6 py-24">
        <div className="mx-auto max-w-2xl text-center">
          <p className="section-eyebrow">Features</p>
          <h2 className="mt-3 text-3xl font-bold sm:text-4xl">
            Everything between raw field data and a decision
          </h2>
        </div>

        <div className="mt-14 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {FEATURES.map(({ icon: Icon, title, desc }, i) => (
            <motion.div
              key={title}
              initial="hidden"
              whileInView="show"
              viewport={{ once: true }}
              variants={fadeUp}
              custom={i}
              whileHover={{ y: -4 }}
              className="glass-card p-6"
            >
              <span className="flex h-11 w-11 items-center justify-center rounded-xl bg-primary-50 text-primary-600 dark:bg-primary-500/10 dark:text-primary-400">
                <Icon size={20} />
              </span>
              <h3 className="mt-4 font-display text-lg font-semibold">{title}</h3>
              <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">{desc}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* ---------------- ABOUT ---------------- */}
      <section id="about" className="bg-white py-24 dark:bg-surface-darkMuted/40">
        <div className="mx-auto grid max-w-7xl gap-12 px-6 lg:grid-cols-2 lg:items-center">
          <div>
            <p className="section-eyebrow">About the project</p>
            <h2 className="mt-3 text-3xl font-bold sm:text-4xl">
              Built as an end-to-end pest intelligence pipeline
            </h2>
            <p className="mt-5 text-slate-600 dark:text-slate-300">
              Raw crop and weather datasets are cleaned, feature-engineered
              (cyclic week encoding, humidity averages, a composite weather
              index) and used to train and tune an Extra Trees regressor,
              benchmarked against Random Forest, Gradient Boosting, XGBoost,
              LightGBM, and CatBoost. The winning model is served through a
              FastAPI backend with SHAP explanations attached to every
              prediction.
            </p>
            <div className="mt-8 space-y-3">
              {[
                "Multi-model comparison before locking the final estimator",
                "5-fold cross-validation for a stable R² estimate",
                "Randomized hyperparameter search on the Extra Trees model",
                "Feature importance surfaced straight from the trained model",
              ].map((item) => (
                <div key={item} className="flex items-start gap-3">
                  <CheckCircle2 size={18} className="mt-0.5 shrink-0 text-primary-600" />
                  <span className="text-sm text-slate-600 dark:text-slate-300">{item}</span>
                </div>
              ))}
            </div>
          </div>

          <motion.div
            initial={{ opacity: 0, scale: 0.96 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            className="glass-card p-6 font-mono text-xs leading-relaxed text-slate-500 dark:text-slate-400"
          >
            <p className="mb-2 text-slate-400 dark:text-slate-500"># model_comparison.csv</p>
            <p>Model &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;R2&nbsp;&nbsp;&nbsp; RMSE</p>
            <p className="text-primary-600">Extra Trees &nbsp; 0.91 &nbsp; 4.82</p>
            <p>XGBoost &nbsp;&nbsp;&nbsp;&nbsp; 0.89 &nbsp; 5.10</p>
            <p>LightGBM &nbsp;&nbsp;&nbsp; 0.88 &nbsp; 5.24</p>
            <p>CatBoost &nbsp;&nbsp;&nbsp; 0.88 &nbsp; 5.31</p>
            <p>Random Forest &nbsp;0.86 &nbsp; 5.67</p>
            <p>Gradient Boost &nbsp;0.85 &nbsp; 5.79</p>
            <p className="mt-3 text-slate-400 dark:text-slate-500">
              # Extra Trees selected — best R² / training-time trade-off
            </p>
          </motion.div>
        </div>
      </section>

      {/* ---------------- BENEFITS ---------------- */}
      <section className="mx-auto max-w-7xl px-6 py-24">
        <div className="grid gap-12 lg:grid-cols-2 lg:items-center">
          <div>
            <p className="section-eyebrow">Benefits</p>
            <h2 className="mt-3 text-3xl font-bold sm:text-4xl">
              Fewer surprises, less reactive spraying
            </h2>
            <p className="mt-5 text-slate-600 dark:text-slate-300">
              Every recommendation ties back to a concrete, explainable
              prediction — not a generic seasonal reminder.
            </p>
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            {BENEFITS.map((b, i) => (
              <motion.div
                key={b}
                initial="hidden"
                whileInView="show"
                viewport={{ once: true }}
                variants={fadeUp}
                custom={i}
                className="glass-card flex items-start gap-3 p-5"
              >
                <ShieldCheck size={18} className="mt-0.5 shrink-0 text-primary-600" />
                <p className="text-sm text-slate-600 dark:text-slate-300">{b}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ---------------- TECHNOLOGY ---------------- */}
      <section id="technology" className="bg-slate-900 py-24 text-white dark:bg-black/40">
        <div className="mx-auto max-w-7xl px-6">
          <div className="mx-auto max-w-2xl text-center">
            <p className="font-mono text-xs uppercase tracking-[0.2em] text-primary-400">
              Technology
            </p>
            <h2 className="mt-3 text-3xl font-bold sm:text-4xl">The stack under the hood</h2>
          </div>
          <div className="mt-14 grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
            {TECHNOLOGIES.map((t) => (
              <div
                key={t.label}
                className="rounded-2xl border border-white/10 bg-white/5 p-4 text-center backdrop-blur-sm"
              >
                <p className="font-display text-sm font-semibold">{t.label}</p>
                <p className="mt-1 text-xs text-slate-400">{t.role}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ---------------- SCREENSHOTS ---------------- */}
      <section id="screenshots" className="mx-auto max-w-7xl px-6 py-24">
        <div className="mx-auto max-w-2xl text-center">
          <p className="section-eyebrow">Screenshots</p>
          <h2 className="mt-3 text-3xl font-bold sm:text-4xl">Inside the workspace</h2>
        </div>
        <div className="mt-14 grid gap-6 sm:grid-cols-3">
          {["Dashboard overview", "Prediction &amp; risk meter", "Analytics"].map((label, i) => (
            <motion.div
              key={label}
              initial="hidden"
              whileInView="show"
              viewport={{ once: true }}
              variants={fadeUp}
              custom={i}
              className="glass-card aspect-video overflow-hidden"
            >
              <div className="flex h-full w-full items-center justify-center bg-gradient-to-br from-primary-50 to-accent-50 text-sm text-slate-400 dark:from-primary-500/5 dark:to-accent-500/5">
                {label.replace("&amp;", "&")} preview
              </div>
            </motion.div>
          ))}
        </div>
      </section>

      {/* ---------------- FAQ ---------------- */}
      <section id="faq" className="bg-white py-24 dark:bg-surface-darkMuted/40">
        <div className="mx-auto max-w-3xl px-6">
          <div className="text-center">
            <p className="section-eyebrow">FAQ</p>
            <h2 className="mt-3 text-3xl font-bold sm:text-4xl">Common questions</h2>
          </div>
          <div className="mt-12 space-y-4">
            {FAQS.map((f) => (
              <details
                key={f.q}
                className="glass-card group p-5 [&_summary::-webkit-details-marker]:hidden"
              >
                <summary className="flex cursor-pointer list-none items-center justify-between font-medium">
                  {f.q}
                  <span className="ml-4 text-primary-600 transition-transform group-open:rotate-45">
                    +
                  </span>
                </summary>
                <p className="mt-3 text-sm text-slate-600 dark:text-slate-300">{f.a}</p>
              </details>
            ))}
          </div>
        </div>
      </section>

      {/* ---------------- CONTACT ---------------- */}
      <section id="contact" className="mx-auto max-w-4xl px-6 py-24">
        <div className="glass-card overflow-hidden p-10 text-center sm:p-14">
          <p className="section-eyebrow justify-center">Contact</p>
          <h2 className="mt-3 text-3xl font-bold sm:text-4xl">
            Questions about the model or the data?
          </h2>
          <p className="mx-auto mt-4 max-w-xl text-slate-600 dark:text-slate-300">
            Reach out and we'll walk through the feature pipeline, the model
            comparison report, or how to plug in your own field data.
          </p>
          <div className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row">
            <a href="mailto:contact@agrishield.ai" className="btn-primary px-6 py-3">
              <Mail size={18} /> Email us
            </a>
            <a href="#" className="btn-secondary px-6 py-3">
              <Github size={18} /> View on GitHub
            </a>
          </div>
        </div>
      </section>
    </div>
  );
}
