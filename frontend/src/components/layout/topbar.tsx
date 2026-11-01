"use client";

import {
  Bell,
  ChevronDown,
  LogOut,
  Menu,
  Search,
  Settings,
  ShieldCheck,
  TriangleAlert,
  X,
} from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useState } from "react";
import { AnimatePresence, motion } from "motion/react";

import { useSecurityAlerts } from "@/features/alerts/use-security-alerts";
import { ConfirmDialog } from "@/components/ui/confirm-dialog";

const severityDot: Record<string, string> = {
  CRITICAL: "bg-red-500",
  HIGH: "bg-red-400",
  MEDIUM: "bg-amber-400",
  LOW: "bg-slate-300",
};

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
  "/settings": "Account & Security",

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
  const [openMenu, setOpenMenu] = useState<null | "notifications" | "profile">(
    null,
  );
  const [confirmLogout, setConfirmLogout] = useState(false);

  const { data: alertData } = useSecurityAlerts(1, 6);
  const alerts = alertData?.items ?? [];
  const openAlerts = alerts.filter(
    (a) => a.status === "OPEN" || a.status === "ACKNOWLEDGED",
  ).length;

  const currentPage = pageLabels[pathname] ?? "Security Operations";

  const displayName = user?.username ?? "Operator";
  const displayRole =
    user?.role === "ADMIN" ? "Administrator" : "Operator";
  const initials = displayName.slice(0, 2).toUpperCase();

  const handleLogout = () => {
    logout();
    router.replace("/login");
  };

  const toggle = (menu: "notifications" | "profile") =>
    setOpenMenu((cur) => (cur === menu ? null : menu));

  const handleMobileNavigation = (href: string) => {
    setMobileMenuOpen(false);
    router.push(href);
  };

  return (
    <>
      <header className="sticky top-0 z-40 flex h-16 items-center justify-between border-b border-slate-200 bg-white px-4 backdrop-blur-xl sm:px-6 lg:px-8">
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
            onClick={() =>
              window.dispatchEvent(new Event("sentinelx:open-command"))
            }
            className="flex h-9 items-center gap-2 rounded-lg border border-slate-200 bg-slate-50 px-2.5 text-slate-500 transition-all duration-200 hover:border-indigo-400/30 hover:bg-indigo-50 hover:text-indigo-600 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-400/40"
            aria-label="Search"
          >
            <Search className="size-4" />
            <kbd className="hidden rounded border border-slate-200 bg-white px-1.5 py-0.5 text-[10px] font-medium text-slate-400 lg:block">
              ⌘K
            </kbd>
          </button>

          {/* Notifications */}
          <div className="relative">
            <button
              type="button"
              onClick={() => toggle("notifications")}
              className="relative flex size-9 items-center justify-center rounded-lg border border-slate-200 bg-slate-50 text-slate-500 transition-all duration-200 hover:border-indigo-400/30 hover:bg-indigo-50 hover:text-indigo-600 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-400/40"
              aria-label="Notifications"
              aria-expanded={openMenu === "notifications"}
            >
              <Bell className="size-4" />
              {openAlerts > 0 && (
                <span className="absolute -right-0.5 -top-0.5 flex min-w-4 items-center justify-center rounded-full bg-red-500 px-1 text-[9px] font-bold text-white">
                  {openAlerts}
                </span>
              )}
            </button>

            <AnimatePresence>
              {openMenu === "notifications" && (
                <motion.div
                  initial={{ opacity: 0, y: -8, scale: 0.98 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: -8, scale: 0.98 }}
                  transition={{ duration: 0.15 }}
                  className="absolute right-0 top-11 z-50 w-80 overflow-hidden rounded-xl border border-slate-200 bg-white shadow-xl shadow-slate-900/10"
                >
                  <div className="flex items-center justify-between border-b border-slate-100 px-4 py-3">
                    <span className="text-xs font-semibold text-slate-800">
                      Notifications
                    </span>
                    <span className="text-[10px] font-medium text-slate-500">
                      {openAlerts} open
                    </span>
                  </div>
                  <div className="max-h-80 overflow-y-auto">
                    {alerts.length === 0 ? (
                      <div className="px-4 py-8 text-center text-xs text-slate-400">
                        No recent alerts.
                      </div>
                    ) : (
                      alerts.map((a) => (
                        <div
                          key={a.id}
                          className="flex items-start gap-3 border-b border-slate-50 px-4 py-3 last:border-0 hover:bg-slate-50"
                        >
                          <span
                            className={`mt-1 size-2 shrink-0 rounded-full ${severityDot[a.severity] ?? "bg-slate-300"}`}
                          />
                          <div className="min-w-0">
                            <div className="truncate text-xs font-medium text-slate-800">
                              {a.title}
                            </div>
                            <div className="mt-0.5 text-[10px] text-slate-500">
                              {a.severity} · {a.status}
                            </div>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                  <Link
                    href="/alerts"
                    onClick={() => setOpenMenu(null)}
                    className="flex items-center justify-center gap-1.5 border-t border-slate-100 py-2.5 text-xs font-medium text-indigo-600 hover:bg-indigo-50"
                  >
                    <TriangleAlert className="size-3.5" />
                    View all alerts
                  </Link>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          <div className="hidden h-7 w-px bg-slate-200 sm:block" />

          {/* Profile */}
          <div className="relative">
            <button
              type="button"
              onClick={() => toggle("profile")}
              className="flex items-center gap-2 rounded-lg border border-transparent px-1.5 py-1 transition-colors hover:bg-slate-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-400/40"
              aria-label="Account menu"
              aria-expanded={openMenu === "profile"}
            >
              <div className="flex size-8 items-center justify-center rounded-full border border-indigo-200 bg-indigo-50 text-[10px] font-semibold tracking-wide text-indigo-600">
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
              <ChevronDown className="hidden size-3.5 text-slate-400 md:block" />
            </button>

            <AnimatePresence>
              {openMenu === "profile" && (
                <motion.div
                  initial={{ opacity: 0, y: -8, scale: 0.98 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: -8, scale: 0.98 }}
                  transition={{ duration: 0.15 }}
                  className="absolute right-0 top-12 z-50 w-56 overflow-hidden rounded-xl border border-slate-200 bg-white shadow-xl shadow-slate-900/10"
                >
                  <div className="border-b border-slate-100 px-4 py-3">
                    <div className="text-sm font-semibold text-slate-900">
                      {displayName}
                    </div>
                    <div className="text-[11px] text-slate-500">
                      {displayRole}
                    </div>
                  </div>
                  <Link
                    href="/settings"
                    onClick={() => setOpenMenu(null)}
                    className="flex items-center gap-2.5 px-4 py-2.5 text-sm text-slate-700 hover:bg-slate-50"
                  >
                    <Settings className="size-4 text-slate-400" />
                    Account &amp; Security
                  </Link>
                  <button
                    type="button"
                    onClick={() => {
                      setOpenMenu(null);
                      setConfirmLogout(true);
                    }}
                    className="flex w-full items-center gap-2.5 border-t border-slate-100 px-4 py-2.5 text-left text-sm text-red-600 hover:bg-red-50"
                  >
                    <LogOut className="size-4" />
                    Sign out
                  </button>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </header>

      {/* Click-away backdrop for dropdowns */}
      {openMenu && (
        <div
          className="fixed inset-0 z-30"
          aria-hidden
          onClick={() => setOpenMenu(null)}
        />
      )}

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

      <ConfirmDialog
        open={confirmLogout}
        variant="danger"
        title="Sign out of SentinelX?"
        description="You'll need to authenticate again to access the control plane."
        confirmLabel="Sign out"
        cancelLabel="Stay signed in"
        onConfirm={() => {
          setConfirmLogout(false);
          handleLogout();
        }}
        onCancel={() => setConfirmLogout(false)}
      />
    </>
  );
}
