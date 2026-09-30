"use client";

import type { ReactNode } from "react";

import {
  Activity,
  AlertTriangle,
  BarChart3,
  Bot,
  CircleAlert,
  Gauge,
  ShieldAlert,
  ShieldCheck,
  Target,
  TrendingUp,
} from "lucide-react";

import { useAnalytics } from "@/features/analytics/use-analytics";

function formatDate(value?: string) {
  if (!value) return "—";

  return new Date(value).toLocaleDateString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

function getRiskClass(level: string) {
  const normalized = level.toUpperCase();

  if (normalized === "HIGH" || normalized === "CRITICAL") {
    return "border-red-500/20 bg-red-500/10 text-red-300";
  }

  if (normalized === "MEDIUM") {
    return "border-amber-500/20 bg-amber-500/10 text-amber-300";
  }

  return "border-emerald-500/20 bg-emerald-500/10 text-emerald-300";
}

function getRiskBarClass(level: string) {
  const normalized = level.toUpperCase();

  if (normalized === "HIGH" || normalized === "CRITICAL") {
    return "bg-red-400";
  }

  if (normalized === "MEDIUM") {
    return "bg-amber-400";
  }

  return "bg-emerald-400";
}

export default function AnalyticsPage() {
  const { agents, metrics, isLoading, isError } = useAnalytics();

  const totalEvents = metrics.reduce(
    (sum, metric) => sum + metric.total_events,
    0,
  );

  const allowedEvents = metrics.reduce(
    (sum, metric) => sum + metric.allowed_events,
    0,
  );

  const blockedEvents = metrics.reduce(
    (sum, metric) => sum + metric.blocked_events,
    0,
  );

  const suspiciousEvents = metrics.reduce(
    (sum, metric) => sum + metric.suspicious_events,
    0,
  );

  const policyViolations = metrics.reduce(
    (sum, metric) => sum + metric.policy_violations,
    0,
  );

  const averageRisk =
    metrics.length > 0
      ? metrics.reduce((sum, metric) => sum + metric.risk_score, 0) /
        metrics.length
      : 0;

  const averageBlockRate =
    metrics.length > 0
      ? metrics.reduce((sum, metric) => sum + metric.block_rate, 0) /
        metrics.length
      : 0;

  const coverage =
    agents.length > 0
      ? Math.min((metrics.length / agents.length) * 100, 100)
      : 0;

  const analyticsState = isLoading
    ? "Synchronizing"
    : isError
      ? "Degraded"
      : "Operational";

  return (
    <div className="space-y-6">
      {/* Header */}
      <section className="security-surface relative overflow-hidden p-6 sm:p-7">
        <div className="security-grid absolute inset-0 opacity-20" />

        <div className="relative">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <div className="flex flex-wrap items-center gap-2">
                <span className="inline-flex items-center gap-2 rounded-full border border-cyan-400/15 bg-cyan-400/5 px-3 py-1.5 text-[10px] font-semibold uppercase tracking-[0.18em] text-cyan-300">
                  <BarChart3 className="h-3.5 w-3.5" />
                  Security Intelligence
                </span>

                <span
                  className={`inline-flex items-center gap-2 rounded-full border px-3 py-1.5 text-[10px] font-semibold uppercase tracking-[0.18em] ${
                    isError
                      ? "border-amber-400/15 bg-amber-400/5 text-amber-300"
                      : "border-emerald-400/15 bg-emerald-400/5 text-emerald-300"
                  }`}
                >
                  <span className="relative flex h-1.5 w-1.5">
                    <span
                      className={`absolute inline-flex h-full w-full rounded-full ${
                        isError
                          ? "bg-amber-400/60"
                          : "animate-ping bg-emerald-400/60"
                      }`}
                    />
                    <span
                      className={`relative inline-flex h-1.5 w-1.5 rounded-full ${
                        isError ? "bg-amber-400" : "bg-emerald-400"
                      }`}
                    />
                  </span>
                  {analyticsState}
                </span>
              </div>

              <p className="mt-5 text-xs font-medium uppercase tracking-[0.2em] text-slate-500">
                Control Plane / Analytics
              </p>

              <h1 className="mt-2 text-3xl font-semibold tracking-tight text-white sm:text-4xl">
                Security Analytics
              </h1>

              <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-400">
                Measure runtime activity, enforcement outcomes, suspicious
                behavior, policy violations, and risk across the SentinelX
                agent fleet.
              </p>
            </div>

            <div className="hidden rounded-2xl border border-slate-800/80 bg-slate-950/50 p-4 sm:block">
              <Activity className="h-7 w-7 text-cyan-300" />

              <p className="mt-3 text-[9px] font-semibold uppercase tracking-[0.18em] text-slate-600">
                Telemetry
              </p>

              <p className="mt-1 text-xs font-medium text-slate-300">
                Live metrics
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Metric rail */}
      <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
        <MetricCard
          label="Events"
          value={totalEvents}
          detail={`${agents.length} monitored agents`}
          icon={<Activity className="h-4 w-4" />}
          accent="cyan"
        />

        <MetricCard
          label="Blocked"
          value={blockedEvents}
          detail="Runtime enforcement"
          icon={<ShieldAlert className="h-4 w-4" />}
          accent="red"
        />

        <MetricCard
          label="Suspicious"
          value={suspiciousEvents}
          detail="Behavioral signals"
          icon={<AlertTriangle className="h-4 w-4" />}
          accent="amber"
        />

        <MetricCard
          label="Violations"
          value={policyViolations}
          detail="Policy enforcement"
          icon={<ShieldCheck className="h-4 w-4" />}
          accent="violet"
        />

        <MetricCard
          label="Allowed"
          value={allowedEvents}
          detail="Permitted activity"
          icon={<Target className="h-4 w-4" />}
          accent="emerald"
        />
      </section>

      {/* Main intelligence area */}
      <section className="grid gap-6 xl:grid-cols-[minmax(0,1.55fr)_minmax(300px,0.45fr)]">
        <div className="security-surface p-6">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-500">
                Fleet Intelligence
              </p>

              <h2 className="mt-2 text-lg font-semibold text-white">
                Agent risk posture
              </h2>

              <p className="mt-1 text-xs text-slate-500">
                Current security measurements returned by the analytics
                service.
              </p>
            </div>

            <div className="rounded-xl border border-cyan-400/10 bg-cyan-400/5 p-2.5 text-cyan-300">
              <TrendingUp className="h-5 w-5" />
            </div>
          </div>

          {isLoading ? (
            <AnalyticsLoading />
          ) : isError ? (
            <AnalyticsError />
          ) : metrics.length === 0 ? (
            <AnalyticsEmpty />
          ) : (
            <div className="mt-6 space-y-3">
              {metrics.map((metric) => (
                <AgentMetricRow
                  key={metric.agent_id}
                  agentId={metric.agent_id}
                  periodStart={metric.period_start}
                  periodEnd={metric.period_end}
                  events={metric.total_events}
                  blocked={metric.blocked_events}
                  suspicious={metric.suspicious_events}
                  violations={metric.policy_violations}
                  riskScore={metric.risk_score}
                  riskLevel={metric.risk_level}
                  blockRate={metric.block_rate}
                />
              ))}
            </div>
          )}
        </div>

        {/* Risk command panel */}
        <div className="security-surface p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-500">
                Risk Signal
              </p>

              <h2 className="mt-2 text-lg font-semibold text-white">
                Fleet score
              </h2>
            </div>

            <Gauge className="h-5 w-5 text-cyan-300" />
          </div>

          <div className="mt-8 flex justify-center">
            <div className="relative flex h-48 w-48 items-center justify-center rounded-full border-[10px] border-slate-800">
              <div
                className="absolute inset-[-10px] rounded-full"
                style={{
                  background: `conic-gradient(rgb(34 211 238 / 0.7) ${
                    Math.min(averageRisk, 100) * 3.6
                  }deg, transparent 0deg)`,
                  mask: "linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0)",
                  maskComposite: "exclude",
                  padding: "10px",
                }}
              />

              <div className="absolute inset-3 rounded-full border border-slate-800/80 bg-[#080c12]" />

              <div className="relative text-center">
                <p className="text-4xl font-semibold tracking-tight text-white">
                  {averageRisk.toFixed(1)}
                </p>

                <p className="mt-1 text-[9px] font-semibold uppercase tracking-[0.2em] text-slate-500">
                  Risk score
                </p>
              </div>
            </div>
          </div>

          <div className="mt-7 space-y-4">
            <SignalLine
              label="Analytics coverage"
              value={`${metrics.length}/${agents.length}`}
              percentage={coverage}
            />

            <SignalLine
              label="Average block rate"
              value={`${(averageBlockRate * 100).toFixed(1)}%`}
              percentage={Math.min(averageBlockRate * 100, 100)}
            />
          </div>

          <div className="mt-5 flex gap-3 rounded-xl border border-cyan-400/10 bg-cyan-400/[0.035] p-4">
            <CircleAlert className="mt-0.5 h-4 w-4 shrink-0 text-cyan-300" />

            <p className="text-xs leading-5 text-slate-500">
              Risk posture is calculated from metrics returned by the
              SentinelX analytics service. Empty fleets do not receive
              synthetic data.
            </p>
          </div>
        </div>
      </section>

      {/* Registry */}
      <section className="security-surface overflow-hidden">
        <div className="border-b border-slate-800/80 p-6">
          <div className="flex flex-wrap items-end justify-between gap-4">
            <div>
              <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-500">
                Analytics Registry
              </p>

              <h2 className="mt-2 text-lg font-semibold text-white">
                Security metrics
              </h2>

              <p className="mt-1 text-xs text-slate-500">
                Per-agent measurements currently available to the control
                plane.
              </p>
            </div>

            <span className="rounded-full border border-slate-800 bg-slate-950/60 px-3 py-1.5 text-[10px] font-semibold uppercase tracking-[0.16em] text-slate-500">
              {metrics.length} records
            </span>
          </div>
        </div>

        {isLoading ? (
          <div className="p-6">
            <div className="h-12 animate-pulse rounded-xl bg-slate-800/40" />
          </div>
        ) : isError ? (
          <div className="p-6">
            <AnalyticsError />
          </div>
        ) : metrics.length === 0 ? (
          <div className="p-10 text-center">
            <BarChart3 className="mx-auto h-9 w-9 text-slate-700" />

            <p className="mt-4 text-sm font-medium text-slate-300">
              No agent metrics
            </p>

            <p className="mx-auto mt-2 max-w-lg text-xs leading-5 text-slate-500">
              The analytics registry is empty because no registered agents
              currently have available security metrics.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[820px] text-left">
              <thead>
                <tr className="border-b border-slate-800/80 text-[9px] uppercase tracking-[0.16em] text-slate-600">
                  <th className="px-6 py-3 font-semibold">Agent</th>
                  <th className="py-3 font-semibold">Events</th>
                  <th className="py-3 font-semibold">Blocked</th>
                  <th className="py-3 font-semibold">Violations</th>
                  <th className="py-3 font-semibold">Block rate</th>
                  <th className="py-3 font-semibold">Risk</th>
                </tr>
              </thead>

              <tbody>
                {metrics.map((metric) => (
                  <tr
                    key={metric.agent_id}
                    className="border-b border-slate-800/60 transition-colors last:border-0 hover:bg-white/[0.015]"
                  >
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="rounded-lg border border-cyan-400/10 bg-cyan-400/5 p-2 text-cyan-300">
                          <Bot className="h-4 w-4" />
                        </div>

                        <div>
                          <p className="text-sm font-medium text-slate-200">
                            Agent #{metric.agent_id}
                          </p>

                          <p className="mt-0.5 text-[10px] text-slate-600">
                            {formatDate(metric.period_start)} →{" "}
                            {formatDate(metric.period_end)}
                          </p>
                        </div>
                      </div>
                    </td>

                    <td className="py-4 text-sm text-slate-400">
                      {metric.total_events}
                    </td>

                    <td className="py-4 text-sm text-slate-400">
                      {metric.blocked_events}
                    </td>

                    <td className="py-4 text-sm text-slate-400">
                      {metric.policy_violations}
                    </td>

                    <td className="py-4 text-sm text-slate-400">
                      {(metric.block_rate * 100).toFixed(1)}%
                    </td>

                    <td className="py-4 pr-6">
                      <span
                        className={`rounded-full border px-2.5 py-1 text-[10px] font-semibold uppercase tracking-wider ${getRiskClass(
                          metric.risk_level,
                        )}`}
                      >
                        {metric.risk_level}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {/* Footer status */}
      <section className="grid gap-3 sm:grid-cols-3">
        <OperationalSignal
          label="Telemetry"
          value={isError ? "Degraded" : "Available"}
          tone={isError ? "amber" : "emerald"}
        />

        <OperationalSignal
          label="Analytics coverage"
          value={`${Math.round(coverage)}%`}
          tone="cyan"
        />

        <OperationalSignal
          label="Risk engine"
          value="Active"
          tone="emerald"
        />
      </section>
    </div>
  );
}

function MetricCard({
  label,
  value,
  detail,
  icon,
  accent,
}: {
  label: string;
  value: number;
  detail: string;
  icon: ReactNode;
  accent: "cyan" | "red" | "amber" | "violet" | "emerald";
}) {
  const accentClasses = {
    cyan: "border-cyan-400/10 bg-cyan-400/5 text-cyan-300",
    red: "border-red-400/10 bg-red-400/5 text-red-300",
    amber: "border-amber-400/10 bg-amber-400/5 text-amber-300",
    violet: "border-violet-400/10 bg-violet-400/5 text-violet-300",
    emerald: "border-emerald-400/10 bg-emerald-400/5 text-emerald-300",
  };

  return (
    <div className="security-surface security-surface-hover p-5">
      <div className="flex items-center justify-between gap-3">
        <span className="text-[9px] font-semibold uppercase tracking-[0.16em] text-slate-500">
          {label}
        </span>

        <div className={`rounded-lg border p-2 ${accentClasses[accent]}`}>
          {icon}
        </div>
      </div>

      <p className="mt-5 text-3xl font-semibold tracking-tight text-white">
        {value}
      </p>

      <p className="mt-1 text-[11px] text-slate-600">{detail}</p>
    </div>
  );
}

function AgentMetricRow({
  agentId,
  periodStart,
  periodEnd,
  events,
  blocked,
  suspicious,
  violations,
  riskScore,
  riskLevel,
  blockRate,
}: {
  agentId: number;
  periodStart?: string;
  periodEnd?: string;
  events: number;
  blocked: number;
  suspicious: number;
  violations: number;
  riskScore: number;
  riskLevel: string;
  blockRate: number;
}) {
  return (
    <div className="group rounded-xl border border-slate-800/80 bg-[#080c12] p-4 transition-all duration-200 hover:border-cyan-400/10 hover:bg-[#0a1018]">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="rounded-lg border border-cyan-400/10 bg-cyan-400/5 p-2 text-cyan-300">
            <Bot className="h-4 w-4" />
          </div>

          <div>
            <p className="text-sm font-medium text-slate-200">
              Agent #{agentId}
            </p>

            <p className="mt-1 text-[10px] text-slate-600">
              {formatDate(periodStart)} → {formatDate(periodEnd)}
            </p>
          </div>
        </div>

        <span
          className={`rounded-full border px-2.5 py-1 text-[10px] font-semibold uppercase tracking-wider ${getRiskClass(
            riskLevel,
          )}`}
        >
          {riskLevel}
        </span>
      </div>

      <div className="mt-4 grid grid-cols-2 gap-2 sm:grid-cols-5">
        <MiniStat label="Events" value={events} />
        <MiniStat label="Blocked" value={blocked} />
        <MiniStat label="Suspicious" value={suspicious} />
        <MiniStat label="Violations" value={violations} />
        <MiniStat label="Risk" value={riskScore.toFixed(1)} />
      </div>

      <div className="mt-4">
        <div className="flex items-center justify-between text-[10px]">
          <span className="uppercase tracking-wider text-slate-600">
            Block rate
          </span>

          <span className="font-medium text-slate-400">
            {(blockRate * 100).toFixed(1)}%
          </span>
        </div>

        <div className="mt-2 h-1 overflow-hidden rounded-full bg-slate-800">
          <div
            className={`h-full rounded-full ${getRiskBarClass(
              riskLevel,
            )} transition-all duration-500`}
            style={{
              width: `${Math.min(blockRate * 100, 100)}%`,
            }}
          />
        </div>
      </div>
    </div>
  );
}

function MiniStat({
  label,
  value,
}: {
  label: string;
  value: number | string;
}) {
  return (
    <div className="rounded-lg border border-slate-800/80 bg-slate-900/40 px-3 py-2.5">
      <p className="text-[9px] font-semibold uppercase tracking-wider text-slate-600">
        {label}
      </p>

      <p className="mt-1 text-sm font-semibold text-slate-300">{value}</p>
    </div>
  );
}

function SignalLine({
  label,
  value,
  percentage,
}: {
  label: string;
  value: string;
  percentage: number;
}) {
  return (
    <div>
      <div className="flex items-center justify-between text-xs">
        <span className="text-slate-500">{label}</span>
        <span className="font-medium text-slate-300">{value}</span>
      </div>

      <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-slate-800">
        <div
          className="h-full rounded-full bg-cyan-400 transition-all duration-500"
          style={{
            width: `${Math.min(Math.max(percentage, 0), 100)}%`,
          }}
        />
      </div>
    </div>
  );
}

function OperationalSignal({
  label,
  value,
  tone,
}: {
  label: string;
  value: string;
  tone: "cyan" | "emerald" | "amber";
}) {
  const toneClasses = {
    cyan: "bg-cyan-400",
    emerald: "bg-emerald-400",
    amber: "bg-amber-400",
  };

  return (
    <div className="security-surface flex items-center justify-between px-4 py-3.5">
      <span className="text-[10px] font-semibold uppercase tracking-[0.16em] text-slate-600">
        {label}
      </span>

      <span className="flex items-center gap-2 text-xs font-medium text-slate-300">
        <span
          className={`h-1.5 w-1.5 rounded-full ${toneClasses[tone]}`}
        />
        {value}
      </span>
    </div>
  );
}

function AnalyticsLoading() {
  return (
    <div className="mt-6 space-y-3">
      {[1, 2, 3].map((item) => (
        <div
          key={item}
          className="h-32 animate-pulse rounded-xl bg-slate-800/30"
        />
      ))}
    </div>
  );
}

function AnalyticsError() {
  return (
    <div className="mt-6 rounded-xl border border-red-500/20 bg-red-500/5 p-5">
      <div className="flex items-start gap-3">
        <ShieldAlert className="mt-0.5 h-5 w-5 shrink-0 text-red-300" />

        <div>
          <p className="text-sm font-medium text-red-300">
            Analytics telemetry unavailable
          </p>

          <p className="mt-1 text-xs leading-5 text-red-300/60">
            SentinelX could not retrieve the current analytics records.
            Verify the backend and authentication state.
          </p>
        </div>
      </div>
    </div>
  );
}

function AnalyticsEmpty() {
  return (
    <div className="mt-6 rounded-xl border border-dashed border-slate-800 bg-[#080c12] p-10 text-center">
      <Gauge className="mx-auto h-9 w-9 text-slate-700" />

      <p className="mt-4 text-sm font-medium text-slate-300">
        No analytics data available
      </p>

      <p className="mx-auto mt-2 max-w-md text-xs leading-5 text-slate-500">
        Agent-level analytics will appear once SentinelX agents are registered
        and security events are generated.
      </p>
    </div>
  );
}