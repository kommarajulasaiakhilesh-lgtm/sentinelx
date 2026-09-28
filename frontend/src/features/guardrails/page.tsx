"use client";

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
  icon: Icon,
}: {
  label: string;
  value: string | number;
  detail: string;
  icon: typeof ShieldCheck;
}) {
  return (
    <div className="relative overflow-hidden rounded-2xl border border-white/10 bg-white/[0.035] p-5">
      <div className="absolute -right-8 -top-8 h-24 w-24 rounded-full bg-cyan-400/5 blur-2xl" />

      <div className="relative flex items-start justify-between">
        <div>
          <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-500">
            {label}
          </p>

          <p className="mt-3 text-3xl font-semibold text-white">
            {value}
          </p>

          <p className="mt-1 text-xs text-slate-500">
            {detail}
          </p>
        </div>

        <div className="rounded-xl border border-cyan-400/15 bg-cyan-400/10 p-3 text-cyan-300">
          <Icon className="h-5 w-5" />
        </div>
      </div>
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
    <div className="space-y-8">
      {/* HERO */}
      <section className="relative overflow-hidden rounded-3xl border border-emerald-400/10 bg-gradient-to-br from-emerald-400/[0.08] via-transparent to-cyan-500/[0.05] p-6 sm:p-8">
        <div className="absolute -right-20 -top-24 h-72 w-72 rounded-full bg-emerald-400/10 blur-3xl" />
        <div className="absolute bottom-0 left-1/3 h-40 w-64 rounded-full bg-cyan-400/5 blur-3xl" />

        <div className="relative">
          <div className="flex flex-wrap items-center gap-3">
            <div className="flex items-center gap-2 rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3 py-1.5 text-xs font-medium text-emerald-300">
              <ShieldCheck className="h-3.5 w-3.5" />
              Runtime Protection
            </div>

            <div className="flex items-center gap-2 text-xs text-emerald-400">
              <span className="h-2 w-2 animate-pulse rounded-full bg-emerald-400" />
              Guardrails online
            </div>
          </div>

          <h1 className="mt-5 text-3xl font-semibold tracking-tight text-white sm:text-4xl">
            Runtime Guardrails
          </h1>

          <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-400">
            Observe the security boundary between AI-agent intent and
            runtime execution. SentinelX evaluates actions before they
            reach protected resources.
          </p>

          <div className="mt-6 flex flex-wrap items-center gap-4 text-xs text-slate-500">
            <span className="flex items-center gap-2">
              <Zap className="h-4 w-4 text-emerald-400" />
              Evaluate
            </span>

            <span className="text-slate-700">→</span>

            <span className="flex items-center gap-2">
              <LockKeyhole className="h-4 w-4 text-cyan-400" />
              Enforce
            </span>

            <span className="text-slate-700">→</span>

            <span className="flex items-center gap-2">
              <Activity className="h-4 w-4 text-blue-400" />
              Audit
            </span>
          </div>
        </div>
      </section>

      {/* METRICS */}
      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard
          label="Protected Agents"
          value={isLoading ? "—" : agents.length}
          detail="Agents under control"
          icon={ShieldCheck}
        />

        <MetricCard
          label="Active Enforcement"
          value={isLoading ? "—" : activeAgents}
          detail="Currently active agents"
          icon={Gauge}
        />

        <MetricCard
          label="Actions Blocked"
          value={isLoading ? "—" : blocked}
          detail="Blocked security events"
          icon={Ban}
        />

        <MetricCard
          label="Runtime Events"
          value={
            isLoading
              ? "—"
              : eventsData?.total ?? 0
          }
          detail="Recorded control decisions"
          icon={Activity}
        />
      </section>

      {/* ENFORCEMENT PIPELINE */}
      <section className="grid gap-6 xl:grid-cols-[1.45fr_1fr]">
        <div className="rounded-2xl border border-white/10 bg-white/[0.025] p-5">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="font-semibold text-white">
                Enforcement Pipeline
              </h2>

              <p className="mt-1 text-xs text-slate-500">
                Runtime action security flow
              </p>
            </div>

            <div className="flex items-center gap-2 rounded-full border border-emerald-400/15 bg-emerald-400/5 px-3 py-1.5 text-[10px] font-semibold tracking-[0.14em] text-emerald-300">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
              LIVE
            </div>
          </div>

          <div className="mt-8 grid gap-3 md:grid-cols-5">
            {[
              {
                title: "REQUEST",
                icon: Activity,
                text: "Agent proposes action",
              },
              {
                title: "INSPECT",
                icon: Gauge,
                text: "Evaluate context",
              },
              {
                title: "POLICY",
                icon: LockKeyhole,
                text: "Apply security rules",
              },
              {
                title: "DECISION",
                icon: ShieldCheck,
                text: "Allow / warn / block",
              },
              {
                title: "AUDIT",
                icon: Activity,
                text: "Record outcome",
              },
            ].map((stage, index) => {
              const Icon = stage.icon;

              return (
                <div key={stage.title} className="relative">
                  <div className="rounded-xl border border-white/10 bg-black/20 p-4">
                    <div className="flex h-9 w-9 items-center justify-center rounded-lg border border-cyan-400/15 bg-cyan-400/10 text-cyan-300">
                      <Icon className="h-4 w-4" />
                    </div>

                    <p className="mt-4 text-[9px] font-semibold tracking-[0.18em] text-slate-500">
                      {stage.title}
                    </p>

                    <p className="mt-1 text-xs leading-5 text-slate-400">
                      {stage.text}
                    </p>
                  </div>

                  {index < 4 && (
                    <div className="absolute -right-3 top-1/2 z-10 hidden text-slate-700 md:block">
                      →
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* SYSTEM STATUS */}
        <div className="rounded-2xl border border-white/10 bg-white/[0.025] p-5">
          <div className="flex items-center gap-3">
            <div className="rounded-xl border border-emerald-400/15 bg-emerald-400/10 p-2.5 text-emerald-300">
              <ShieldCheck className="h-5 w-5" />
            </div>

            <div>
              <h2 className="font-semibold text-white">
                Guardrail Status
              </h2>

              <p className="text-xs text-slate-500">
                Control-plane protection state
              </p>
            </div>
          </div>

          <div className="mt-6 space-y-3">
            {[
              ["Policy evaluation", true],
              ["Agent authentication", true],
              ["Action enforcement", true],
              ["Security event audit", true],
            ].map(([label, healthy]) => (
              <div
                key={String(label)}
                className="flex items-center justify-between rounded-xl border border-white/5 bg-black/20 px-4 py-3"
              >
                <div className="flex items-center gap-3">
                  {healthy ? (
                    <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                  ) : (
                    <ShieldOff className="h-4 w-4 text-red-400" />
                  )}

                  <span className="text-sm text-slate-300">
                    {label}
                  </span>
                </div>

                <span className="text-[9px] font-semibold tracking-[0.15em] text-emerald-300">
                  OPERATIONAL
                </span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* RECENT DECISIONS */}
      <section className="overflow-hidden rounded-2xl border border-white/10 bg-white/[0.025]">
        <div className="flex items-center justify-between border-b border-white/10 px-5 py-4">
          <div>
            <h2 className="font-semibold text-white">
              Recent Runtime Decisions
            </h2>

            <p className="mt-1 text-xs text-slate-500">
              Latest actions evaluated by the security control plane
            </p>
          </div>

          <div className="rounded-lg border border-white/10 px-3 py-1.5 text-[10px] font-semibold tracking-[0.14em] text-slate-500">
            LIVE FEED
          </div>
        </div>

        {isLoading ? (
          <div className="flex min-h-56 items-center justify-center">
            <div className="flex items-center gap-2 text-sm text-slate-500">
              <LoaderCircle className="h-4 w-4 animate-spin" />
              Loading runtime activity...
            </div>
          </div>
        ) : events.length === 0 ? (
          <div className="flex min-h-56 items-center justify-center px-6 text-center">
            <div>
              <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl border border-cyan-400/15 bg-cyan-400/10">
                <Activity className="h-6 w-6 text-cyan-300" />
              </div>

              <h3 className="mt-4 font-semibold text-white">
                No runtime decisions yet
              </h3>

              <p className="mt-2 max-w-md text-sm leading-6 text-slate-500">
                Runtime policy decisions will appear here when agents
                begin submitting actions for evaluation.
              </p>
            </div>
          </div>
        ) : (
          <div className="divide-y divide-white/5">
            {events.map((event) => {
              const decision =
                event.decision.toUpperCase();

              const isBlocked = decision.includes("BLOCK");
              const isWarn = decision.includes("WARN");

              return (
                <div
                  key={event.id}
                  className="flex flex-col gap-3 px-5 py-4 sm:flex-row sm:items-center sm:justify-between"
                >
                  <div className="flex items-center gap-4">
                    <div
                      className={`flex h-9 w-9 items-center justify-center rounded-lg border ${
                        isBlocked
                          ? "border-red-400/15 bg-red-400/10 text-red-300"
                          : isWarn
                            ? "border-amber-400/15 bg-amber-400/10 text-amber-300"
                            : "border-emerald-400/15 bg-emerald-400/10 text-emerald-300"
                      }`}
                    >
                      {isBlocked ? (
                        <Ban className="h-4 w-4" />
                      ) : isWarn ? (
                        <AlertTriangle className="h-4 w-4" />
                      ) : (
                        <CheckCircle2 className="h-4 w-4" />
                      )}
                    </div>

                    <div>
                      <p className="text-sm font-medium text-white">
                        {event.event_type}
                      </p>

                      <p className="mt-1 text-xs text-slate-500">
                        Agent #{event.agent_id}
                        {event.action
                          ? ` · ${event.action}`
                          : ""}
                      </p>
                    </div>
                  </div>

                  <span
                    className={`w-fit rounded-full border px-2.5 py-1 text-[9px] font-semibold tracking-[0.14em] ${
                      isBlocked
                        ? "border-red-400/20 bg-red-400/10 text-red-300"
                        : isWarn
                          ? "border-amber-400/20 bg-amber-400/10 text-amber-300"
                          : "border-emerald-400/20 bg-emerald-400/10 text-emerald-300"
                    }`}
                  >
                    {decision}
                  </span>
                </div>
              );
            })}
          </div>
        )}
      </section>

      {/* BOTTOM SECURITY NOTE */}
      <div className="flex items-start gap-3 rounded-2xl border border-cyan-400/10 bg-cyan-400/[0.025] p-5">
        <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-cyan-400" />

        <div>
          <p className="text-sm font-medium text-cyan-200">
            Runtime enforcement boundary
          </p>

          <p className="mt-1 text-xs leading-5 text-slate-500">
            SentinelX evaluates agent actions before execution and
            records security decisions for audit and analytics.
          </p>
        </div>
      </div>
    </div>
  );
}