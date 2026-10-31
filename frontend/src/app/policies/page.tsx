
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
  TriangleAlert,
} from "lucide-react";

import { usePolicies } from "@/features/policies/use-policies";
import type { Policy } from "@/types/api";

export default function PoliciesPage() {
  const { policies, agents, isLoading, isError } = usePolicies();

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

  const enabledPolicyShare =
    policies.length === 0
      ? 0
      : Math.round((enabledPolicies.length / policies.length) * 100);

  const policyDataState = isLoading
    ? "Loading"
    : isError
      ? "Unavailable"
      : "Available";

  return (
    <div className="space-y-5">
      {/* Header */}
      <section className="security-surface relative overflow-hidden p-5 sm:p-6">
        <div className="security-grid pointer-events-none absolute inset-0 opacity-25" />

        <div className="relative">
          <div className="flex flex-wrap items-center gap-2">
            <div className="flex items-center gap-2 text-[10px] font-semibold uppercase tracking-[0.2em] text-indigo-600">
              <FileSliders className="size-3.5" />
              Policy Enforcement
            </div>

            <span className="h-1 w-1 rounded-full bg-slate-200" />

            <span className="font-mono text-[9px] uppercase tracking-[0.16em] text-slate-500">
              Control Plane / Policies
            </span>
          </div>

          <div className="mt-5 flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <h1 className="text-2xl font-semibold tracking-tight text-slate-900 sm:text-3xl">
                Security Policies
              </h1>

              <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">
                Define the runtime decisions that control how SentinelX agents
                respond to sensitive or potentially unsafe actions.
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-2">
              <HeaderSignal
                label="Registered Agents"
                value={isLoading ? "—" : agents.length.toString()}
                icon={ShieldCheck}
                tone="emerald"
              />

              <HeaderSignal
                label="Policy data"
                value={policyDataState}
                icon={SlidersHorizontal}
                tone={
                  isError
                    ? "red"
                    : isLoading
                      ? "amber"
                      : "cyan"
                }
                pulse={false}
              />
            </div>
          </div>
        </div>
      </section>

      {/* Policy posture */}
      <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <PostureCard
          label="Total Policies"
          value={isLoading ? "—" : isError ? "!" : policies.length.toString()}
          detail="Registered enforcement rules"
          icon={FileSliders}
          tone="cyan"
        />

        <PostureCard
          label="Active Rules"
          value={
            isLoading
              ? "—"
              : isError
                ? "!"
                : enabledPolicies.length.toString()
          }
          detail="Enabled for runtime evaluation"
          icon={ShieldCheck}
          tone="emerald"
        />

        <PostureCard
          label="Blocking Rules"
          value={
            isLoading
              ? "—"
              : isError
                ? "!"
                : blockedPolicies.length.toString()
          }
          detail="Hard enforcement controls"
          icon={Ban}
          tone="red"
        />

        <PostureCard
          label="Enabled Policy Share"
          value={isLoading || isError ? "—" : `${enabledPolicyShare}%`}
          detail="Enabled policies / registered policies"
          icon={Gauge}
          tone="cyan"
        />
      </section>

      {/* Enforcement overview */}
      <section className="grid gap-4 xl:grid-cols-[1.35fr_0.65fr]">
        <section className="security-surface p-5">
          <div className="flex items-start justify-between gap-4">
            <div>
              <div className="flex items-center gap-2">
                <SlidersHorizontal className="size-4 text-indigo-600" />

                <h2 className="text-sm font-semibold text-slate-800">
                  Enforcement Posture
                </h2>
              </div>

              <p className="mt-1 text-[10px] text-slate-500">
                  Distribution of configured policy actions
              </p>
            </div>

            <span className="rounded-md border border-slate-200 bg-slate-50 px-2 py-1 font-mono text-[8px] uppercase tracking-[0.12em] text-slate-500">
              Decision Model
            </span>
          </div>

          <div className="mt-6 space-y-5">
            <DistributionRow
              label="BLOCK"
              count={blockedPolicies.length}
              total={policies.length}
              icon={Ban}
              tone="red"
            />

            <DistributionRow
              label="WARN"
              count={warningPolicies.length}
              total={policies.length}
              icon={TriangleAlert}
              tone="amber"
            />

            <DistributionRow
              label="ALLOW"
              count={allowedPolicies.length}
              total={policies.length}
              icon={CheckCircle2}
              tone="emerald"
            />
          </div>
        </section>

        {/* Policy health */}
        <section className="security-surface relative overflow-hidden p-5">
          <div className="pointer-events-none absolute -right-16 -top-16 size-40 rounded-full bg-indigo-400/[0.025] blur-3xl" />

          <div className="relative">
            <div className="flex items-center gap-2">
              <ShieldCheck className="size-4 text-indigo-600" />

              <h2 className="text-sm font-semibold text-slate-800">
                Policy Activation
              </h2>
            </div>

            <p className="mt-1 text-[10px] text-slate-500">
              Share of registered policy records enabled
            </p>

            <div className="mt-6 flex justify-center">
              <div
                className="relative flex size-36 items-center justify-center rounded-full"
                style={{
                  background: `conic-gradient(rgba(99, 102, 241,0.8) ${
                    enabledPolicyShare * 3.6
                  }deg, rgba(255,255,255,0.04) 0deg)`,
                }}
              >
                <div className="flex size-28 flex-col items-center justify-center rounded-full bg-white">
                  <span className="font-mono text-2xl font-semibold text-slate-900">
                    {isLoading || isError ? "—" : `${enabledPolicyShare}%`}
                  </span>

                  <span className="mt-1 text-[8px] uppercase tracking-[0.16em] text-slate-500">
                    Enabled
                  </span>
                </div>
              </div>
            </div>

            <div className="mt-5 text-center">
              <p className="text-[10px] leading-5 text-slate-500">
                Enabled policies divided by all registered policies
              </p>
            </div>
          </div>
        </section>
      </section>

      {/* Registry */}
      <section className="security-surface overflow-hidden">
        <div className="flex flex-col gap-3 border-b border-slate-200 px-5 py-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <div className="flex items-center gap-2">
              <FileSliders className="size-4 text-indigo-600" />

              <h2 className="text-sm font-semibold text-slate-800">
                Policy Registry
              </h2>
            </div>

            <p className="mt-1 text-[10px] text-slate-500">
              Runtime rules currently known to the control plane
            </p>
          </div>

          {!isLoading && !isError && (
            <span className="w-fit rounded-full border border-slate-200 bg-slate-50 px-2.5 py-1 font-mono text-[9px] uppercase tracking-[0.12em] text-slate-500">
              {policies.length} Rules
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

      {/* Operational footer */}
      <section className="grid gap-3 md:grid-cols-3">
        <OperationalSignal
          icon={SlidersHorizontal}
          label="Policy registry"
          value={isLoading ? "Loading" : isError ? "Unavailable" : "Available"}
          detail="Policy configuration retrieval"
          tone={isError ? "red" : "cyan"}
        />

        <OperationalSignal
          icon={ShieldCheck}
          label="Enabled policy share"
          value={isLoading || isError ? "—" : `${enabledPolicyShare}%`}
          detail="Enabled policies / registered policies"
          tone="emerald"
        />

        <OperationalSignal
          icon={Ban}
          label="Hard controls"
          value={isLoading || isError ? "—" : blockedPolicies.length.toString()}
          detail="Blocking rules registered"
          tone="red"
        />
      </section>
    </div>
  );
}

function HeaderSignal({
  label,
  value,
  icon: Icon,
  tone,
  pulse = false,
}: {
  label: string;
  value: string;
  icon: typeof ShieldCheck;
  tone: "cyan" | "emerald" | "amber" | "red";
  pulse?: boolean;
}) {
  const styles = {
    cyan: "border-indigo-400/10 bg-indigo-400/[0.04] text-indigo-600",
    emerald:
      "border-emerald-400/10 bg-emerald-400/[0.04] text-emerald-600",
    amber: "border-amber-400/10 bg-amber-400/[0.04] text-amber-600",
    red: "border-red-400/10 bg-red-400/[0.04] text-red-600",
  }[tone];

  return (
    <div className={`rounded-xl border px-4 py-3 ${styles}`}>
      <div className="text-[8px] uppercase tracking-[0.16em] opacity-60">
        {label}
      </div>

      <div className="mt-1 flex items-center gap-2">
        <Icon className="size-4" />

        <span className="text-[10px] font-semibold uppercase tracking-[0.1em]">
          {value}
        </span>

        {pulse && (
          <span className="size-1.5 animate-pulse rounded-full bg-current" />
        )}
      </div>
    </div>
  );
}

function PostureCard({
  label,
  value,
  detail,
  icon: Icon,
  tone,
}: {
  label: string;
  value: string;
  detail: string;
  icon: typeof FileSliders;
  tone: "cyan" | "emerald" | "red";
}) {
  const styles = {
    cyan: {
      icon: "border-indigo-400/10 bg-indigo-400/[0.05] text-indigo-600",
      value: "text-slate-900",
    },
    emerald: {
      icon: "border-emerald-400/10 bg-emerald-400/[0.05] text-emerald-600",
      value: "text-emerald-600",
    },
    red: {
      icon: "border-red-400/10 bg-red-400/[0.05] text-red-600",
      value: "text-red-600",
    },
  }[tone];

  return (
    <div className="security-surface security-surface-hover p-4">
      <div className="flex items-start justify-between gap-3">
        <span className="text-[9px] font-semibold uppercase tracking-[0.17em] text-slate-500">
          {label}
        </span>

        <div
          className={`flex size-8 shrink-0 items-center justify-center rounded-lg border ${styles.icon}`}
        >
          <Icon className="size-4" />
        </div>
      </div>

      <div
        className={`mt-4 font-mono text-2xl font-semibold tracking-tight ${styles.value}`}
      >
        {value}
      </div>

      <p className="mt-1 text-[10px] text-slate-500">{detail}</p>
    </div>
  );
}

function DistributionRow({
  label,
  count,
  total,
  icon: Icon,
  tone,
}: {
  label: string;
  count: number;
  total: number;
  icon: typeof Ban;
  tone: "red" | "amber" | "emerald";
}) {
  const percentage =
    total === 0 ? 0 : Math.round((count / total) * 100);

  const styles = {
    red: {
      icon: "text-red-600",
      bar: "bg-red-400",
      badge: "border-red-400/10 bg-red-400/[0.05] text-red-600",
    },
    amber: {
      icon: "text-amber-600",
      bar: "bg-amber-400",
      badge: "border-amber-400/10 bg-amber-400/[0.05] text-amber-600",
    },
    emerald: {
      icon: "text-emerald-600",
      bar: "bg-emerald-400",
      badge:
        "border-emerald-400/10 bg-emerald-400/[0.05] text-emerald-600",
    },
  }[tone];

  return (
    <div>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Icon className={`size-3.5 ${styles.icon}`} />

          <span className="text-[10px] font-medium tracking-[0.12em] text-slate-600">
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

      <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-slate-100">
        <div
          className={`h-full rounded-full transition-all duration-500 ${styles.bar}`}
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
      ? "border-red-400/15 bg-red-400/[0.05] text-red-600"
      : action === "WARN"
        ? "border-amber-400/15 bg-amber-400/[0.05] text-amber-600"
        : "border-emerald-400/15 bg-emerald-400/[0.05] text-emerald-600";

  const statusStyles = policy.enabled
    ? "border-emerald-400/10 bg-emerald-400/[0.04] text-emerald-600"
    : "border-slate-200 bg-slate-50 text-slate-500";

  return (
    <article className="group border-l-2 border-l-transparent px-5 py-4 transition-colors hover:border-l-indigo-400/50 hover:bg-white/[0.015]">
      <div className="flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
        <div className="flex min-w-0 items-start gap-3">
          <div
            className={`flex size-9 shrink-0 items-center justify-center rounded-lg border ${
              policy.enabled
                ? "border-indigo-400/10 bg-indigo-400/[0.04]"
                : "border-slate-200 bg-slate-50"
            }`}
          >
            {policy.enabled ? (
              <ShieldCheck className="size-4 text-indigo-600" />
            ) : (
              <ShieldOff className="size-4 text-slate-500" />
            )}
          </div>

          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <h3 className="truncate text-sm font-semibold text-slate-800">
                {policy.name}
              </h3>

              <span
                className={`rounded-full border px-2 py-0.5 text-[8px] font-semibold uppercase tracking-[0.12em] ${actionStyles}`}
              >
                {action}
              </span>

              <span
                className={`rounded-full border px-2 py-0.5 text-[8px] font-semibold uppercase tracking-[0.12em] ${statusStyles}`}
              >
                {policy.enabled ? "Enabled" : "Disabled"}
              </span>
            </div>

            <p className="mt-1 max-w-2xl truncate text-[10px] leading-5 text-slate-500">
              {policy.description || "No policy description provided"}
            </p>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-x-8 gap-y-3 sm:grid-cols-3 xl:min-w-[430px]">
          <PolicyMetadata
            label="Type"
            value={policy.policy_type}
          />

          <PolicyMetadata
            label="Priority"
            value={policy.priority.toString()}
            progress={Math.min(
              100,
              Math.max(5, 100 - policy.priority / 2),
            )}
          />

          <PolicyMetadata
            label="State"
            value={policy.enabled ? "ENABLED" : "DISABLED"}
            accent={policy.enabled ? "emerald" : "slate"}
          />
        </div>
      </div>
    </article>
  );
}

function PolicyMetadata({
  label,
  value,
  progress,
  accent = "default",
}: {
  label: string;
  value: string;
  progress?: number;
  accent?: "default" | "emerald" | "slate";
}) {
  const valueClass =
    accent === "emerald"
      ? "text-emerald-600"
      : accent === "slate"
        ? "text-slate-500"
        : "text-slate-600";

  return (
    <div className="min-w-0">
      <div className="text-[8px] font-medium uppercase tracking-[0.14em] text-slate-400">
        {label}
      </div>

      {progress !== undefined ? (
        <div className="mt-2 flex items-center gap-2">
          <div className="h-1 w-16 overflow-hidden rounded-full bg-slate-100">
            <div
              className="h-full rounded-full bg-indigo-400/70 transition-all duration-500"
              style={{ width: `${progress}%` }}
            />
          </div>

          <span className="font-mono text-[10px] text-slate-600">
            {value}
          </span>
        </div>
      ) : (
        <div className={`mt-1 truncate font-mono text-[10px] ${valueClass}`}>
          {value}
        </div>
      )}
    </div>
  );
}

function OperationalSignal({
  icon: Icon,
  label,
  value,
  detail,
  tone,
}: {
  icon: typeof SlidersHorizontal;
  label: string;
  value: string;
  detail: string;
  tone: "cyan" | "emerald" | "red";
}) {
  const styles = {
    cyan: "border-indigo-400/10 bg-indigo-400/[0.04] text-indigo-600",
    emerald:
      "border-emerald-400/10 bg-emerald-400/[0.04] text-emerald-600",
    red: "border-red-400/10 bg-red-400/[0.04] text-red-600",
  }[tone];

  return (
    <div className="security-surface flex items-center gap-3 p-4">
      <div
        className={`flex size-9 shrink-0 items-center justify-center rounded-lg border ${styles}`}
      >
        <Icon className="size-4" />
      </div>

      <div className="min-w-0">
        <p className="text-[9px] font-semibold uppercase tracking-[0.15em] text-slate-500">
          {label}
        </p>

        <div className="mt-1 flex items-center gap-2">
          <span className="text-xs font-semibold text-slate-800">
            {value}
          </span>

          <span className="truncate text-[9px] text-slate-400">
            {detail}
          </span>
        </div>
      </div>
    </div>
  );
}

function LoadingState() {
  return (
    <div className="flex min-h-72 flex-col items-center justify-center">
      <div className="flex size-10 items-center justify-center rounded-xl border border-indigo-400/10 bg-indigo-400/[0.04]">
        <LoaderCircle className="size-5 animate-spin text-indigo-600" />
      </div>

      <p className="mt-4 text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-500">
        Synchronizing policy registry
      </p>

      <p className="mt-1 text-[10px] text-slate-400">
        Reading current runtime enforcement rules
      </p>
    </div>
  );
}

function ErrorState() {
  return (
    <div className="flex min-h-72 flex-col items-center justify-center px-6 text-center">
      <div className="flex size-11 items-center justify-center rounded-xl border border-red-400/10 bg-red-400/[0.04]">
        <CircleAlert className="size-5 text-red-600" />
      </div>

      <p className="mt-4 text-sm font-medium text-slate-700">
        Policy registry unavailable
      </p>

      <p className="mt-1 max-w-md text-[10px] leading-5 text-slate-500">
        SentinelX could not retrieve the current policy registry. Verify the
        security session and control-plane connection.
      </p>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="relative flex min-h-72 flex-col items-center justify-center overflow-hidden px-6 text-center">
      <div className="security-grid pointer-events-none absolute inset-0 opacity-20" />

      <div className="relative flex size-14 items-center justify-center rounded-2xl border border-indigo-400/10 bg-indigo-400/[0.04]">
        <FileSliders className="size-6 text-indigo-300/70" />
      </div>

      <p className="relative mt-4 text-sm font-semibold text-slate-700">
        No policies configured
      </p>

      <p className="relative mt-1 max-w-sm text-[10px] leading-5 text-slate-500">
        There are currently no runtime security policies associated with the
        available agents.
      </p>

      <div className="relative mt-5 flex items-center gap-2 rounded-full border border-amber-400/10 bg-amber-400/[0.03] px-3 py-1.5">
        <AlertTriangle className="size-3 text-amber-600/70" />

        <span className="font-mono text-[9px] uppercase tracking-[0.14em] text-slate-500">
          Policy coverage unavailable
        </span>
      </div>
    </div>
  );
}
