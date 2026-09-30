"use client";

import type { ReactNode } from "react";
import {
  Activity,
  AlertTriangle,
  Ban,
  CheckCircle2,
  Gauge,
  LockKeyhole,
  LoaderCircle,
  ShieldCheck,
  ShieldOff,
  Zap,
} from "lucide-react";

import { useMyAgents } from "@/features/agents/use-agents";
import {
  useBlockedSecurityEvents,
  useSecurityEvents,
} from "@/features/events/use-security-events";

function MetricCard({
  label,
  value,
  detail,
  icon,
}: {
  label: string;
  value: string | number;
  detail: string;
  icon: ReactNode;
}) {
  return (
    <article className="security-surface security-surface-hover relative overflow-hidden p-5">
      <div className="pointer-events-none absolute -right-8 -top-8 size-24 rounded-full bg-cyan-400/5 blur-2xl" />

      <div className="relative flex items-start justify-between gap-4">
        <div className="min-w-0">
          <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-500">
            {label}
          </p>

          <p className="mt-3 text-3xl font-semibold tracking-tight text-white">
            {value}
          </p>

          <p className="mt-1 text-xs text-slate-500">{detail}</p>
        </div>

        <div className="shrink-0 rounded-xl border border-cyan-400/15 bg-cyan-400/10 p-3 text-cyan-300">
          {icon}
        </div>
      </div>
    </article>
  );
}

function StatusLine({
  label,
  healthy,
}: {
  label: string;
  healthy: boolean;
}) {
  return (
    <div className="flex items-center justify-between rounded-xl border border-slate-800/70 bg-slate-950/40 px-4 py-3">
      <div className="flex min-w-0 items-center gap-3">
        {healthy ? (
          <CheckCircle2 className="size-4 shrink-0 text-emerald-400" />
        ) : (
          <ShieldOff className="size-4 shrink-0 text-red-400" />
        )}

        <span className="truncate text-sm text-slate-300">{label}</span>
      </div>

      <span
        className={`shrink-0 text-[9px] font-semibold uppercase tracking-[0.15em] ${
          healthy ? "text-emerald-300" : "text-red-300"
        }`}
      >
        {healthy ? "Operational" : "Attention"}
      </span>
    </div>
  );
}

function DecisionBadge({ decision }: { decision: string }) {
  const normalized = decision.toUpperCase();

  const blocked = normalized.includes("BLOCK");
  const warning = normalized.includes("WARN");

  const className = blocked
    ? "border-red-400/20 bg-red-400/10 text-red-300"
    : warning
      ? "border-amber-400/20 bg-amber-400/10 text-amber-300"
      : "border-emerald-400/20 bg-emerald-400/10 text-emerald-300";

  return (
    <span
      className={`inline-flex w-fit items-center gap-1.5 rounded-full border px-2.5 py-1 text-[9px] font-semibold uppercase tracking-[0.14em] ${className}`}
    >
      <span
        className={`size-1.5 rounded-full ${
          blocked
            ? "bg-red-400"
            : warning
              ? "bg-amber-400"
              : "bg-emerald-400"
        }`}
      />

      {normalized}
    </span>
  );
}

function PipelineStage({
  number,
  title,
  description,
  icon,
}: {
  number: string;
  title: string;
  description: string;
  icon: ReactNode;
}) {
  return (
    <div className="relative">
      <div className="security-surface-hover h-full rounded-xl p-4">
        <div className="flex items-center justify-between">
          <div className="flex size-9 items-center justify-center rounded-lg border border-cyan-400/15 bg-cyan-400/10 text-cyan-300">
            {icon}
          </div>

          <span className="font-mono text-[9px] text-slate-700">
            {number}
          </span>
        </div>

        <p className="mt-4 text-[9px] font-semibold uppercase tracking-[0.18em] text-slate-500">
          {title}
        </p>

        <p className="mt-1 text-xs leading-5 text-slate-400">
          {description}
        </p>
      </div>
    </div>
  );
}

function LoadingState() {
  return (
    <div className="flex min-h-56 items-center justify-center">
      <div className="flex items-center gap-2 text-sm text-slate-500">
        <LoaderCircle className="size-4 animate-spin text-cyan-400" />
        Loading runtime activity...
      </div>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="flex min-h-56 flex-col items-center justify-center px-6 text-center">
      <div className="flex size-14 items-center justify-center rounded-2xl border border-cyan-400/15 bg-cyan-400/10">
        <Activity className="size-6 text-cyan-300" />
      </div>

      <h3 className="mt-4 font-semibold text-white">
        No runtime decisions yet
      </h3>

      <p className="mt-2 max-w-md text-sm leading-6 text-slate-500">
        Runtime policy decisions will appear here when agents begin submitting
        actions for evaluation.
      </p>
    </div>
  );
}

