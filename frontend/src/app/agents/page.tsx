"use client";

import {
  Activity,
  Bot,
  CalendarDays,
  CircleAlert,
  CircleCheck,
  Clock3,
  LoaderCircle,
  ShieldCheck,
  UserRound,
  Wifi,
} from "lucide-react";
import { useMyAgents } from "@/features/agents/use-agents";

export default function AgentsPage() {
  const {
    data: agents = [],
    isLoading,
    isError,
  } = useMyAgents();

  const activeAgents = agents.filter(
    (agent) => agent.status === "ACTIVE",
  ).length;

  const suspendedAgents = agents.filter(
    (agent) => agent.status === "SUSPENDED",
  ).length;

  const notSuspendedAgents = agents.filter(
    (agent) => agent.status !== "SUSPENDED",
  ).length;

  const fleetState = isLoading
    ? "Loading"
    : isError
      ? "Unavailable"
      : "Available";

  return (
    <div className="space-y-5">
      {/* Page header */}
      <section className="security-surface relative overflow-hidden p-5 sm:p-6">
        <div className="security-grid pointer-events-none absolute inset-0 opacity-30" />

        <div className="relative">
          <div className="flex flex-wrap items-center gap-2">
            <div className="flex items-center gap-2 text-[10px] font-semibold uppercase tracking-[0.2em] text-indigo-600">
              <Bot className="size-3.5" />
              Agent Operations
            </div>

            <span className="h-1 w-1 rounded-full bg-slate-200" />

            <span className="font-mono text-[9px] uppercase tracking-[0.16em] text-slate-500">
              Fleet / Runtime
            </span>
          </div>

          <div className="mt-5 flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <h1 className="text-2xl font-semibold tracking-tight text-slate-900 sm:text-3xl">
                Agent Fleet
              </h1>

              <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">
                Review agents registered to SentinelX and their stored status.
              </p>
            </div>

            <FleetIndicator state={fleetState} isError={isError} />
          </div>
        </div>
      </section>

      {/* Fleet metrics */}
      <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard
          label="Registered"
          value={isLoading ? "—" : isError ? "!" : agents.length.toString()}
          detail="Control-plane inventory"
          icon={Bot}
          accent="cyan"
        />

        <MetricCard
          label="Active"
          value={isLoading ? "—" : isError ? "!" : activeAgents.toString()}
          detail="Stored agent status is ACTIVE"
          icon={Activity}
          accent="emerald"
        />

        <MetricCard
          label="Not Suspended"
          value={isLoading ? "—" : isError ? "!" : notSuspendedAgents.toString()}
          detail="Registered agents not suspended"
          icon={ShieldCheck}
          accent="cyan"
        />

        <MetricCard
          label="Suspended"
          value={isLoading ? "—" : isError ? "!" : suspendedAgents.toString()}
          detail={
            suspendedAgents > 0
              ? "Operator attention required"
              : "No suspended agents"
          }
          icon={CircleAlert}
          accent={suspendedAgents > 0 ? "amber" : "slate"}
        />
      </section>

      {/* Fleet panel */}
      <section className="security-surface overflow-hidden">
        <div className="flex flex-col gap-3 border-b border-slate-200 px-5 py-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <div className="flex items-center gap-2">
              <div className="flex size-7 items-center justify-center rounded-lg border border-indigo-400/10 bg-indigo-400/[0.05]">
                <Wifi className="size-3.5 text-indigo-600" />
              </div>

              <h2 className="text-sm font-semibold text-slate-800">
                Registered Agents
              </h2>
            </div>

            <p className="mt-1 text-[10px] text-slate-500">
              Inventory associated with the current security account
            </p>
          </div>

          <div className="flex items-center gap-2">
            <span className="font-mono text-[9px] uppercase tracking-[0.14em] text-slate-500">
              Nodes
            </span>

            <span className="rounded-md border border-slate-200 bg-slate-50 px-2.5 py-1 font-mono text-[10px] text-slate-600">
              {isLoading ? "—" : isError ? "ERR" : agents.length}
            </span>
          </div>
        </div>

        {isLoading ? (
          <AgentsLoadingState />
        ) : isError ? (
          <AgentsErrorState />
        ) : agents.length === 0 ? (
          <AgentsEmptyState />
        ) : (
          <div className="divide-y divide-white/[0.05]">
            {agents.map((agent, index) => (
              <AgentRow
                key={agent.id}
                agent={agent}
                index={index}
              />
            ))}
          </div>
        )}
      </section>

      {/* Operational footer */}
      <section className="grid gap-3 md:grid-cols-3">
        <OperationalSignal
          icon={ShieldCheck}
          label="Runtime policy evaluation"
          value="Available"
          detail="Agent requests can use the enforcement API"
          tone="emerald"
        />

        <OperationalSignal
          icon={Clock3}
          label="Agent inventory"
          value={isError ? "Unavailable" : "Available"}
          detail={
            isError
              ? "Check security session"
              : "Inventory endpoint responded"
          }
          tone={isError ? "red" : "cyan"}
        />

        <OperationalSignal
          icon={CircleCheck}
          label="Policy enforcement"
          value="Policy-based"
          detail="Decisions are returned to authenticated callers"
          tone="emerald"
        />
      </section>
    </div>
  );
}

