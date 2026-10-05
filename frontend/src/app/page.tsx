"use client";

import {
  Activity,
  ArrowUpRight,
  Bot,
  CalendarDays,
  CircleAlert,
  Cpu,
  LoaderCircle,
  Network,
  ShieldCheck,
  UserRound,
} from "lucide-react";


import { useMyAgents } from "@/features/agents/use-agents";
import { useSecurityEventStream } from "@/features/security-events/use-security-event-stream";

export default function CommandCenterPage() {
    const { status: streamStatus } = useSecurityEventStream();
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

  const monitoredAgents = agents.length - suspendedAgents;

  return (
    <div className="space-y-6">
      {/* Command Center Header */}
      <section className="security-surface relative overflow-hidden">
        <div className="security-grid absolute inset-0 opacity-30" />

        <div className="relative">
          <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <div className="flex items-center gap-2 text-[10px] font-semibold uppercase tracking-[0.22em] text-cyan-400">
                <Network className="size-3.5" />
                Security Operations
              </div>

              <h1 className="mt-2 text-3xl font-semibold tracking-tight text-white sm:text-4xl">
                Command Center
              </h1>

              <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">
                Monitor the SentinelX security control plane, connected agents,
                and runtime protection posture from a single operational view.
              </p>
            </div>

            <div className="flex shrink-0 items-center gap-2 self-start rounded-full border border-emerald-400/10 bg-emerald-400/[0.05] px-3 py-1.5 lg:self-auto">
              <span className="relative flex size-1.5">
                <span className="absolute inline-flex size-full animate-ping rounded-full bg-emerald-400 opacity-40" />
                <span className="relative inline-flex size-1.5 rounded-full bg-emerald-400" />
              </span>

              <span
  className={`text-[9px] font-medium uppercase tracking-[0.16em] ${
    streamStatus === "CONNECTED"
      ? "text-emerald-300"
      : streamStatus === "CONNECTING"
        ? "text-amber-300"
        : "text-rose-300"
  }`}
>
  {streamStatus === "CONNECTED"
    ? "Control link connected"
    : streamStatus === "CONNECTING"
      ? "Control link connecting"
      : "Control link disconnected"}
</span>
            </div>
          </div>

          <div className="mt-6 flex flex-wrap items-center gap-x-5 gap-y-2 border-t border-white/[0.05] pt-4">
            <SystemSignal
              label="Runtime"
              value="Protected"
              status="healthy"
            />

            <SystemSignal
              label="Fleet"
              value={isLoading ? "Syncing" : isError ? "Degraded" : "Monitored"}
              status={isError ? "warning" : "healthy"}
            />

            <SystemSignal
              label="Security mode"
              value="Enforced"
              status="healthy"
            />
          </div>
        </div>
      </section>

      {/* Security Signal Rail */}
      <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard
          label="Registered Agents"
          value={isLoading ? "—" : isError ? "!" : agents.length.toString()}
          detail={isError ? "Unable to synchronize fleet" : "Connected to control plane"}
          icon={Bot}
        />

        <MetricCard
          label="Active Agents"
          value={isLoading ? "—" : isError ? "!" : activeAgents.toString()}
          detail={isError ? "Fleet data unavailable" : "Currently active"}
          icon={Activity}
          accent="emerald"
        />

        <MetricCard
          label="Monitored"
          value={isLoading ? "—" : isError ? "!" : monitoredAgents.toString()}
          detail="Under runtime security monitoring"
          icon={ShieldCheck}
          accent="cyan"
        />

        <MetricCard
          label="Suspended"
          value={isLoading ? "—" : isError ? "!" : suspendedAgents.toString()}
          detail="Require operator attention"
          icon={CircleAlert}
          accent={suspendedAgents > 0 ? "amber" : "slate"}
        />
      </section>

      {/* Operational Overview */}
      <section className="grid gap-4 xl:grid-cols-[minmax(0,1.6fr)_minmax(300px,0.7fr)]">
        <div className="security-surface overflow-hidden">
          <div className="flex flex-col gap-3 border-b border-white/[0.05] px-5 py-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <div className="flex items-center gap-2">
                <Cpu className="size-4 text-cyan-300" />

                <h2 className="text-sm font-semibold text-slate-200">
                  Agent Fleet
                </h2>
              </div>

              <p className="mt-1 text-[10px] text-slate-600">
                Live agent inventory connected to the current security account
              </p>
            </div>

            {!isLoading && !isError && (
              <div className="flex items-center gap-2">
                <span className="rounded-full border border-white/[0.06] bg-white/[0.025] px-2.5 py-1 font-mono text-[9px] text-slate-500">
                  {agents.length.toString().padStart(2, "0")} NODES
                </span>

                <span className="flex items-center gap-1.5 rounded-full border border-emerald-400/10 bg-emerald-400/[0.04] px-2.5 py-1 text-[9px] uppercase tracking-[0.12em] text-emerald-300">
                  <span className="size-1.5 rounded-full bg-emerald-400" />
                  Live
                </span>
              </div>
            )}
          </div>

          {isLoading ? (
            <FleetLoadingState />
          ) : isError ? (
            <FleetErrorState />
          ) : agents.length === 0 ? (
            <FleetEmptyState />
          ) : (
            <div className="divide-y divide-white/[0.04]">
              {agents.map((agent) => (
                <AgentRow key={agent.id} agent={agent} />
              ))}
            </div>
          )}
        </div>

        {/* Security Posture */}
        <div className="security-surface overflow-hidden">
          <div className="border-b border-white/[0.05] px-5 py-4">
            <div className="flex items-center gap-2">
              <ShieldCheck className="size-4 text-emerald-300" />

              <h2 className="text-sm font-semibold text-slate-200">
                Security Posture
              </h2>
            </div>

            <p className="mt-1 text-[10px] text-slate-600">
              Current control-plane operating state
            </p>
          </div>

          <div className="p-5">
            <div className="relative overflow-hidden rounded-xl border border-emerald-400/10 bg-emerald-400/[0.035] p-4">
              <div className="absolute right-0 top-0 size-24 translate-x-8 -translate-y-8 rounded-full bg-emerald-400/[0.05] blur-2xl" />

              <div className="relative">
                <div className="flex items-center justify-between">
                  <span className="text-[9px] font-semibold uppercase tracking-[0.18em] text-emerald-300">
                    Operational
                  </span>

                  <ShieldCheck className="size-5 text-emerald-300/70" />
                </div>

                <p className="mt-4 text-xl font-semibold tracking-tight text-white">
                  Security controls active
                </p>

                <p className="mt-2 text-[11px] leading-5 text-slate-500">
                  SentinelX is monitoring the connected agent fleet and
                  enforcing the configured security control plane.
                </p>
              </div>
            </div>

            <div className="mt-4 space-y-1">
              <PostureRow
                label="Agent monitoring"
                value={isError ? "Degraded" : "Active"}
                warning={isError}
              />

              <PostureRow
                label="Runtime protection"
                value="Enabled"
              />

              <PostureRow
                label="Policy enforcement"
                value="Ready"
              />

              <PostureRow
                label="Security telemetry"
                value="Available"
              />
            </div>
          </div>
        </div>
      </section>

      {/* Operations Timeline */}
      <section className="security-surface overflow-hidden">
        <div className="flex items-center justify-between border-b border-white/[0.05] px-5 py-4">
          <div>
            <div className="flex items-center gap-2">
              <Activity className="size-4 text-cyan-300" />

              <h2 className="text-sm font-semibold text-slate-200">
                Operations Overview
              </h2>
            </div>

            <p className="mt-1 text-[10px] text-slate-600">
              Command-center signals prepared for live security telemetry
            </p>
          </div>

          <span className="hidden items-center gap-1.5 text-[9px] uppercase tracking-[0.14em] text-slate-600 sm:flex">
            <span className="size-1.5 rounded-full bg-slate-600" />
            Awaiting events
          </span>
        </div>

        <div className="grid gap-px bg-white/[0.04] sm:grid-cols-3">
          <OverviewTile
            label="Security Events"
            value="Ready"
            detail="Event stream available"
            href="/events"
          />

          <OverviewTile
            label="Alerts & Incidents"
            value="Ready"
            detail="Incident response console"
            href="/alerts"
          />

          <OverviewTile
            label="Analytics"
            value="Ready"
            detail="Security intelligence"
            href="/analytics"
          />
        </div>
      </section>
    </div>
  );
}

