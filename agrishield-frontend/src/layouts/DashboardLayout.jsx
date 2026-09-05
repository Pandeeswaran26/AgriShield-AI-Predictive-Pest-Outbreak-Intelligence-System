import { useState } from "react";
import { Outlet, Link } from "react-router-dom";
import { Menu, Leaf } from "lucide-react";
import Sidebar from "../components/Sidebar";

export default function DashboardLayout() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <div className="flex min-h-screen bg-mist dark:bg-field-900">
      {/* Desktop Sidebar */}
      <Sidebar />

      {/* Mobile Drawer Overlay */}
      {mobileMenuOpen && (
        <div className="fixed inset-0 z-50 flex md:hidden">
          <div
            className="fixed inset-0 bg-black/60 backdrop-blur-sm transition-opacity"
            onClick={() => setMobileMenuOpen(false)}
          />
          <div className="relative z-50 w-72 max-w-[80vw] bg-white shadow-2xl dark:bg-field-950">
            <Sidebar onClose={() => setMobileMenuOpen(false)} isMobile={true} />
          </div>
        </div>
      )}

      {/* Main Content Area */}
      <div className="flex flex-1 flex-col overflow-x-hidden">
        {/* Mobile Header Bar */}
        <header className="flex items-center justify-between border-b border-field-900/10 bg-white px-5 py-3.5 dark:border-mist/10 dark:bg-field-950 md:hidden">
          <Link to="/app/dashboard" className="flex items-center gap-2">
            <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-canopy/15 text-canopy">
              <Leaf size={16} />
            </div>
            <span className="font-display text-base font-semibold">AgriShield</span>
          </Link>
          <button
            onClick={() => setMobileMenuOpen(true)}
            className="rounded-lg p-2 text-field-900/70 hover:bg-field-900/5 dark:text-mist/70 dark:hover:bg-mist/5"
            aria-label="Open menu"
          >
            <Menu size={20} />
          </button>
        </header>

        <main className="flex-1 px-5 py-6 md:px-10 md:py-8">
          <div className="mx-auto max-w-6xl">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}