function FleetIndicator({
  state,
  isError,
}: {
  state: string;
  isError: boolean;
}) {
  const tone = isError
    ? "red"
    : state === "Loading"
      ? "amber"
      : "emerald";

  const classes = {
    red: "border-red-400/15 bg-red-400/[0.05] text-red-600",
    amber: "border-amber-400/15 bg-amber-400/[0.05] text-amber-600",
    emerald: "border-emerald-400/15 bg-emerald-400/[0.05] text-emerald-600",
  }[tone];

  const dot = {
    red: "bg-red-400",
    amber: "bg-amber-400",
    emerald: "bg-emerald-400",
  }[tone];

  return (
    <div
      className={`inline-flex w-fit items-center gap-2 rounded-full border px-3 py-1.5 ${classes}`}
    >
      <span className={`size-1.5 rounded-full ${dot}`} />

      <span className="text-[9px] font-semibold uppercase tracking-[0.16em]">
        Inventory {state}
      </span>
    </div>
  );
}

function MetricCard({
  label,
  value,
  detail,
  icon: Icon,
  accent,
}: {
  label: string;
  value: string;
  detail: string;
  icon: typeof Bot;
  accent: "cyan" | "emerald" | "amber" | "slate";
}) {
  const styles = {
    cyan: {
      icon: "border-indigo-400/10 bg-indigo-400/[0.05] text-indigo-600",
      value: "text-slate-900",
    },
    emerald: {
      icon: "border-emerald-400/10 bg-emerald-400/[0.05] text-emerald-600",
      value: "text-slate-900",
    },
    amber: {
      icon: "border-amber-400/10 bg-amber-400/[0.05] text-amber-600",
      value: "text-slate-900",
    },
    slate: {
      icon: "border-slate-200 bg-slate-50 text-slate-600",
      value: "text-slate-900",
    },
  }[accent];

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

      <div className={`mt-4 text-2xl font-semibold tracking-tight ${styles.value}`}>
        {value}
      </div>

      <p className="mt-1 text-[10px] text-slate-500">{detail}</p>
    </div>
  );
}

function AgentRow({
  agent,
  index,
}: {
  agent: {
    id: number;
    name: string;
    description?: string | null;
    status: string;
    owner_id: number;
    created_at?: string;
  };
  index: number;
}) {
  return (
    <article className="security-surface-hover group relative px-5 py-5 transition-colors">
      <div className="flex flex-col gap-5 xl:flex-row xl:items-center xl:justify-between">
        <div className="flex min-w-0 items-start gap-3">
          <div className="relative flex size-11 shrink-0 items-center justify-center rounded-xl border border-indigo-400/10 bg-indigo-400/[0.04]">
            <Bot className="size-5 text-indigo-600" />

          </div>

          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <span className="font-mono text-[9px] text-slate-400">
                NODE-{String(index + 1).padStart(2, "0")}
              </span>

              <StatusBadge status={agent.status} />
            </div>

            <h3 className="mt-1 truncate text-sm font-semibold text-slate-800">
              {agent.name}
            </h3>

            <p className="mt-1 max-w-xl truncate text-[10px] text-slate-500">
              {agent.description || "No agent description provided"}
            </p>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-x-8 gap-y-3 sm:grid-cols-3 xl:min-w-[460px]">
          <MetadataItem
            icon={Activity}
            label="Agent ID"
            value={`#${agent.id}`}
          />

          <MetadataItem
            icon={UserRound}
            label="Owner"
            value={`#${agent.owner_id}`}
          />

          <MetadataItem
            icon={CalendarDays}
            label="Registered"
            value={formatDate(agent.created_at)}
          />
        </div>
      </div>
    </article>
  );
}

