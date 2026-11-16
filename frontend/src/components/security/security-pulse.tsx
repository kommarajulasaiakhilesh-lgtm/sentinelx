"use client";

import {
  Activity,
  AlertTriangle,
  BarChart3,
  FlaskConical,
  ShieldCheck,
} from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

import { useSecurityAlerts } from "@/features/alerts/use-security-alerts";
import { useSecurityEvents } from "@/features/events/use-security-events";

export function SecurityPulse() {
  const pathname = usePathname();

  const { data: eventsData, isLoading: eventsLoading } = useSecurityEvents(1, 6);
  const { data: alertsData, isLoading: alertsLoading } = useSecurityAlerts(1, 10);

  const alerts = alertsData?.items ?? [];
  const openAlerts = alerts.filter((a) => {
    const s = a.status.toUpperCase();
    return s === "OPEN" || s === "INVESTIGATING";
  }).length;

  const syncing = eventsLoading || alertsLoading;

  const chips = [
    {
      href: "/events",
      label: "Events",
      value: `${eventsData?.total ?? 0}`,
      icon: Activity,
      alert: false,
    },
    {
      href: "/alerts",
      label: "Alerts",
      value: openAlerts > 0 ? `${openAlerts} open` : "clear",
      icon: AlertTriangle,
      alert: openAlerts > 0,
    },
    { href: "/guardrails", label: "Guardrails", value: "enforced", icon: ShieldCheck, alert: false },
    { href: "/analytics", label: "Analytics", value: "live", icon: BarChart3, alert: false },
    { href: "/security-tests", label: "Testing", value: "ready", icon: FlaskConical, alert: false },
  ];

  return (
    <section
      aria-label="Security telemetry"
      className="mb-5 flex flex-wrap items-center gap-x-1 gap-y-1 rounded-xl border border-slate-200 bg-white px-2.5 py-1.5 dark:border-slate-800 dark:bg-slate-900"
    >
      <span className="mr-1 flex items-center gap-1.5 pl-1 text-[11px] font-medium text-slate-400 dark:text-slate-500">
        <span className="relative flex size-1.5">
          <span
            className={`absolute inline-flex size-full rounded-full ${
              syncing ? "bg-amber-400" : "animate-ping bg-emerald-400/60"
            }`}
          />
          <span
            className={`relative inline-flex size-1.5 rounded-full ${
              syncing ? "bg-amber-400" : "bg-emerald-400"
            }`}
          />
        </span>
        {syncing ? "Syncing" : "Live"}
      </span>

      <span className="mr-1 h-4 w-px bg-slate-200 dark:bg-slate-800" />

      {chips.map((c) => {
        const Icon = c.icon;
        const active = pathname === c.href;
        return (
          <Link
            key={c.href}
            href={c.href}
            aria-current={active ? "page" : undefined}
            className={`group flex items-center gap-1.5 rounded-lg px-2 py-1 text-[11px] transition-colors ${
              active
                ? "bg-indigo-50 text-indigo-700 dark:bg-indigo-500/10 dark:text-indigo-300"
                : "text-slate-500 hover:bg-slate-50 hover:text-slate-700 dark:text-slate-400 dark:hover:bg-slate-800/60 dark:hover:text-slate-200"
            }`}
          >
            <Icon className="size-3.5 opacity-70" />
            <span className="font-medium">{c.label}</span>
            <span
              className={`tabular-nums ${
                c.alert
                  ? "font-semibold text-red-600 dark:text-red-400"
                  : "text-slate-400 dark:text-slate-500"
              }`}
            >
              {c.value}
            </span>
          </Link>
        );
      })}

      <span className="ml-auto hidden items-center gap-1.5 pr-1.5 text-[10px] font-medium uppercase tracking-[0.1em] text-slate-400 dark:text-slate-500 sm:flex">
        Control link
        <span className="size-1.5 rounded-full bg-emerald-400" />
      </span>
    </section>
  );
}
