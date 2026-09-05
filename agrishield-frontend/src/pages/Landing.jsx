import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { ScanLine, Sprout, CloudRain, ShieldCheck, ArrowRight, Activity } from "lucide-react";

const STEPS = [
  {
    icon: CloudRain,
    title: "Feed in field conditions",
    text: "Crop, pest pressure, location, and the week's temperature, humidity, rainfall and wind readings.",
  },
  {
    icon: Activity,
    title: "Extra Trees model scores it",
    text: "A model trained on multi-season cotton and rice pest records returns a pest-pressure value in real time.",
  },
  {
    icon: ShieldCheck,
    title: "Act before the outbreak",
    text: "Get a risk level, SHAP-backed explanation, and pest-specific treatment and prevention steps.",
  },
];

const COVERAGE = [
  { crop: "Cotton", pests: "Aphids, whiteflies, bollworms, jassids" },
  { crop: "Rice", pests: "Stem borers, brown planthoppers, leaf folders" },
];

export default function Landing() {
  return (
    <div>
      {/* Hero */}
      <section className="relative overflow-hidden field-lines border-b border-mist/10">
        <div className="mx-auto grid max-w-6xl items-center gap-12 px-6 py-20 md:grid-cols-2 md:py-28">
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <span className="inline-flex items-center gap-2 rounded-full border border-canopy/30 bg-canopy/10 px-3 py-1 text-xs font-mono uppercase tracking-widest text-canopy">
              <ScanLine size={13} /> Predictive Pest Intelligence
            </span>
            <h1 className="mt-6 font-display text-4xl font-semibold leading-[1.1] md:text-5xl">
              Know the outbreak
              <br />
              before it reaches the field.
            </h1>
            <p className="mt-5 max-w-md text-mist/65">
              AgriShield AI turns this week's weather and pest signals into a pest-pressure
              score, a risk level, and a treatment plan — for cotton and rice growers.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link to="/register" className="btn-primary">
                Get started <ArrowRight size={16} />
              </Link>
              <Link to="/login" className="btn-ghost !border-mist/15 !text-mist hover:!text-canopy">
                Log in
              </Link>
            </div>
          </motion.div>

          {/* Signature element: a live-scanning readout card */}
          <motion.div
            initial={{ opacity: 0, scale: 0.96 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6, delay: 0.15 }}
            className="relative mx-auto w-full max-w-sm"
          >
            <div className="relative overflow-hidden rounded-2xl border border-mist/15 bg-field-900 p-6 shadow-2xl shadow-black/40">
              <div className="pointer-events-none absolute inset-x-0 top-0 h-24 bg-gradient-to-b from-canopy/25 to-transparent animate-scan" />
              <p className="font-mono text-[11px] uppercase tracking-widest text-canopy/80">
                Field scan — Coimbatore
              </p>
              <div className="mt-4 flex items-baseline gap-2">
                <span className="font-display text-5xl font-semibold text-canopy">62.4</span>
                <span className="text-sm text-mist/50">pest value</span>
              </div>
              <div className="mt-2 inline-flex items-center gap-1.5 rounded-full border border-clay/30 bg-clay/10 px-2.5 py-1 text-xs font-semibold text-clay">
                <span className="h-1.5 w-1.5 rounded-full bg-current" /> Medium risk
              </div>
              <div className="mt-6 space-y-2.5 border-t border-mist/10 pt-4 font-mono text-xs text-mist/55">
                <div className="flex justify-between"><span>Crop</span><span className="text-mist/85">Cotton</span></div>
                <div className="flex justify-between"><span>Pest</span><span className="text-mist/85">Bollworm</span></div>
                <div className="flex justify-between"><span>Humidity</span><span className="text-mist/85">78%</span></div>
                <div className="flex justify-between"><span>Rainfall</span><span className="text-mist/85">34mm</span></div>
              </div>
            </div>
            <Sprout className="absolute -bottom-5 -right-5 text-canopy/20" size={72} strokeWidth={1} />
          </motion.div>
        </div>
      </section>

      {/* How it works */}
      <section id="how-it-works" className="mx-auto max-w-6xl px-6 py-20">
        <h2 className="font-display text-2xl font-semibold md:text-3xl">How it works</h2>
        <p className="mt-2 max-w-lg text-mist/60">Three steps from field data to field action.</p>

        <div className="mt-10 grid gap-5 md:grid-cols-3">
          {STEPS.map(({ icon: Icon, title, text }, i) => (
            <motion.div
              key={title}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: i * 0.1 }}
              className="rounded-2xl border border-mist/10 bg-field-900 p-6"
            >
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-canopy/12 text-canopy">
                <Icon size={19} />
              </div>
              <h3 className="mt-4 font-display text-lg font-semibold">{title}</h3>
              <p className="mt-2 text-sm text-mist/60">{text}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Coverage */}
      <section id="coverage" className="border-t border-mist/10 bg-field-900/60">
        <div className="mx-auto max-w-6xl px-6 py-20">
          <h2 className="font-display text-2xl font-semibold md:text-3xl">Built for two crops, deeply</h2>
          <p className="mt-2 max-w-lg text-mist/60">
            Trained on multi-season observation records rather than generic pest databases.
          </p>
          <div className="mt-10 grid gap-5 md:grid-cols-2">
            {COVERAGE.map(({ crop, pests }) => (
              <div key={crop} className="rounded-2xl border border-mist/10 p-6">
                <p className="font-mono text-xs uppercase tracking-widest text-canopy">{crop}</p>
                <p className="mt-2 text-lg text-mist/85">{pests}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <footer className="border-t border-mist/10 px-6 py-8 text-center text-xs text-mist/40">
        AgriShield AI — Predictive Pest Outbreak Intelligence System
      </footer>
    </div>
  );
}
