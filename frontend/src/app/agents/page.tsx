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

  const monitoredAgents = agents.filter(
    (agent) => agent.status !== "SUSPENDED",
  ).length;

  const fleetState = isLoading
    ? "Synchronizing"
    : isError
      ? "Degraded"
      : "Operational";

  return (
    <div className="space-y-5">
      {/* Page header */}
      <section className="security-surface relative overflow-hidden p-5 sm:p-6">
        <div className="security-grid pointer-events-none absolute inset-0 opacity-30" />

        <div className="relative">
          <div className="flex flex-wrap items-center gap-2">
            <div className="flex items-center gap-2 text-[10px] font-semibold uppercase tracking-[0.2em] text-cyan-400">
              <Bot className="size-3.5" />
              Agent Operations
            </div>

            <span className="h-1 w-1 rounded-full bg-slate-700" />

            <span className="font-mono text-[9px] uppercase tracking-[0.16em] text-slate-600">
              Fleet / Runtime
            </span>
          </div>

          <div className="mt-5 flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <h1 className="text-2xl font-semibold tracking-tight text-white sm:text-3xl">
                Agent Fleet
              </h1>

              <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">
                Observe the AI agents connected to SentinelX and their current
                runtime security state.
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
          detail="Currently operational"
          icon={Activity}
          accent="emerald"
        />

        <MetricCard
          label="Monitored"
          value={isLoading ? "—" : isError ? "!" : monitoredAgents.toString()}
          detail="Runtime security coverage"
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
        <div className="flex flex-col gap-3 border-b border-white/[0.06] px-5 py-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <div className="flex items-center gap-2">
              <div className="flex size-7 items-center justify-center rounded-lg border border-cyan-400/10 bg-cyan-400/[0.05]">
                <Wifi className="size-3.5 text-cyan-300" />
              </div>

              <h2 className="text-sm font-semibold text-slate-200">
                Connected Fleet
              </h2>
            </div>

            <p className="mt-1 text-[10px] text-slate-600">
              Live inventory associated with the current security account
            </p>
          </div>

          <div className="flex items-center gap-2">
            <span className="font-mono text-[9px] uppercase tracking-[0.14em] text-slate-600">
              Nodes
            </span>

            <span className="rounded-md border border-white/[0.06] bg-white/[0.025] px-2.5 py-1 font-mono text-[10px] text-slate-400">
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
          label="Runtime protection"
          value="Enabled"
          detail="Security controls active"
          tone="emerald"
        />

        <OperationalSignal
          icon={Clock3}
          label="Fleet synchronization"
          value={isError ? "Unavailable" : "Available"}
          detail={
            isError
              ? "Check security session"
              : "Control plane responding"
          }
          tone={isError ? "red" : "cyan"}
        />

        <OperationalSignal
          icon={CircleCheck}
          label="Policy enforcement"
          value="Ready"
          detail="Runtime decisions enabled"
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
    : state === "Synchronizing"
      ? "amber"
      : "emerald";

  const classes = {
    red: "border-red-400/15 bg-red-400/[0.05] text-red-300",
    amber: "border-amber-400/15 bg-amber-400/[0.05] text-amber-300",
    emerald: "border-emerald-400/15 bg-emerald-400/[0.05] text-emerald-300",
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
      <span className={`size-1.5 rounded-full ${dot} ${
        state === "Operational" ? "animate-pulse" : ""
      }`} />

      <span className="text-[9px] font-semibold uppercase tracking-[0.16em]">
        Fleet {state}
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
      icon: "border-cyan-400/10 bg-cyan-400/[0.05] text-cyan-300",
      value: "text-white",
    },
    emerald: {
      icon: "border-emerald-400/10 bg-emerald-400/[0.05] text-emerald-300",
      value: "text-white",
    },
    amber: {
      icon: "border-amber-400/10 bg-amber-400/[0.05] text-amber-300",
      value: "text-white",
    },
    slate: {
      icon: "border-white/[0.06] bg-white/[0.025] text-slate-400",
      value: "text-white",
    },
  }[accent];

  return (
    <div className="security-surface security-surface-hover p-4">
      <div className="flex items-start justify-between gap-3">
        <span className="text-[9px] font-semibold uppercase tracking-[0.17em] text-slate-600">
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

      <p className="mt-1 text-[10px] text-slate-600">{detail}</p>
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
          <div className="relative flex size-11 shrink-0 items-center justify-center rounded-xl border border-cyan-400/10 bg-cyan-400/[0.04]">
            <Bot className="size-5 text-cyan-300" />

            <span className="absolute -bottom-0.5 -right-0.5 flex size-3.5 items-center justify-center rounded-full border-2 border-[#080b10] bg-emerald-400">
              <span className="size-1 rounded-full bg-[#06100b]" />
            </span>
          </div>

          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <span className="font-mono text-[9px] text-slate-700">
                NODE-{String(index + 1).padStart(2, "0")}
              </span>

              <StatusBadge status={agent.status} />
            </div>

            <h3 className="mt-1 truncate text-sm font-semibold text-slate-200">
              {agent.name}
            </h3>

            <p className="mt-1 max-w-xl truncate text-[10px] text-slate-600">
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
    ? "border-emerald-400/15 bg-emerald-400/[0.06] text-emerald-300"
    : isSuspended
      ? "border-amber-400/15 bg-amber-400/[0.06] text-amber-300"
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
      <div className="flex items-center gap-1.5 text-[8px] font-medium uppercase tracking-[0.14em] text-slate-700">
        <Icon className="size-3" />
        {label}
      </div>

      <div className="mt-1 truncate font-mono text-[10px] text-slate-400">
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
    cyan: "border-cyan-400/10 bg-cyan-400/[0.04] text-cyan-300",
    emerald: "border-emerald-400/10 bg-emerald-400/[0.04] text-emerald-300",
    red: "border-red-400/10 bg-red-400/[0.04] text-red-300",
  }[tone];

  return (
    <div className="security-surface flex items-center gap-3 p-4">
      <div
        className={`flex size-9 shrink-0 items-center justify-center rounded-lg border ${iconStyle}`}
      >
        <Icon className="size-4" />
      </div>

      <div className="min-w-0">
        <p className="text-[9px] font-semibold uppercase tracking-[0.15em] text-slate-600">
          {label}
        </p>

        <div className="mt-1 flex items-center gap-2">
          <span className="text-xs font-semibold text-slate-200">
            {value}
          </span>

          <span className="truncate text-[9px] text-slate-700">
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
      <div className="flex size-10 items-center justify-center rounded-xl border border-cyan-400/10 bg-cyan-400/[0.04]">
        <LoaderCircle className="size-5 animate-spin text-cyan-400" />
      </div>

      <p className="mt-4 text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-500">
        Synchronizing fleet
      </p>

      <p className="mt-1 text-[10px] text-slate-700">
        Reading current control-plane inventory
      </p>
    </div>
  );
}