export default function GuardrailsPage() {
  const {
    data: agents = [],
    isLoading: agentsLoading,
  } = useMyAgents();

  const {
    data: eventsData,
    isLoading: eventsLoading,
  } = useSecurityEvents(1, 6);

  const {
    data: blockedData,
    isLoading: blockedLoading,
  } = useBlockedSecurityEvents();

  const events = eventsData?.items ?? [];
  const blocked = blockedData?.total ?? 0;

  const activeAgents = agents.filter(
    (agent) => agent.status === "ACTIVE",
  ).length;

  const isLoading =
    agentsLoading || eventsLoading || blockedLoading;

  return (
    <div className="space-y-6 sm:space-y-8">
      {/* Header */}
      <section className="relative overflow-hidden rounded-2xl border border-emerald-400/10 bg-emerald-400/[0.025] p-6 sm:p-8">
        <div className="security-grid absolute inset-0 opacity-30" />

        <div className="relative">
          <div className="flex flex-wrap items-center gap-3">
            <span className="inline-flex items-center gap-2 rounded-full border border-emerald-400/20 bg-emerald-400/[0.06] px-3 py-1.5 text-[10px] font-semibold uppercase tracking-[0.18em] text-emerald-300">
              <ShieldCheck className="size-3.5" />
              Runtime Protection
            </span>

            <span className="inline-flex items-center gap-2 text-[10px] font-medium uppercase tracking-[0.16em] text-emerald-400">
              <span className="size-1.5 animate-pulse rounded-full bg-emerald-400" />
              Guardrails online
            </span>
          </div>

          <div className="mt-5 flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <h1 className="text-2xl font-semibold tracking-tight text-white sm:text-3xl">
                Runtime Guardrails
              </h1>

              <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-400">
                Observe the security boundary between AI-agent intent and
                runtime execution. SentinelX evaluates actions before they
                reach protected resources.
              </p>
            </div>

            <div className="flex shrink-0 items-center gap-2 rounded-xl border border-emerald-400/10 bg-emerald-400/[0.035] px-4 py-3">
              <LockKeyhole className="size-4 text-emerald-300" />

              <div>
                <p className="text-[9px] font-semibold uppercase tracking-[0.16em] text-emerald-400">
                  Enforcement state
                </p>

                <p className="mt-0.5 text-xs text-slate-400">
                  Runtime controls active
                </p>
              </div>
            </div>
          </div>

          <div className="mt-7 grid gap-2 sm:grid-cols-3">
            <div className="flex items-center gap-2 rounded-lg border border-slate-800/70 bg-slate-950/30 px-3 py-2.5">
              <Zap className="size-3.5 text-emerald-400" />
              <span className="text-[10px] font-medium uppercase tracking-[0.14em] text-slate-400">
                Evaluate
              </span>
            </div>

            <div className="flex items-center gap-2 rounded-lg border border-slate-800/70 bg-slate-950/30 px-3 py-2.5">
              <LockKeyhole className="size-3.5 text-cyan-400" />
              <span className="text-[10px] font-medium uppercase tracking-[0.14em] text-slate-400">
                Enforce
              </span>
            </div>

            <div className="flex items-center gap-2 rounded-lg border border-slate-800/70 bg-slate-950/30 px-3 py-2.5">
              <Activity className="size-3.5 text-blue-400" />
              <span className="text-[10px] font-medium uppercase tracking-[0.14em] text-slate-400">
                Audit
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* Metrics */}
      <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard
          label="Protected Agents"
          value={isLoading ? "—" : agents.length}
          detail="Agents under control"
          icon={<ShieldCheck className="size-5" />}
        />

        <MetricCard
          label="Active Enforcement"
          value={isLoading ? "—" : activeAgents}
          detail="Currently active agents"
          icon={<Gauge className="size-5" />}
        />

        <MetricCard
          label="Actions Blocked"
          value={isLoading ? "—" : blocked}
          detail="Blocked security events"
          icon={<Ban className="size-5" />}
        />

        <MetricCard
          label="Runtime Events"
          value={isLoading ? "—" : eventsData?.total ?? 0}
          detail="Recorded control decisions"
          icon={<Activity className="size-5" />}
        />
      </section>

      {/* Enforcement pipeline */}
      <section className="grid gap-5 xl:grid-cols-[1.45fr_1fr]">
        <div className="security-surface p-5 sm:p-6">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-cyan-400">
                Decision path
              </p>

              <h2 className="mt-1 text-lg font-semibold text-white">
                Enforcement Pipeline
              </h2>

              <p className="mt-1 text-xs text-slate-500">
                Runtime action security flow
              </p>
            </div>

            <span className="inline-flex w-fit items-center gap-2 rounded-full border border-emerald-400/15 bg-emerald-400/[0.05] px-3 py-1.5 text-[9px] font-semibold uppercase tracking-[0.14em] text-emerald-300">
              <span className="size-1.5 animate-pulse rounded-full bg-emerald-400" />
              Live
            </span>
          </div>

          <div className="mt-6 grid gap-3 sm:grid-cols-2 md:grid-cols-3 xl:grid-cols-5">
            <PipelineStage
              number="01"
              title="Request"
              description="Agent proposes action"
              icon={<Activity className="size-4" />}
            />

            <PipelineStage
              number="02"
              title="Inspect"
              description="Evaluate context"
              icon={<Gauge className="size-4" />}
            />

            <PipelineStage
              number="03"
              title="Policy"
              description="Apply security rules"
              icon={<LockKeyhole className="size-4" />}
            />

            <PipelineStage
              number="04"
              title="Decision"
              description="Allow, warn, or block"
              icon={<ShieldCheck className="size-4" />}
            />

            <PipelineStage
              number="05"
              title="Audit"
              description="Record outcome"
              icon={<Activity className="size-4" />}
            />
          </div>
        </div>

        {/* System status */}
        <div className="security-surface p-5 sm:p-6">
          <div className="flex items-center gap-3">
            <div className="rounded-xl border border-emerald-400/15 bg-emerald-400/10 p-2.5 text-emerald-300">
              <ShieldCheck className="size-5" />
            </div>

            <div>
              <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-emerald-400">
                Control health
              </p>

              <h2 className="mt-1 font-semibold text-white">
                Guardrail Status
              </h2>
            </div>
          </div>

          <div className="mt-6 space-y-2.5">
            <StatusLine label="Policy evaluation" healthy />
            <StatusLine label="Agent authentication" healthy />
            <StatusLine label="Action enforcement" healthy />
            <StatusLine label="Security event audit" healthy />
          </div>

          <div className="mt-5 flex items-start gap-3 rounded-xl border border-emerald-400/10 bg-emerald-400/[0.025] p-4">
            <CheckCircle2 className="mt-0.5 size-4 shrink-0 text-emerald-400" />

            <p className="text-xs leading-5 text-slate-500">
              The runtime protection boundary is operational and ready to
              evaluate agent actions.
            </p>
          </div>
        </div>
      </section>

      {/* Recent decisions */}
      <section className="security-surface overflow-hidden">
        <div className="flex flex-col gap-3 border-b border-slate-800/80 px-5 py-4 sm:flex-row sm:items-center sm:justify-between sm:px-6">
          <div>
            <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-cyan-400">
              Runtime telemetry
            </p>

            <h2 className="mt-1 font-semibold text-white">
              Recent Runtime Decisions
            </h2>

            <p className="mt-1 text-xs text-slate-500">
              Latest actions evaluated by the security control plane
            </p>
          </div>

          <span className="inline-flex w-fit items-center gap-2 rounded-lg border border-slate-800 bg-slate-950/50 px-3 py-1.5 text-[9px] font-semibold uppercase tracking-[0.14em] text-slate-500">
            <span className="size-1.5 rounded-full bg-cyan-400" />
            Live feed
          </span>
        </div>

        {isLoading ? (
          <LoadingState />
        ) : events.length === 0 ? (
          <EmptyState />
        ) : (
          <div className="divide-y divide-slate-800/60">
            {events.map((event) => {
              const decision = event.decision.toUpperCase();
              const isBlocked = decision.includes("BLOCK");
              const isWarn = decision.includes("WARN");

              return (
                <div
                  key={event.id}
                  className="flex flex-col gap-3 px-5 py-4 transition-colors hover:bg-white/[0.015] sm:flex-row sm:items-center sm:justify-between sm:px-6"
                >
                  <div className="flex min-w-0 items-center gap-4">
                    <div
                      className={`flex size-9 shrink-0 items-center justify-center rounded-lg border ${
                        isBlocked
                          ? "border-red-400/15 bg-red-400/10 text-red-300"
                          : isWarn
                            ? "border-amber-400/15 bg-amber-400/10 text-amber-300"
                            : "border-emerald-400/15 bg-emerald-400/10 text-emerald-300"
                      }`}
                    >
                      {isBlocked ? (
                        <Ban className="size-4" />
                      ) : isWarn ? (
                        <AlertTriangle className="size-4" />
                      ) : (
                        <CheckCircle2 className="size-4" />
                      )}
                    </div>

                    <div className="min-w-0">
                      <p className="truncate text-sm font-medium text-white">
                        {event.event_type}
                      </p>

                      <p className="mt-1 truncate text-xs text-slate-500">
                        Agent #{event.agent_id}
                        {event.action ? ` · ${event.action}` : ""}
                      </p>
                    </div>
                  </div>

                  <DecisionBadge decision={decision} />
                </div>
              );
            })}
          </div>
        )}
      </section>

      {/* Enforcement note */}
      <section className="rounded-2xl border border-cyan-400/10 bg-cyan-400/[0.025] p-5">
        <div className="flex items-start gap-3">
          <AlertTriangle className="mt-0.5 size-4 shrink-0 text-cyan-400" />

          <div>
            <p className="text-sm font-medium text-cyan-200">
              Runtime enforcement boundary
            </p>

            <p className="mt-1 text-xs leading-5 text-slate-500">
              SentinelX evaluates agent actions before execution and records
              security decisions for audit and analytics.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}