function StatusBadge({ status }: { status: string }) {
  const normalized = status.toUpperCase();

  const isActive = normalized === "ACTIVE";
  const isSuspended = normalized === "SUSPENDED";

  const style = isActive
    ? "border-emerald-400/15 bg-emerald-400/[0.06] text-emerald-600"
    : isSuspended
      ? "border-amber-400/15 bg-amber-400/[0.06] text-amber-600"
      : "border-slate-400/10 bg-slate-400/[0.04] text-slate-500";

  const dot = isActive
    ? "bg-emerald-400"
    : isSuspended
      ? "bg-amber-400"
      : "bg-slate-500";

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-2 py-0.5 text-[8px] font-semibold uppercase tracking-[0.12em] ${style}`}
    >
      <span className={`size-1.5 rounded-full ${dot}`} />
      {status}
    </span>
  );
}

function MetadataItem({
  icon: Icon,
  label,
  value,
}: {
  icon: typeof Activity;
  label: string;
  value: string;
}) {
  return (
    <div className="min-w-0">
      <div className="flex items-center gap-1.5 text-[8px] font-medium uppercase tracking-[0.14em] text-slate-400">
        <Icon className="size-3" />
        {label}
      </div>

      <div className="mt-1 truncate font-mono text-[10px] text-slate-600">
        {value}
      </div>
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
  icon: typeof ShieldCheck;
  label: string;
  value: string;
  detail: string;
  tone: "cyan" | "emerald" | "red";
}) {
  const iconStyle = {
    cyan: "border-indigo-400/10 bg-indigo-400/[0.04] text-indigo-600",
    emerald: "border-emerald-400/10 bg-emerald-400/[0.04] text-emerald-600",
    red: "border-red-400/10 bg-red-400/[0.04] text-red-600",
  }[tone];

  return (
    <div className="security-surface flex items-center gap-3 p-4">
      <div
        className={`flex size-9 shrink-0 items-center justify-center rounded-lg border ${iconStyle}`}
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

function AgentsLoadingState() {
  return (
    <div className="flex min-h-72 flex-col items-center justify-center">
      <div className="flex size-10 items-center justify-center rounded-xl border border-indigo-400/10 bg-indigo-400/[0.04]">
        <LoaderCircle className="size-5 animate-spin text-indigo-600" />
      </div>

      <p className="mt-4 text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-500">
        Synchronizing fleet
      </p>

      <p className="mt-1 text-[10px] text-slate-400">
        Reading current control-plane inventory
      </p>
    </div>
  );
}

function AgentsErrorState() {
  return (
    <div className="flex min-h-72 flex-col items-center justify-center px-6 text-center">
      <div className="flex size-11 items-center justify-center rounded-xl border border-red-400/10 bg-red-400/[0.04]">
        <CircleAlert className="size-5 text-red-600" />
      </div>

      <p className="mt-4 text-sm font-medium text-slate-700">
        Fleet synchronization unavailable
      </p>

      <p className="mt-1 max-w-md text-[10px] leading-5 text-slate-500">
        SentinelX could not retrieve the registered agent fleet. Verify the
        security session and control-plane connection.
      </p>
    </div>
  );
}

function AgentsEmptyState() {
  return (
    <div className="relative flex min-h-72 flex-col items-center justify-center overflow-hidden px-6 text-center">
      <div className="security-grid pointer-events-none absolute inset-0 opacity-20" />

      <div className="relative flex size-14 items-center justify-center rounded-2xl border border-indigo-400/10 bg-indigo-400/[0.04]">
        <Bot className="size-6 text-indigo-300/70" />
      </div>

      <p className="relative mt-4 text-sm font-semibold text-slate-700">
        No agents registered
      </p>

      <p className="relative mt-1 max-w-sm text-[10px] leading-5 text-slate-500">
        There are currently no AI agents associated with this security
        account. Connected agents will appear here when registered.
      </p>

      <div className="relative mt-5 flex items-center gap-2 rounded-full border border-slate-200 bg-slate-50 px-3 py-1.5">
        <span className="size-1.5 rounded-full bg-slate-600" />

        <span className="font-mono text-[9px] uppercase tracking-[0.14em] text-slate-500">
          Fleet awaiting nodes
        </span>
      </div>
    </div>
  );
}

function formatDate(value?: string) {
  if (!value) {
    return "—";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "—";
  }

  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}
