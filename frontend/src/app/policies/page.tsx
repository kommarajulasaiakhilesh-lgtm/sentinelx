"use client";
import {
  AlertTriangle,
  Ban,
  CheckCircle2,
  CircleAlert,
  FileSliders,
  Gauge,
  LoaderCircle,
  ShieldCheck,
  ShieldOff,
  SlidersHorizontal,
  Sparkles,
  TriangleAlert,
} from "lucide-react";
import { usePolicies } from "@/features/policies/use-policies";
import type { Policy } from "@/types/api";

export default function PoliciesPage() {
  const {
    policies,
    agents,
    isLoading,
    isError,
  } = usePolicies();

  const enabledPolicies = policies.filter((policy) => policy.enabled);
  const blockedPolicies = policies.filter(
    (policy) => policy.action === "BLOCK",
  );
  const warningPolicies = policies.filter(
    (policy) => policy.action === "WARN",
  );
  const allowedPolicies = policies.filter(
    (policy) => policy.action === "ALLOW",
  );

  const protectionRate =
    policies.length === 0
      ? 0
      : Math.round((enabledPolicies.length / policies.length) * 100);

  return (
    <div className="space-y-6">
      {/* Hero */}
      <section className="relative overflow-hidden rounded-2xl border border-white/[0.06] bg-white/[0.02]">
        <div className="security-grid absolute inset-0 opacity-40" />

        <div className="absolute -right-24 -top-24 size-64 rounded-full border border-cyan-400/[0.05]" />
        <div className="absolute -right-12 -top-12 size-40 rounded-full border border-cyan-400/[0.06]" />

        <div className="relative p-6 lg:p-7">
          <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <div className="flex items-center gap-2 text-[10px] font-medium uppercase tracking-[0.2em] text-cyan-400">
               <FileSliders className="size-3.5" />
                Policy Enforcement
              </div>

              <h1 className="mt-2 text-2xl font-semibold tracking-tight text-white">
                Security Policies
              </h1>

              <p className="mt-1 max-w-2xl text-sm leading-6 text-slate-500">
                Define the runtime decisions that control how SentinelX agents
                respond to sensitive or potentially unsafe actions.
              </p>
            </div>

            <div className="flex items-center gap-3">
              <div className="rounded-xl border border-white/[0.06] bg-black/20 px-4 py-3">
                <div className="text-[8px] uppercase tracking-[0.16em] text-slate-600">
                  Protected Agents
                </div>

                <div className="mt-1 flex items-center gap-2">
                  <ShieldCheck className="size-4 text-emerald-300" />

                  <span className="font-mono text-sm text-slate-200">
                    {agents.length}
                  </span>
                </div>
              </div>

              <div className="rounded-xl border border-cyan-400/10 bg-cyan-400/[0.04] px-4 py-3">
                <div className="text-[8px] uppercase tracking-[0.16em] text-slate-600">
                  Enforcement
                </div>

                <div className="mt-1 flex items-center gap-2">
                  <span className="size-1.5 animate-pulse rounded-full bg-cyan-400" />

                  <span className="text-[10px] uppercase tracking-[0.12em] text-cyan-300">
                    Online
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Posture */}
      <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <PostureCard
          label="Total Policies"
          value={isLoading ? "—" : isError ? "!" : policies.length.toString()}
          detail="Registered enforcement rules"
          icon={FileSliders}
        />

        <PostureCard
          label="Active Rules"
          value={
            isLoading ? "—" : isError ? "!" : enabledPolicies.length.toString()
          }
          detail="Currently enforcing"
          icon={ShieldCheck}
          accent="green"
        />

        <PostureCard
          label="Blocking Rules"
          value={
            isLoading ? "—" : isError ? "!" : blockedPolicies.length.toString()
          }
          detail="Hard enforcement controls"
          icon={Ban}
          accent="red"
        />

        <PostureCard
          label="Protection"
          value={isLoading || isError ? "—" : `${protectionRate}%`}
          detail="Policy activation coverage"
          icon={Gauge}
          accent="cyan"
        />
      </section>

      {/* Enforcement distribution */}
      <section className="grid gap-4 xl:grid-cols-[1.4fr_0.6fr]">
        <div className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-5">
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center gap-2">
                <SlidersHorizontal className="size-4 text-cyan-300" />

                <h2 className="text-sm font-medium text-slate-200">
                  Enforcement Posture
                </h2>
              </div>

              <p className="mt-1 text-[10px] text-slate-600">
                Distribution of runtime policy decisions
              </p>
            </div>

            <Sparkles className="size-4 text-slate-700" />
          </div>

          <div className="mt-6 space-y-5">
            <DistributionRow
              label="BLOCK"
              count={blockedPolicies.length}
              total={policies.length}
              icon={Ban}
              type="block"
            />

            <DistributionRow
              label="WARN"
              count={warningPolicies.length}
              total={policies.length}
              icon={TriangleAlert}
              type="warn"
            />

            <DistributionRow
              label="ALLOW"
              count={allowedPolicies.length}
              total={policies.length}
              icon={CheckCircle2}
              type="allow"
            />
          </div>
        </div>

        {/* Protection gauge */}
        <div className="relative overflow-hidden rounded-xl border border-white/[0.06] bg-white/[0.02] p-5">
          <div className="absolute right-0 top-0 size-32 rounded-full bg-cyan-400/[0.025] blur-2xl" />

          <div className="relative">
            <div className="flex items-center gap-2">
              <ShieldCheck className="size-4 text-cyan-300" />

              <h2 className="text-sm font-medium text-slate-200">
                Policy Health
              </h2>
            </div>

            <div className="mt-6 flex items-center justify-center">
              <div
                className="relative flex size-36 items-center justify-center rounded-full"
                style={{
                  background: `conic-gradient(rgba(34,211,238,0.8) ${protectionRate * 3.6}deg, rgba(255,255,255,0.04) 0deg)`,
                }}
              >
                <div className="flex size-28 flex-col items-center justify-center rounded-full bg-[#080b10]">
                  <span className="font-mono text-2xl font-semibold text-white">
                    {isLoading || isError ? "—" : `${protectionRate}%`}
                  </span>

                  <span className="mt-1 text-[8px] uppercase tracking-[0.16em] text-slate-600">
                    Active
                  </span>
                </div>
              </div>
            </div>

            <div className="mt-5 text-center">
              <p className="text-[10px] text-slate-500">
                Enabled policy coverage across the current fleet
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Registry */}
      <section className="overflow-hidden rounded-xl border border-white/[0.06] bg-white/[0.02]">
        <div className="flex items-center justify-between border-b border-white/[0.06] px-5 py-4">
          <div>
            <div className="flex items-center gap-2">
              <ShieldCheck className="size-4 text-cyan-300" />

              <h2 className="text-sm font-medium text-slate-200">
                Policy Registry
              </h2>
            </div>

            <p className="mt-1 text-[10px] text-slate-600">
              Runtime rules currently known to the control plane
            </p>
          </div>

          {!isLoading && !isError && (
            <span className="rounded-full border border-white/[0.06] bg-white/[0.03] px-2.5 py-1 font-mono text-[9px] text-slate-500">
              {policies.length} RULES
            </span>
          )}
        </div>

        {isLoading ? (
          <LoadingState />
        ) : isError ? (
          <ErrorState />
        ) : policies.length === 0 ? (
          <EmptyState />
        ) : (
          <div className="divide-y divide-white/[0.05]">
            {policies.map((policy) => (
              <PolicyRow key={policy.id} policy={policy} />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

function PostureCard({
  label,
  value,
  detail,
  icon: Icon,
  accent = "default",
}: {
  label: string;
  value: string;
  detail: string;
  icon: typeof FileSliders;
  accent?: "default" | "green" | "red" | "cyan";
}) {
  const iconClass = {
    default: "text-slate-300",
    green: "text-emerald-300",
    red: "text-red-300",
    cyan: "text-cyan-300",
  }[accent];

  return (
    <div className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-4">
      <div className="flex items-center justify-between">
        <span className="text-[9px] font-medium uppercase tracking-[0.16em] text-slate-600">
          {label}
        </span>

        <div className="flex size-8 items-center justify-center rounded-lg border border-white/[0.06] bg-white/[0.03]">
          <Icon className={`size-4 ${iconClass}`} />
        </div>
      </div>

      <div className="mt-3 font-mono text-2xl font-semibold tracking-tight text-white">
        {value}
      </div>

      <div className="mt-1 text-[10px] text-slate-600">{detail}</div>
    </div>
  );
}

function DistributionRow({
  label,
  count,
  total,
  icon: Icon,
  type,
}: {
  label: string;
  count: number;
  total: number;
  icon: typeof Ban;
  type: "block" | "warn" | "allow";
}) {
  const percentage = total === 0 ? 0 : Math.round((count / total) * 100);

  const styles = {
    block: {
      icon: "text-red-300",
      bar: "bg-red-400",
      badge: "border-red-400/10 bg-red-400/[0.05] text-red-300",
    },
    warn: {
      icon: "text-amber-300",
      bar: "bg-amber-400",
      badge: "border-amber-400/10 bg-amber-400/[0.05] text-amber-300",
    },
    allow: {
      icon: "text-emerald-300",
      bar: "bg-emerald-400",
      badge:
        "border-emerald-400/10 bg-emerald-400/[0.05] text-emerald-300",
    },
  }[type];

  return (
    <div>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Icon className={`size-3.5 ${styles.icon}`} />

          <span className="text-[10px] font-medium tracking-[0.12em] text-slate-400">
            {label}
          </span>
        </div>

        <div className="flex items-center gap-2">
          <span className="font-mono text-[10px] text-slate-500">
            {count}
          </span>

          <span
            className={`rounded-full border px-2 py-0.5 font-mono text-[8px] ${styles.badge}`}
          >
            {percentage}%
          </span>
        </div>
      </div>

      <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-white/[0.04]">
        <div
          className={`h-full rounded-full transition-all ${styles.bar}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}

function PolicyRow({ policy }: { policy: Policy }) {
  const action = policy.action.toUpperCase();

  const actionStyles =
    action === "BLOCK"
      ? "border-red-400/15 bg-red-400/[0.05] text-red-300"
      : action === "WARN"
        ? "border-amber-400/15 bg-amber-400/[0.05] text-amber-300"
        : "border-emerald-400/15 bg-emerald-400/[0.05] text-emerald-300";

  return (
    <article className="group px-5 py-4 transition-colors hover:bg-white/[0.02]">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div className="flex min-w-0 items-start gap-3">
          <div
            className={`mt-0.5 flex size-9 shrink-0 items-center justify-center rounded-lg border ${
              policy.enabled
                ? "border-cyan-400/10 bg-cyan-400/[0.04]"
                : "border-white/[0.06] bg-white/[0.02]"
            }`}
          >
            {policy.enabled ? (
              <ShieldCheck className="size-4 text-cyan-300" />
            ) : (
              <ShieldOff className="size-4 text-slate-600" />
            )}
          </div>

          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <h3 className="truncate text-sm font-medium text-slate-200">
                {policy.name}
              </h3>

              <span
                className={`rounded-full border px-2 py-0.5 text-[8px] font-medium uppercase tracking-[0.12em] ${actionStyles}`}
              >
                {action}
              </span>

              {policy.enabled ? (
                <span className="text-[8px] uppercase tracking-[0.12em] text-emerald-400">
                  Enabled
                </span>
              ) : (
                <span className="text-[8px] uppercase tracking-[0.12em] text-slate-600">
                  Disabled
                </span>
              )}
            </div>

            <p className="mt-1 max-w-xl truncate text-[10px] text-slate-600">
              {policy.description || "No policy description provided"}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-6">
          <div>
            <div className="text-[8px] uppercase tracking-[0.14em] text-slate-700">
              Type
            </div>

            <div className="mt-1 font-mono text-[10px] text-slate-400">
              {policy.policy_type}
            </div>
          </div>

          <div>
            <div className="text-[8px] uppercase tracking-[0.14em] text-slate-700">
              Priority
            </div>

            <div className="mt-1 flexicon={FileSliders} items-center gap-2">
              <div className="h-1 w-16 overflow-hidden rounded-full bg-white/[0.04]">
                <div
                  className="h-full rounded-full bg-cyan-400/70"
                  style={{
                    width: `${Math.min(
                      100,
                      Math.max(5, 100 - policy.priority / 2),
                    )}%`,
                  }}
                />
              </div>

              <span className="font-mono text-[10px] text-slate-400">
                {policy.priority}
              </span>
            </div>
          </div>
        </div>
      </div>
    </article>
  );
}

function LoadingState() {
  return (
    <div className="flex min-h-64 flex-col items-center justify-center">
      <LoaderCircle className="size-5 animate-spin text-cyan-400" />

      <p className="mt-3 text-[10px] uppercase tracking-[0.16em] text-slate-600">
        Loading policy registry
      </p>
    </div>
  );
}

function ErrorState() {
  return (
    <div className="flex min-h-64 flex-col items-center justify-center px-6 text-center">
      <div className="flex size-10 items-center justify-center rounded-full border border-red-400/10 bg-red-400/[0.05]">
        <CircleAlert className="size-5 text-red-300" />
      </div>

      <p className="mt-3 text-sm font-medium text-slate-300">
        Unable to load policies
      </p>

      <p className="mt-1 max-w-sm text-[10px] leading-5 text-slate-600">
        SentinelX could not retrieve the policy registry. Check the security
        session and backend connection.
      </p>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="flex min-h-64 flex-col items-center justify-center px-6 text-center">
      <div className="flex size-12 items-center justify-center rounded-xl border border-cyan-400/10 bg-cyan-400/[0.04]">
        <FileSliders className="size-6 text-cyan-300/70" />
      </div>

      <p className="mt-4 text-sm font-medium text-slate-300">
        No policies configured
      </p>

      <p className="mt-1 max-w-sm text-[10px] leading-5 text-slate-600">
        There are currently no runtime security policies associated with the
        available agents.
      </p>

      <div className="mt-4 flex items-center gap-2 text-[9px] uppercase tracking-[0.14em] text-slate-700">
        <AlertTriangle className="size-3" />
        Policy coverage unavailable
      </div>
    </div>
  );
}