function SystemSignal({
  label,
  value,
  status,
}: {
  label: string;
  value: string;
  status: "healthy" | "warning";
}) {
  return (
    <div className="flex items-center gap-2">
      <span
        className={`size-1.5 rounded-full ${
          status === "healthy" ? "bg-emerald-400" : "bg-amber-400"
        }`}
      />

      <span className="text-[9px] uppercase tracking-[0.14em] text-slate-600">
        {label}
      </span>

      <span
        className={`text-[10px] font-medium ${
          status === "healthy" ? "text-slate-300" : "text-amber-300"
        }`}
      >
        {value}
      </span>
    </div>
  );
}

function MetricCard({
  label,
  value,
  detail,
  icon: Icon,
  accent = "cyan",
}: {
  label: string;
  value: string;
  detail: string;
  icon: typeof Bot;
  accent?: "cyan" | "emerald" | "amber" | "slate";
}) {
  const accentClasses = {
    cyan: {
      border: "border-cyan-400/10",
      background: "bg-cyan-400/[0.045]",
      icon: "text-cyan-300",
    },
    emerald: {
      border: "border-emerald-400/10",
      background: "bg-emerald-400/[0.04]",
      icon: "text-emerald-300",
    },
    amber: {
      border: "border-amber-400/10",
      background: "bg-amber-400/[0.04]",
      icon: "text-amber-300",
    },
    slate: {
      border: "border-white/[0.06]",
      background: "bg-white/[0.025]",
      icon: "text-slate-400",
    },
  };

  const colors = accentClasses[accent];

  return (
    <div className="security-surface security-surface-hover p-4">
      <div className="flex items-center justify-between">
        <span className="text-[9px] font-semibold uppercase tracking-[0.16em] text-slate-600">
          {label}
        </span>

        <div
          className={`flex size-8 items-center justify-center rounded-lg border ${colors.border} ${colors.background}`}
        >
          <Icon className={`size-4 ${colors.icon}`} />
        </div>
      </div>

      <div className="mt-3 text-2xl font-semibold tracking-tight text-white">
        {value}
      </div>

      <div className="mt-1 text-[10px] text-slate-600">{detail}</div>
    </div>
  );
}

