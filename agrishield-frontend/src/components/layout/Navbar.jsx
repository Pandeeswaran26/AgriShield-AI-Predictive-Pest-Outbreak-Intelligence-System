import { useEffect, useState } from "react";
import { Link, NavLink } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { Leaf, Moon, Sun, Menu, X } from "lucide-react";
import { useTheme } from "../../context/ThemeContext";

const NAV_LINKS = [
  { label: "Features", href: "#features" },
  { label: "How it works", href: "#about" },
  { label: "Technology", href: "#technology" },
  { label: "FAQ", href: "#faq" },
];

export default function Navbar() {
  const { theme, toggleTheme } = useTheme();
  const [scrolled, setScrolled] = useState(false);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8);
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <header
      className={`sticky top-0 z-50 transition-all ${
        scrolled
          ? "glass-card !rounded-none border-x-0 border-t-0"
          : "bg-transparent"
      }`}
    >
      <nav className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
        <Link to="/" className="flex items-center gap-2 font-display text-lg font-bold">
          <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary-600 text-white">
            <Leaf size={18} />
          </span>
          AgriShield <span className="text-primary-600">AI</span>
        </Link>

        <div className="hidden items-center gap-8 md:flex">
          {NAV_LINKS.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className="text-sm font-medium text-slate-600 transition-colors hover:text-primary-700 dark:text-slate-300 dark:hover:text-primary-400"
            >
              {link.label}
            </a>
          ))}
        </div>

        <div className="hidden items-center gap-3 md:flex">
          <button
            onClick={toggleTheme}
            aria-label="Toggle dark mode"
            className="rounded-lg p-2 text-slate-500 transition-colors hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-white/5"
          >
            {theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}
          </button>
          <NavLink to="/login" className="btn-secondary">
            Log in
          </NavLink>
          <NavLink to="/register" className="btn-primary">
            Get started
          </NavLink>
        </div>

        <button
          className="p-2 md:hidden"
          onClick={() => setOpen((v) => !v)}
          aria-label="Toggle menu"
        >
          {open ? <X size={22} /> : <Menu size={22} />}
        </button>
      </nav>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden border-t border-surface-border dark:border-surface-darkBorder md:hidden"
          >
            <div className="flex flex-col gap-4 px-6 py-4">
              {NAV_LINKS.map((link) => (
                <a key={link.href} href={link.href} className="text-sm font-medium">
                  {link.label}
                </a>
              ))}
              <div className="flex gap-3 pt-2">
                <NavLink to="/login" className="btn-secondary flex-1">
                  Log in
                </NavLink>
                <NavLink to="/register" className="btn-primary flex-1">
                  Get started
                </NavLink>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
}
