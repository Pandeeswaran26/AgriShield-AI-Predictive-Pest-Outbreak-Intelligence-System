import { Leaf, Github, Mail, Twitter } from "lucide-react";

const COLUMNS = [
  {
    title: "Product",
    links: ["Features", "Technology", "Screenshots", "FAQ"],
  },
  {
    title: "Company",
    links: ["About the project", "Contact", "Documentation"],
  },
  {
    title: "Resources",
    links: ["API reference", "Model card", "Changelog"],
  },
];

export default function Footer() {
  return (
    <footer className="border-t border-surface-border bg-white dark:border-surface-darkBorder dark:bg-surface-dark">
      <div className="mx-auto max-w-7xl px-6 py-14">
        <div className="grid grid-cols-2 gap-10 md:grid-cols-5">
          <div className="col-span-2">
            <div className="flex items-center gap-2 font-display text-lg font-bold">
              <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary-600 text-white">
                <Leaf size={18} />
              </span>
              AgriShield AI
            </div>
            <p className="mt-3 max-w-xs text-sm text-slate-500 dark:text-slate-400">
              Predictive pest outbreak intelligence for fields, built on an
              Extra Trees model with SHAP-backed explanations.
            </p>
            <div className="mt-4 flex gap-3 text-slate-400">
              <a href="#" aria-label="GitHub" className="hover:text-primary-600">
                <Github size={18} />
              </a>
              <a href="#" aria-label="Twitter" className="hover:text-primary-600">
                <Twitter size={18} />
              </a>
              <a href="#contact" aria-label="Email" className="hover:text-primary-600">
                <Mail size={18} />
              </a>
            </div>
          </div>

          {COLUMNS.map((col) => (
            <div key={col.title}>
              <h4 className="font-display text-sm font-semibold">{col.title}</h4>
              <ul className="mt-3 space-y-2">
                {col.links.map((link) => (
                  <li key={link}>
                    <a
                      href="#"
                      className="text-sm text-slate-500 transition-colors hover:text-primary-600 dark:text-slate-400"
                    >
                      {link}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="mt-12 flex flex-col items-center justify-between gap-4 border-t border-surface-border pt-6 text-xs text-slate-400 dark:border-surface-darkBorder md:flex-row">
          <p>© {new Date().getFullYear()} AgriShield AI. Final-year academic project.</p>
          <p>Built with React, FastAPI &amp; Scikit-Learn.</p>
        </div>
      </div>
    </footer>
  );
}
