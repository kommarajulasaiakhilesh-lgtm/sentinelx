"use client";

import {
  Activity,
  AlertTriangle,
  BarChart3,
  Bot,
  Gauge,
  ShieldAlert,
  ShieldCheck,
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

export default function AnalyticsPage() {
  const { agents, metrics, isLoading, isError } = useAnalytics();

  const totalEvents = metrics.reduce(
    (sum, metric) => sum + metric.total_events,
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

  return (
    <div className="space-y-8">
      {/* Hero */}
      <section className="relative overflow-hidden rounded-2xl border border-cyan-500/10 bg-[#0a0f16] p-6 sm:p-8">
        <div className="security-grid absolute inset-0 opacity-30" />

        <div className="relative">
          <div className="mb-4 flex flex-wrap items-center gap-3">
            <span className="inline-flex items-center gap-2 rounded-full border border-cyan-400/20 bg-cyan-400/5 px-3 py-1.5 text-[10px] font-semibold uppercase tracking-[0.18em] text-cyan-300">
              <BarChart3 className="h-3.5 w-3.5" />
              Security Intelligence
            </span>

            <span className="inline-flex items-center gap-2 rounded-full border border-emerald-400/20 bg-emerald-400/5 px-3 py-1.5 text-[10px] font-semibold uppercase tracking-[0.18em] text-emerald-300">
              <Activity className="h-3.5 w-3.5" />
              Analytics Online
            </span>
          </div>

          <h1 className="text-3xl font-semibold tracking-tight text-white sm:text-4xl">
            Security Analytics
          </h1>

          <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-400">
            Measure agent activity, enforcement outcomes, policy violations,
            suspicious behavior, and runtime risk across the SentinelX
            control plane.
          </p>
        </div>
      </section>

      {/* Metrics */}
      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard
          label="Total Events"
          value={totalEvents}
          icon={Activity}
          detail={`${agents.length} monitored agents`}
        />

        <MetricCard
          label="Blocked Events"
          value={blockedEvents}
          icon={ShieldAlert}
          detail="Runtime enforcement"
        />

        <MetricCard
          label="Suspicious Activity"
          value={suspiciousEvents}
          icon={AlertTriangle}
          detail="Behavioral signals"
        />

        <MetricCard
          label="Policy Violations"
          value={policyViolations}
          icon={ShieldCheck}
          detail="Policy enforcement"
        />
      </section>

      {/* Risk overview */}
      <section className="grid gap-6 xl:grid-cols-[1.4fr_0.6fr]">
        <div className="rounded-2xl border border-slate-800 bg-[#0a0f16] p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
                Fleet Risk Overview
              </p>

              <h2 className="mt-2 text-lg font-semibold text-white">
                Agent security posture
              </h2>
            </div>

            <div className="rounded-xl border border-cyan-400/10 bg-cyan-400/5 p-2.5 text-cyan-300">
              <TrendingUp className="h-5 w-5" />
            </div>
          </div>

          {isLoading ? (
            <div className="mt-8 h-32 animate-pulse rounded-xl bg-slate-800/40" />
          ) : metrics.length === 0 ? (
            <div className="mt-8 rounded-xl border border-dashed border-slate-800 bg-[#080c12] p-8 text-center">
              <Gauge className="mx-auto h-8 w-8 text-slate-600" />

              <p className="mt-4 text-sm font-medium text-slate-300">
                No analytics data available
              </p>

              <p className="mx-auto mt-2 max-w-md text-xs leading-5 text-slate-500">
                Agent-level analytics will appear here once SentinelX agents
                are registered and security events are generated.
              </p>
            </div>
          ) : (
            <div className="mt-6 space-y-3">
              {metrics.map((metric) => (
                <div
                  key={metric.agent_id}
                  className="rounded-xl border border-slate-800 bg-[#080c12] p-4"
                >
                  <div className="flex flex-wrap items-center justify-between gap-4">
                    <div className="flex items-center gap-3">
                      <div className="rounded-lg border border-cyan-400/10 bg-cyan-400/5 p-2 text-cyan-300">
                        <Bot className="h-4 w-4" />
                      </div>

                      <div>
                        <p className="text-sm font-medium text-slate-200">
                          Agent #{metric.agent_id}
                        </p>

                        <p className="mt-1 text-[11px] text-slate-500">
                          {formatDate(metric.period_start)} →{" "}
                          {formatDate(metric.period_end)}
                        </p>
                      </div>
                    </div>

                    <span
                      className={`rounded-full border px-2.5 py-1 text-[10px] font-semibold uppercase tracking-wider ${getRiskClass(
                        metric.risk_level,
                      )}`}
                    >
                      {metric.risk_level}
                    </span>
                  </div>

                  <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-4">
                    <MiniStat
                      label="Events"
                      value={metric.total_events}
                    />

                    <MiniStat
                      label="Blocked"
                      value={metric.blocked_events}
                    />

                    <MiniStat
                      label="Suspicious"
                      value={metric.suspicious_events}
                    />

                    <MiniStat
                      label="Risk Score"
                      value={metric.risk_score.toFixed(1)}
                    />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Risk score */}
        <div className="rounded-2xl border border-slate-800 bg-[#0a0f16] p-6">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
            Fleet Risk Score
          </p>

          <div className="mt-6 flex items-center justify-center">
            <div className="relative flex h-44 w-44 items-center justify-center rounded-full border-[10px] border-cyan-400/10">
              <div className="absolute inset-2 rounded-full border border-cyan-400/10" />

              <div className="text-center">
                <p className="text-4xl font-semibold text-white">
                  {averageRisk.toFixed(1)}
                </p>

                <p className="mt-1 text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-500">
                  Risk Score
                </p>
              </div>
            </div>
          </div>

          <div className="mt-6 rounded-xl border border-slate-800 bg-[#080c12] p-4">
            <div className="flex items-center justify-between text-xs">
              <span className="text-slate-500">Analytics coverage</span>
              <span className="font-medium text-slate-300">
                {agents.length > 0
                  ? `${metrics.length}/${agents.length}`
                  : "0/0"}
              </span>
            </div>

            <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-slate-800">
              <div
                className="h-full rounded-full bg-cyan-400"
                style={{
                  width:
                    agents.length > 0
                      ? `${Math.min(
                          (metrics.length / agents.length) * 100,
                          100,
                        )}%`
                      : "0%",
                }}
              />
            </div>
          </div>

          <div className="mt-4 flex items-start gap-3 rounded-xl border border-cyan-400/10 bg-cyan-400/5 p-4">
            <Gauge className="mt-0.5 h-4 w-4 shrink-0 text-cyan-300" />

            <p className="text-xs leading-5 text-slate-400">
              Risk posture is calculated from the security metrics returned
              by the SentinelX analytics service.
            </p>
          </div>
        </div>
      </section>

      {/* Analytics detail */}
      <section className="rounded-2xl border border-slate-800 bg-[#0a0f16] p-6">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
              Analytics Registry
            </p>

            <h2 className="mt-2 text-lg font-semibold text-white">
              Agent Metrics
            </h2>
          </div>

          <span className="rounded-full border border-slate-800 bg-slate-900/60 px-3 py-1.5 text-[10px] font-semibold uppercase tracking-wider text-slate-500">
            {metrics.length} RECORDS
          </span>
        </div>

        {isError ? (
          <div className="mt-6 rounded-xl border border-red-500/20 bg-red-500/5 p-5">
            <p className="text-sm font-medium text-red-300">
              Analytics telemetry unavailable
            </p>

            <p className="mt-1 text-xs text-red-300/60">
              SentinelX could not retrieve one or more agent analytics
              records. Verify the backend and authentication state.
            </p>
          </div>
        ) : metrics.length === 0 && !isLoading ? (
          <div className="mt-6 rounded-xl border border-dashed border-slate-800 bg-[#080c12] p-10 text-center">
            <BarChart3 className="mx-auto h-9 w-9 text-slate-700" />

            <p className="mt-4 text-sm font-medium text-slate-300">
              No agent metrics
            </p>

            <p className="mx-auto mt-2 max-w-lg text-xs leading-5 text-slate-500">
              The analytics registry is empty because the current account
              has no registered agents with available security metrics.
            </p>
          </div>
        ) : (
          <div className="mt-6 overflow-x-auto">
            <table className="w-full min-w-[760px] text-left">
              <thead>
                <tr className="border-b border-slate-800 text-[10px] uppercase tracking-[0.16em] text-slate-600">
                  <th className="pb-3 font-semibold">Agent</th>
                  <th className="pb-3 font-semibold">Events</th>
                  <th className="pb-3 font-semibold">Blocked</th>
                  <th className="pb-3 font-semibold">Violations</th>
                  <th className="pb-3 font-semibold">Block Rate</th>
                  <th className="pb-3 font-semibold">Risk</th>
                </tr>
              </thead>

              <tbody>
                {metrics.map((metric) => (
                  <tr
                    key={metric.agent_id}
                    className="border-b border-slate-800/70 last:border-0"
                  >
                    <td className="py-4">
                      <span className="text-sm font-medium text-slate-200">
                        Agent #{metric.agent_id}
                      </span>
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

                    <td className="py-4">
                      <span
                        className={`rounded-full border px-2.5 py-1 text-[10px] font-semibold uppercase ${getRiskClass(
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

      {/* Security note */}
      <section className="rounded-2xl border border-cyan-400/10 bg-cyan-400/[0.03] p-5">
        <div className="flex items-start gap-3">
          <ShieldCheck className="mt-0.5 h-5 w-5 shrink-0 text-cyan-300" />

          <div>
            <p className="text-sm font-medium text-slate-200">
              Analytics integrity
            </p>

            <p className="mt-1 text-xs leading-5 text-slate-500">
              Metrics displayed here are sourced directly from the SentinelX
              analytics API. No synthetic security activity is generated for
              empty agent fleets.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}

function MetricCard({
  label,
  value,
  detail,
  icon: Icon,
}: {
  label: string;
  value: number;
  detail: string;
  icon: typeof Activity;
}) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-[#0a0f16] p-5">
      <div className="flex items-center justify-between">
        <span className="text-[10px] font-semibold uppercase tracking-[0.16em] text-slate-500">
          {label}
        </span>

        <div className="rounded-lg border border-cyan-400/10 bg-cyan-400/5 p-2 text-cyan-300">
          <Icon className="h-4 w-4" />
        </div>
      </div>

      <p className="mt-5 text-3xl font-semibold tracking-tight text-white">
        {value}
      </p>

      <p className="mt-1 text-xs text-slate-600">{detail}</p>
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