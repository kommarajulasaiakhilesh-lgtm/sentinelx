"use client";

import type { ReactNode } from "react";
import {
  AlertOctagon,
  AlertTriangle,
  CheckCircle2,
  Clock3,
  Eye,
  LoaderCircle,
  ShieldAlert,
  ShieldCheck,
  Siren,
} from "lucide-react";

import { useSecurityAlerts } from "@/features/alerts/use-security-alerts";

function formatDate(value?: string | null) {
  if (!value) {
    return "—";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat("en-IN", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

function getSeverityClass(severity: string) {
  const normalized = severity.toUpperCase();

  if (normalized === "CRITICAL") {
    return "border-red-400/20 bg-red-400/10 text-red-300";
  }

  if (normalized === "HIGH") {
    return "border-orange-400/20 bg-orange-400/10 text-orange-300";
  }

  if (normalized === "MEDIUM") {
    return "border-amber-400/20 bg-amber-400/10 text-amber-300";
  }

  return "border-slate-700 bg-slate-800/50 text-slate-300";
}

function getStatusClass(status: string) {
  const normalized = status.toUpperCase();

  if (normalized === "OPEN") {
    return "border-red-400/20 bg-red-400/10 text-red-300";
  }

  if (normalized === "INVESTIGATING") {
    return "border-amber-400/20 bg-amber-400/10 text-amber-300";
  }

  if (normalized === "RESOLVED" || normalized === "CLOSED") {
    return "border-emerald-400/20 bg-emerald-400/10 text-emerald-300";
  }

  return "border-slate-700 bg-slate-800/50 text-slate-300";
}

function MetricCard({
  label,
  value,
  detail,
  icon,
  tone,
}: {
  label: string;
  value: string | number;
  detail: string;
  icon: ReactNode;
  tone: "red" | "orange" | "amber" | "emerald";
}) {
  const toneClasses = {
    red: {
      icon: "border-red-400/15 bg-red-400/10 text-red-300",
      value: "text-red-200",
    },
    orange: {
      icon: "border-orange-400/15 bg-orange-400/10 text-orange-300",
      value: "text-orange-200",
    },
    amber: {
      icon: "border-amber-400/15 bg-amber-400/10 text-amber-300",
      value: "text-amber-200",
    },
    emerald: {
      icon: "border-emerald-400/15 bg-emerald-400/10 text-emerald-300",
      value: "text-emerald-200",
    },
  }[tone];

  return (
    <article className="security-surface security-surface-hover relative overflow-hidden p-5">
      <div
        className={`pointer-events-none absolute -right-10 -top-10 size-28 rounded-full blur-3xl ${
          tone === "red"
            ? "bg-red-400/5"
            : tone === "orange"
              ? "bg-orange-400/5"
              : tone === "amber"
                ? "bg-amber-400/5"
                : "bg-emerald-400/5"
        }`}
      />

      <div className="relative flex items-start justify-between gap-4">
        <div>
          <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-500">
            {label}
          </p>

          <p className={`mt-3 text-3xl font-semibold tracking-tight ${toneClasses.value}`}>
            {value}
          </p>

          <p className="mt-1 text-xs text-slate-500">{detail}</p>
        </div>

        <div className={`rounded-xl border p-3 ${toneClasses.icon}`}>
          {icon}
        </div>
      </div>
    </article>
  );
}

function SeverityBadge({ severity }: { severity: string }) {
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[9px] font-semibold uppercase tracking-[0.14em] ${getSeverityClass(
        severity,
      )}`}
    >
      <span className="size-1.5 rounded-full bg-current" />
      {severity}
    </span>
  );
}

function StatusBadge({ status }: { status: string }) {
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-[9px] font-semibold uppercase tracking-[0.14em] ${getStatusClass(
        status,
      )}`}
    >
      <span className="size-1.5 rounded-full bg-current" />
      {status}
    </span>
  );
}

function LoadingState() {
  return (
    <div className="flex min-h-72 items-center justify-center">
      <div className="flex items-center gap-2 text-sm text-slate-500">
        <LoaderCircle className="size-4 animate-spin text-cyan-400" />
        Loading alert telemetry...
      </div>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="flex min-h-72 flex-col items-center justify-center px-6 text-center">
      <div className="flex size-14 items-center justify-center rounded-2xl border border-emerald-400/15 bg-emerald-400/10">
        <ShieldCheck className="size-7 text-emerald-300" />
      </div>

      <h3 className="mt-5 text-sm font-semibold text-white">
        No security alerts
      </h3>

      <p className="mt-2 max-w-md text-sm leading-6 text-slate-500">
        The SentinelX control plane has not recorded any alerts for the
        current account.
      </p>

      <div className="mt-5 inline-flex items-center gap-2 rounded-full border border-emerald-400/15 bg-emerald-400/5 px-3 py-1.5 text-[9px] font-semibold uppercase tracking-[0.18em] text-emerald-300">
        <CheckCircle2 className="size-3.5" />
        No active incidents
      </div>
    </div>
  );
}

function ErrorState() {
  return (
    <div className="flex min-h-72 items-center justify-center p-6">
      <div className="max-w-md text-center">
        <AlertTriangle className="mx-auto size-9 text-red-400" />

        <h3 className="mt-4 text-sm font-semibold text-white">
          Alert telemetry unavailable
        </h3>

        <p className="mt-2 text-sm leading-6 text-slate-500">
          SentinelX could not retrieve the current security alert stream.
          Verify that the backend is running and authenticated.
        </p>
      </div>
    </div>
  );
}

function OperationalCard({
  icon,
  title,
  description,
  children,
}: {
  icon: ReactNode;
  title: string;
  description: string;
  children: ReactNode;
}) {
  return (
    <div className="security-surface security-surface-hover p-5">
      <div className="flex items-center gap-3">
        <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-2.5">
          {icon}
        </div>

        <div className="min-w-0">
          <p className="text-sm font-semibold text-white">{title}</p>
          <p className="mt-0.5 text-xs text-slate-500">{description}</p>
        </div>
      </div>

      <div className="mt-5">{children}</div>
    </div>
  );
}

export default function AlertsPage() {
  const {
    data,
    isLoading,
    isError,
  } = useSecurityAlerts(1, 10);

  const alerts = data?.items ?? [];

  const openAlerts = alerts.filter(
    (alert) =>
      alert.status.toUpperCase() === "OPEN" ||
      alert.status.toUpperCase() === "INVESTIGATING",
  ).length;

  const criticalAlerts = alerts.filter(
    (alert) => alert.severity.toUpperCase() === "CRITICAL",
  ).length;

  const highAlerts = alerts.filter(
    (alert) => alert.severity.toUpperCase() === "HIGH",
  ).length;

  const resolvedAlerts = alerts.filter(
    (alert) =>
      alert.status.toUpperCase() === "RESOLVED" ||
      alert.status.toUpperCase() === "CLOSED",
  ).length;

  const highPriority = criticalAlerts + highAlerts;

  return (
    <div className="space-y-6 sm:space-y-8">
      {/* Header */}
      <section className="relative overflow-hidden rounded-2xl border border-red-400/10 bg-red-400/[0.025] p-6 sm:p-8">
        <div className="security-grid absolute inset-0 opacity-25" />

        <div className="pointer-events-none absolute -right-24 -top-24 size-64 rounded-full bg-red-400/5 blur-3xl" />

        <div className="relative">
          <div className="flex flex-wrap items-center gap-3">
            <span className="inline-flex items-center gap-2 rounded-full border border-red-400/20 bg-red-400/[0.06] px-3 py-1.5 text-[10px] font-semibold uppercase tracking-[0.18em] text-red-300">
              <Siren className="size-3.5" />
              Incident Response
            </span>

            <span className="inline-flex items-center gap-2 text-[10px] font-medium uppercase tracking-[0.16em] text-emerald-400">
              <span className="size-1.5 animate-pulse rounded-full bg-emerald-400" />
              Alert pipeline online
            </span>
          </div>

          <div className="mt-5 flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <h1 className="text-2xl font-semibold tracking-tight text-white sm:text-3xl">
                Alerts &amp; Incidents
              </h1>

              <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-400">
                Investigate security alerts generated by SentinelX agents,
                policies, and runtime enforcement.
              </p>
            </div>

            <div className="flex shrink-0 items-center gap-3 rounded-xl border border-red-400/10 bg-red-400/[0.035] px-4 py-3">
              <div className="flex size-9 items-center justify-center rounded-lg border border-red-400/15 bg-red-400/10">
                <ShieldAlert className="size-4 text-red-300" />
              </div>

              <div>
                <p className="text-[9px] font-semibold uppercase tracking-[0.16em] text-red-400">
                  Incident state
                </p>

                <p className="mt-0.5 text-xs text-slate-400">
                  {openAlerts > 0
                    ? `${openAlerts} active incident${openAlerts === 1 ? "" : "s"}`
                    : "No active incidents"}
                </p>
              </div>
            </div>
          </div>

          <div className="mt-7 grid gap-2 sm:grid-cols-3">
            {[
              ["DETECT", "Identify suspicious activity"],
              ["TRIAGE", "Prioritize security alerts"],
              ["RESPOND", "Track incident resolution"],
            ].map(([title, description]) => (
              <div
                key={title}
                className="rounded-xl border border-slate-800/70 bg-slate-950/30 p-4"
              >
                <p className="text-[9px] font-semibold uppercase tracking-[0.2em] text-cyan-400">
                  {title}
                </p>

                <p className="mt-2 text-xs text-slate-400">
                  {description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Metrics */}
      <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard
          label="Total Alerts"
          value={data?.total ?? 0}
          detail="Recorded security alerts"
          icon={<AlertOctagon className="size-5" />}
          tone="red"
        />

        <MetricCard
          label="Open Incidents"
          value={openAlerts}
          detail="Open or investigating"
          icon={<ShieldAlert className="size-5" />}
          tone="orange"
        />

        <MetricCard
          label="High Priority"
          value={highPriority}
          detail={`${criticalAlerts} critical · ${highAlerts} high`}
          icon={<AlertTriangle className="size-5" />}
          tone="amber"
        />

        <MetricCard
          label="Resolved Alerts"
          value={resolvedAlerts}
          detail="Resolved or closed"
          icon={<CheckCircle2 className="size-5" />}
          tone="emerald"
        />
      </section>

      {/* Incident queue */}
      <section className="security-surface overflow-hidden">
        <div className="flex flex-col gap-4 border-b border-slate-800/80 px-5 py-4 sm:flex-row sm:items-center sm:justify-between sm:px-6">
          <div>
            <div className="flex flex-wrap items-center gap-3">
              <div>
                <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-red-400">
                  Security operations
                </p>

                <h2 className="mt-1 text-lg font-semibold text-white">
                  Incident Queue
                </h2>
              </div>

              <span className="rounded-full border border-slate-800 bg-slate-950/60 px-2.5 py-1 text-[9px] font-semibold uppercase tracking-[0.15em] text-slate-500">
                {data?.total ?? 0} alerts
              </span>
            </div>

            <p className="mt-1 text-xs text-slate-500">
              Latest alerts requiring security operations attention
            </p>
          </div>

          <button
            type="button"
            className="inline-flex w-fit items-center gap-2 rounded-xl border border-slate-800 bg-slate-950/50 px-4 py-2.5 text-xs font-semibold text-slate-400 transition hover:border-cyan-400/20 hover:text-cyan-300 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-400/50"
          >
            <Eye className="size-4" />
            Review Queue
          </button>
        </div>

        {isLoading && <LoadingState />}

        {isError && !isLoading && <ErrorState />}

        {!isLoading && !isError && alerts.length === 0 && <EmptyState />}

        {!isLoading && !isError && alerts.length > 0 && (
          <div className="divide-y divide-slate-800/60">
            {alerts.map((alert) => (
              <article
                key={alert.id}
                className="group relative px-5 py-5 transition-colors hover:bg-white/[0.015] sm:px-6"
              >
                <div
                  className={`absolute inset-y-0 left-0 w-0.5 ${
                    alert.severity.toUpperCase() === "CRITICAL"
                      ? "bg-red-400"
                      : alert.severity.toUpperCase() === "HIGH"
                        ? "bg-orange-400"
                        : alert.severity.toUpperCase() === "MEDIUM"
                          ? "bg-amber-400"
                          : "bg-slate-600"
                  }`}
                />

                <div className="flex flex-col gap-5 xl:flex-row xl:items-center xl:justify-between">
                  <div className="flex min-w-0 gap-4">
                    <div className="mt-0.5 flex size-10 shrink-0 items-center justify-center rounded-xl border border-red-400/15 bg-red-400/10 text-red-300">
                      <Siren className="size-5" />
                    </div>

                    <div className="min-w-0">
                      <div className="flex flex-wrap items-center gap-2.5">
                        <h3 className="truncate text-sm font-semibold text-white">
                          {alert.title}
                        </h3>

                        <SeverityBadge severity={alert.severity} />
                      </div>

                      <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-500">
                        {alert.description ||
                          "No incident description provided."}
                      </p>

                      <div className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-2 text-[11px] text-slate-600">
                        <span className="font-mono text-slate-500">
                          ALERT-{alert.id}
                        </span>

                        <span className="flex items-center gap-1.5">
                          <Clock3 className="size-3.5" />
                          {formatDate(alert.created_at)}
                        </span>

                        {alert.agent_id !== null &&
                          alert.agent_id !== undefined && (
                            <span>Agent #{alert.agent_id}</span>
                          )}
                      </div>
                    </div>
                  </div>

                  <div className="flex shrink-0 items-center gap-3 xl:pl-4">
                    <StatusBadge status={alert.status} />
                  </div>
                </div>
              </article>
            ))}
          </div>
        )}
      </section>

      {/* Operational posture */}
      <section className="grid gap-3 lg:grid-cols-3">
        <OperationalCard
          icon={<Siren className="size-5 text-cyan-300" />}
          title="Detection Pipeline"
          description="Alert generation operational"
        >
          <div className="flex items-center gap-3">
            <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-slate-800">
              <div className="h-full w-full rounded-full bg-cyan-400" />
            </div>

            <span className="text-[9px] font-semibold uppercase tracking-[0.14em] text-cyan-300">
              Online
            </span>
          </div>
        </OperationalCard>

        <OperationalCard
          icon={<AlertTriangle className="size-5 text-amber-300" />}
          title="Priority Monitoring"
          description="Severity classification active"
        >
          <div className="flex items-center gap-4 text-xs">
            <span className="flex items-center gap-2 text-red-300">
              <span className="size-1.5 rounded-full bg-red-400" />
              {criticalAlerts} critical
            </span>

            <span className="flex items-center gap-2 text-orange-300">
              <span className="size-1.5 rounded-full bg-orange-400" />
              {highAlerts} high
            </span>
          </div>
        </OperationalCard>

        <OperationalCard
          icon={<CheckCircle2 className="size-5 text-emerald-300" />}
          title="Response Tracking"
          description="Incident lifecycle monitored"
        >
          <div className="flex items-center gap-2 text-xs text-emerald-300">
            <span className="size-1.5 rounded-full bg-emerald-400" />
            Resolution telemetry online
          </div>
        </OperationalCard>
      </section>
    </div>
  );
}