function AgentRow({
  agent,
}: {
  agent: {
    id: number;
    name: string;
    description?: string | null;
    status: string;
    owner_id: number;
    created_at?: string;
  };
}) {
  return (
    <article className="group px-5 py-4 transition-colors duration-200 hover:bg-white/[0.018]">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div className="flex min-w-0 items-start gap-3">
          <div className="relative flex size-10 shrink-0 items-center justify-center rounded-lg border border-cyan-400/10 bg-cyan-400/[0.04]">
            <Bot className="size-5 text-cyan-300" />

            {agent.status.toUpperCase() === "ACTIVE" && (
              <span className="absolute -right-0.5 -top-0.5 size-2 rounded-full border-2 border-[#0b1017] bg-emerald-400" />
            )}
          </div>

          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <h3 className="truncate text-sm font-medium text-slate-200">
                {agent.name}
              </h3>

              <StatusBadge status={agent.status} />
            </div>

            <p className="mt-1 truncate text-[10px] text-slate-600">
              {agent.description || "No description provided"}
            </p>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-x-8 gap-y-2 sm:grid-cols-3 lg:min-w-[440px] lg:grid-cols-3">
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
            label="Created"
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

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-2 py-0.5 text-[8px] font-medium uppercase tracking-[0.12em] ${
        isActive
          ? "border-emerald-400/15 bg-emerald-400/[0.06] text-emerald-300"
          : isSuspended
            ? "border-amber-400/15 bg-amber-400/[0.06] text-amber-300"
            : "border-slate-400/10 bg-slate-400/[0.04] text-slate-500"
      }`}
    >
      <span
        className={`size-1.5 rounded-full ${
          isActive
            ? "bg-emerald-400"
            : isSuspended
              ? "bg-amber-400"
              : "bg-slate-500"
        }`}
      />

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
    <div>
      <div className="flex items-center gap-1.5 text-[8px] uppercase tracking-[0.14em] text-slate-700">
        <Icon className="size-3" />
        {label}
      </div>

      <div className="mt-1 truncate font-mono text-[10px] text-slate-400">
        {value}
      </div>
    </div>
  );
}

function PostureRow({
  label,
  value,
  warning = false,
}: {
  label: string;
  value: string;
  warning?: boolean;
}) {
  return (
    <div className="flex items-center justify-between border-b border-white/[0.035] py-2.5 last:border-0">
      <span className="text-[10px] text-slate-600">{label}</span>

      <span
        className={`text-[9px] font-medium uppercase tracking-[0.1em] ${
          warning ? "text-amber-300" : "text-slate-400"
        }`}
      >
        {value}
      </span>
    </div>
  );
}

function OverviewTile({
  label,
  value,
  detail,
  href,
}: {
  label: string;
  value: string;
  detail: string;
  href: string;
}) {
  return (
    <a
      href={href}
      className="group bg-[#0b1017] p-5 transition-colors duration-200 hover:bg-[#101722] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-400/50"
    >
      <div className="flex items-center justify-between">
        <span className="text-[9px] font-semibold uppercase tracking-[0.16em] text-slate-600">
          {label}
        </span>

        <ArrowUpRight className="size-3.5 text-slate-700 transition-transform duration-200 group-hover:-translate-y-0.5 group-hover:translate-x-0.5 group-hover:text-cyan-300" />
      </div>

      <div className="mt-4 text-sm font-medium text-slate-300">{value}</div>

      <p className="mt-1 text-[10px] text-slate-600">{detail}</p>
    </a>
  );
}

function FleetLoadingState() {
  return (
    <div className="flex min-h-64 flex-col items-center justify-center">
      <LoaderCircle className="size-5 animate-spin text-cyan-400" />

      <p className="mt-3 text-[10px] uppercase tracking-[0.16em] text-slate-600">
        Synchronizing agent fleet
      </p>
    </div>
  );
}

function FleetErrorState() {
  return (
    <div className="flex min-h-64 flex-col items-center justify-center px-6 text-center">
      <div className="flex size-10 items-center justify-center rounded-full border border-red-400/10 bg-red-400/[0.05]">
        <CircleAlert className="size-5 text-red-300" />
      </div>

      <p className="mt-3 text-sm font-medium text-slate-300">
        Fleet synchronization unavailable
      </p>

      <p className="mt-1 max-w-sm text-[10px] leading-5 text-slate-600">
        SentinelX could not retrieve the registered agent fleet. Check the
        security session and backend connection.
      </p>
    </div>
  );
}

function FleetEmptyState() {
  return (
    <div className="flex min-h-64 flex-col items-center justify-center px-6 text-center">
      <div className="flex size-12 items-center justify-center rounded-xl border border-cyan-400/10 bg-cyan-400/[0.04]">
        <Bot className="size-6 text-cyan-300/70" />
      </div>

      <p className="mt-4 text-sm font-medium text-slate-300">
        No agents registered
      </p>

      <p className="mt-1 max-w-sm text-[10px] leading-5 text-slate-600">
        There are currently no AI agents associated with this security
        account.
      </p>
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