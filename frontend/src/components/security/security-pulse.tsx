"use client";

import {
  Activity,
  AlertTriangle,
  BarChart3,
  ChevronRight,
  FlaskConical,
  ShieldCheck,
  Zap,
} from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

import { useSecurityAlerts } from "@/features/alerts/use-security-alerts";
import { useSecurityEvents } from "@/features/events/use-security-events";

const modules = [
  {
    href: "/events",
    label: "Events",
    icon: Activity,
    tone: "cyan",
  },
  {
    href: "/alerts",
    label: "Alerts",
    icon: AlertTriangle,
    tone: "red",
  },
  {
    href: "/guardrails",
    label: "Guardrails",
    icon: ShieldCheck,
    tone: "emerald",
  },
  {
    href: "/analytics",
    label: "Analytics",
    icon: BarChart3,
    tone: "cyan",
  },
  {
    href: "/security-tests",
    label: "Simulation",
    icon: FlaskConical,
    tone: "violet",
  },
] as const;

const toneClasses = {
  cyan: {
    dot: "bg-cyan-400",
    text: "text-cyan-300",
    border: "border-cyan-400/20",
    background: "bg-cyan-400/[0.06]",
  },
  red: {
    dot: "bg-red-400",
    text: "text-red-300",
    border: "border-red-400/20",
    background: "bg-red-400/[0.06]",
  },
  emerald: {
    dot: "bg-emerald-400",
    text: "text-emerald-300",
    border: "border-emerald-400/20",
    background: "bg-emerald-400/[0.06]",
  },
  violet: {
    dot: "bg-violet-400",
    text: "text-violet-300",
    border: "border-violet-400/20",
    background: "bg-violet-400/[0.06]",
  },
} as const;

export function SecurityPulse() {
  const pathname = usePathname();

  const { data: eventsData, isLoading: eventsLoading } =
    useSecurityEvents(1, 6);

  const { data: alertsData, isLoading: alertsLoading } =
    useSecurityAlerts(1, 10);

  const events = eventsData?.items ?? [];
  const alerts = alertsData?.items ?? [];

  const blockedEvents = events.filter((event) =>
    event.decision.toUpperCase().includes("BLOCK"),
  ).length;

  const openAlerts = alerts.filter((alert) => {
    const status = alert.status.toUpperCase();

    return status === "OPEN" || status === "INVESTIGATING";
  }).length;

  const telemetryLoading = eventsLoading || alertsLoading;

  return (
    <section
      aria-label="Security pulse"
      className="mb-6 overflow-hidden rounded-2xl border border-slate-800/80 bg-[#080c12]/90"
    >
      <div className="flex flex-col lg:flex-row lg:items-stretch">
        <div className="flex min-w-0 items-center gap-3 border-b border-slate-800/80 px-4 py-3 lg:w-[250px] lg:border-b-0 lg:border-r">
          <div className="relative flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-cyan-400/20 bg-cyan-400/[0.06]">
            <Zap className="h-4 w-4 text-cyan-300" />
            <span className="absolute -right-0.5 -top-0.5 h-2 w-2 animate-pulse rounded-full bg-cyan-400" />
          </div>

          <div className="min-w-0">
            <p className="text-[9px] font-bold uppercase tracking-[0.2em] text-cyan-300/80">
              Security Pulse
            </p>

            <p className="mt-0.5 truncate text-xs text-slate-500">
              Cross-module telemetry
            </p>
          </div>

          <div className="ml-auto hidden items-center gap-2 text-[9px] font-semibold uppercase tracking-[0.14em] text-emerald-400 sm:flex lg:hidden">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
            Linked
          </div>
        </div>

        <div className="flex min-w-0 flex-1 flex-wrap items-center">
          {modules.map((module) => {
            const Icon = module.icon;
            const tone = toneClasses[module.tone];
            const active = pathname === module.href;

            let count: number | null = null;

            if (module.href === "/events") {
              count = eventsData?.total ?? 0;
            }

            if (module.href === "/alerts") {
              count = alertsData?.total ?? 0;
            }

            return (
              <Link
                key={module.href}
                href={module.href}
                className={`group flex min-w-[108px] flex-1 items-center gap-2 border-r border-slate-800/70 px-3 py-3 transition-colors last:border-r-0 hover:bg-white/[0.025] ${
                  active ? tone.background : ""
                }`}
                aria-current={active ? "page" : undefined}
              >
                <span
                  className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-md border ${
                    active
                      ? `${tone.border} ${tone.background}`
                      : "border-slate-800 bg-slate-950/50"
                  }`}
                >
                  <Icon
                    className={`h-3.5 w-3.5 ${
                      active ? tone.text : "text-slate-500"
                    }`}
                  />
                </span>

                <span className="min-w-0">
                  <span
                    className={`block text-[10px] font-semibold uppercase tracking-[0.12em] ${
                      active ? tone.text : "text-slate-400"
                    }`}
                  >
                    {module.label}
                  </span>

                  <span className="mt-0.5 block text-[9px] text-slate-600">
                    {module.href === "/security-tests"
                      ? "Controlled"
                      : module.href === "/guardrails"
                        ? "Enforced"
                        : module.href === "/analytics"
                          ? "Measured"
                          : module.href === "/alerts"
                            ? openAlerts > 0
                              ? `${openAlerts} open`
                              : "Clear"
                            : `${count ?? 0} recorded`}
                  </span>
                </span>

                {module.href === "/events" && blockedEvents > 0 && (
                  <span className="ml-auto hidden rounded-full border border-red-400/20 bg-red-400/10 px-1.5 py-0.5 text-[8px] font-bold text-red-300 xl:block">
                    {blockedEvents}
                  </span>
                )}

                {module.href === "/alerts" && openAlerts > 0 && (
                  <span className="ml-auto h-1.5 w-1.5 animate-pulse rounded-full bg-red-400" />
                )}

                {active && (
                  <ChevronRight
                    className={`ml-auto hidden h-3 w-3 ${tone.text} sm:block`}
                  />
                )}
              </Link>
            );
          })}
        </div>

        <div className="flex items-center justify-between border-t border-slate-800/80 px-4 py-2.5 lg:w-[155px] lg:border-l lg:border-t-0">
          <span className="text-[9px] font-semibold uppercase tracking-[0.16em] text-slate-600">
            Control link
          </span>

          <span className="flex items-center gap-2 text-[9px] font-semibold uppercase tracking-[0.14em] text-emerald-400">
            <span
              className={`h-1.5 w-1.5 rounded-full ${
                telemetryLoading
                  ? "animate-pulse bg-amber-400"
                  : "bg-emerald-400"
              }`}
            />

            {telemetryLoading ? "Syncing" : "Linked"}
          </span>
        </div>
      </div>
    </section>
  );
}