function AgentsErrorState() {
  return (
    <div className="flex min-h-72 flex-col items-center justify-center px-6 text-center">
      <div className="flex size-11 items-center justify-center rounded-xl border border-red-400/10 bg-red-400/[0.04]">
        <CircleAlert className="size-5 text-red-300" />
      </div>

      <p className="mt-4 text-sm font-medium text-slate-300">
        Fleet synchronization unavailable
      </p>

      <p className="mt-1 max-w-md text-[10px] leading-5 text-slate-600">
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

      <div className="relative flex size-14 items-center justify-center rounded-2xl border border-cyan-400/10 bg-cyan-400/[0.04]">
        <Bot className="size-6 text-cyan-300/70" />
      </div>

      <p className="relative mt-4 text-sm font-semibold text-slate-300">
        No agents registered
      </p>

      <p className="relative mt-1 max-w-sm text-[10px] leading-5 text-slate-600">
        There are currently no AI agents associated with this security
        account. Connected agents will appear here when registered.
      </p>

      <div className="relative mt-5 flex items-center gap-2 rounded-full border border-white/[0.05] bg-white/[0.02] px-3 py-1.5">
        <span className="size-1.5 rounded-full bg-slate-600" />

        <span className="font-mono text-[9px] uppercase tracking-[0.14em] text-slate-600">
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