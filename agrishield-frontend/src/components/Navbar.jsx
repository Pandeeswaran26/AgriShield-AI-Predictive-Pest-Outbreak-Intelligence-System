import { Link, useNavigate } from "react-router-dom";
import { Leaf, Menu, X } from "lucide-react";
import { useState } from "react";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const { isAuthenticated } = useAuth();
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();

  return (
    <header className="sticky top-0 z-40 border-b border-mist/10 bg-field-950/85 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <Link to="/" className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-canopy/15 text-canopy">
            <Leaf size={18} />
          </div>
          <span className="font-display text-lg font-semibold text-mist">AgriShield AI</span>
        </Link>

        <nav className="hidden items-center gap-8 text-sm font-medium text-mist/70 md:flex">
          <a href="/#how-it-works" className="hover:text-mist">How it works</a>
          <a href="/#coverage" className="hover:text-mist">Coverage</a>
        </nav>

        <div className="hidden items-center gap-3 md:flex">
          {isAuthenticated ? (
            <button onClick={() => navigate("/app/dashboard")} className="btn-primary">
              Go to dashboard
            </button>
          ) : (
            <>
              <Link to="/login" className="btn-ghost !border-mist/15 !text-mist hover:!text-canopy">
                Log in
              </Link>
              <Link to="/register" className="btn-primary">
                Get started
              </Link>
            </>
          )}
        </div>

        <button className="text-mist md:hidden" onClick={() => setOpen((v) => !v)} aria-label="Toggle menu">
          {open ? <X size={22} /> : <Menu size={22} />}
        </button>
      </div>

      {open && (
        <div className="border-t border-mist/10 px-6 py-4 md:hidden">
          <div className="flex flex-col gap-3">
            {isAuthenticated ? (
              <Link to="/app/dashboard" className="btn-primary w-full">Go to dashboard</Link>
            ) : (
              <>
                <Link to="/login" className="btn-ghost w-full !border-mist/15 !text-mist">Log in</Link>
                <Link to="/register" className="btn-primary w-full">Get started</Link>
              </>
            )}
          </div>
        </div>
      )}
    </header>
  );
}
