"use client";

import {
  Bell,
  LogOut,
  Menu,
  Search,
  ShieldCheck,
  X,
} from "lucide-react";
import { usePathname, useRouter } from "next/navigation";
import { useState } from "react";

import { useAuth } from "@/hooks/use-auth";

const pageLabels: Record<string, string> = {
  "/": "Command Center",
  "/agents": "Agents",
  "/policies": "Policies",
  "/tools": "Tools & Actions",
  "/guardrails": "Runtime Guardrails",
  "/posture": "Agent Posture",
  "/security-tests": "Security Testing",
  "/events": "Security Events",
  "/alerts": "Alerts & Incidents",
  "/analytics": "Analytics",
  "/compliance": "Compliance",
  "/detection-rules": "Detection Rules",
  "/incidents": "Incident Response",
  "/audit": "Audit Log",

};

const navigationItems = [
  { label: "Command Center", href: "/" },
  { label: "Agents", href: "/agents" },
  { label: "Policies", href: "/policies" },
  { label: "Tools & Actions", href: "/tools" },
  { label: "Runtime Guardrails", href: "/guardrails" },
  { label: "Agent Posture", href: "/posture" },
  { label: "Security Testing", href: "/security-tests" },
  { label: "Security Events", href: "/events" },
  { label: "Alerts & Incidents", href: "/alerts" },
  { label: "Analytics", href: "/analytics" },
  { label: "Compliance", href: "/compliance" },

  { label: "Detection Rules", href: "/detection-rules" },
  { label: "Incident Response", href: "/incidents" },
  { label: "Audit Log", href: "/audit" },

];

export function Topbar() {
  const router = useRouter();
  const pathname = usePathname();
  const { logout, user } = useAuth();

  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const currentPage = pageLabels[pathname] ?? "Security Operations";

  const displayName = user?.username ?? "Operator";
  const displayRole =
    user?.role === "ADMIN" ? "Administrator" : "Operator";
  const initials = displayName.slice(0, 2).toUpperCase();

  const handleLogout = () => {
    logout();
    router.replace("/login");
  };

  const handleMobileNavigation = (href: string) => {
    setMobileMenuOpen(false);
    router.push(href);
  };

  return (
    <>
      <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-slate-200 bg-white px-4 backdrop-blur-xl sm:px-6 lg:px-8">
        <div className="flex min-w-0 items-center gap-3">
          <button
            type="button"
            onClick={() => setMobileMenuOpen((open) => !open)}
            className="flex size-9 shrink-0 items-center justify-center rounded-lg border border-slate-200 bg-slate-50 text-slate-600 transition-all duration-200 hover:border-indigo-400/20 hover:bg-indigo-400/[0.05] hover:text-indigo-600 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-400/40 lg:hidden"
            aria-label={
              mobileMenuOpen ? "Close navigation" : "Open navigation"
            }
            aria-expanded={mobileMenuOpen}
            aria-controls="mobile-navigation"
          >
            {mobileMenuOpen ? (
              <X className="size-4" />
            ) : (
              <Menu className="size-4" />
            )}
          </button>

          <div className="flex min-w-0 items-center gap-2 text-xs">
            <ShieldCheck className="size-4 shrink-0 text-indigo-600" />

            <span className="hidden text-slate-500 sm:inline">
              Security Operations
            </span>

            <span className="hidden text-slate-400 sm:inline">/</span>

            <span className="truncate font-medium text-slate-700">
              {currentPage}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2 sm:gap-3">
          <button
            type="button"
            className="flex size-9 items-center justify-center rounded-lg border border-slate-200 bg-slate-50 text-slate-500 transition-all duration-200 hover:border-indigo-400/20 hover:bg-indigo-400/[0.05] hover:text-indigo-600 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-400/40"
            aria-label="Search"
          >
            <Search className="size-4" />
          </button>

          <button
            type="button"
            className="relative flex size-9 items-center justify-center rounded-lg border border-slate-200 bg-slate-50 text-slate-500 transition-all duration-200 hover:border-amber-400/20 hover:bg-amber-400/[0.05] hover:text-amber-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-400/40"
            aria-label="Notifications"
          >
            <Bell className="size-4" />

            <span className="absolute right-2 top-2 size-1.5 rounded-full bg-red-400 shadow-[0_0_7px_rgba(248,113,113,0.7)]" />
          </button>

          <div className="hidden h-7 w-px bg-white/[0.08] sm:block" />

          <div className="hidden items-center gap-2 sm:flex">
            <div className="flex size-8 items-center justify-center rounded-full border border-indigo-400/20 bg-indigo-400/[0.07] text-[10px] font-semibold tracking-wide text-indigo-600">
              {initials}
            </div>

            <div className="hidden text-left md:block">
              <div className="text-xs font-medium text-slate-800">
                {displayName}
              </div>

              <div className="mt-0.5 text-[10px] text-slate-500">
                {displayRole}
              </div>
            </div>
          </div>

          <button
            type="button"
            onClick={handleLogout}
            className="group flex size-9 items-center justify-center rounded-lg border border-slate-200 bg-slate-50 text-slate-500 transition-all duration-200 hover:border-red-400/20 hover:bg-red-400/[0.05] hover:text-red-600 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-red-400/40"
            aria-label="Sign out"
            title="Sign out"
          >
            <LogOut className="size-4 transition-transform duration-200 group-hover:-translate-x-0.5" />
          </button>
        </div>
      </header>

      {mobileMenuOpen && (
        <div
          id="mobile-navigation"
          className="fixed inset-x-0 top-16 z-20 border-b border-slate-200 bg-white px-4 py-3 shadow-2xl shadow-slate-900/10 backdrop-blur-xl lg:hidden"
        >
          <div className="mb-3 flex items-center gap-2 px-1">
            <div className="size-1.5 rounded-full bg-indigo-300 shadow-[0_0_8px_rgba(79, 70, 229,0.8)]" />

            <span className="text-[9px] font-semibold uppercase tracking-[0.2em] text-slate-500">
              Navigation
            </span>
          </div>

          <nav className="grid gap-1 sm:grid-cols-2">
            {navigationItems.map((item) => {
              const active =
                item.href === "/"
                  ? pathname === "/"
                  : pathname === item.href ||
                    pathname.startsWith(`${item.href}/`);

              return (
                <button
                  key={item.href}
                  type="button"
                  onClick={() => handleMobileNavigation(item.href)}
                  className={`flex items-center justify-between rounded-lg border px-3 py-2.5 text-left text-xs font-medium transition-all duration-200 ${
                    active
                      ? "border-indigo-400/15 bg-indigo-400/[0.075] text-indigo-600"
                      : "border-transparent text-slate-500 hover:border-slate-200 hover:bg-slate-50 hover:text-slate-800"
                  }`}
                  aria-current={active ? "page" : undefined}
                >
                  <span>{item.label}</span>

                  {active && (
                    <span className="size-1.5 rounded-full bg-indigo-300 shadow-[0_0_8px_rgba(79, 70, 229,0.8)]" />
                  )}
                </button>
              );
            })}
          </nav>
        </div>
      )}
    </>
  );
}
