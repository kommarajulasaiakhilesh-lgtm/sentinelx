"use client";

import {
  Activity,
  Bot,
  CalendarDays,
  CircleAlert,
  LoaderCircle,
  ShieldCheck,
  UserRound,
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

  return (
    <div className="space-y-6">
      {/* Header */}
      <section className="relative overflow-hidden rounded-2xl border border-white/[0.06] bg-white/[0.02] p-6">
        <div className="security-grid absolute inset-0 opacity-40" />

        <div className="relative">
          <div className="flex items-center gap-2 text-[10px] font-medium uppercase tracking-[0.2em] text-cyan-400">
            <Bot className="size-3.5" />
            Agent Security
          </div>

          <div className="mt-2 flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
            <div>
              <h1 className="text-2xl font-semibold tracking-tight text-white">
                Agents
              </h1>

              <p className="mt-1 max-w-2xl text-sm text-slate-500">
                Monitor and manage the AI agents connected to the SentinelX
                control plane.
              </p>
            </div>

            <div className="flex items-center gap-2 rounded-full border border-emerald-400/10 bg-emerald-400/[0.05] px-3 py-1.5">
              <span className="size-1.5 animate-pulse rounded-full bg-emerald-400" />
              <span className="text-[9px] uppercase tracking-[0.16em] text-emerald-300">
                Control plane operational
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* Summary */}
      <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
        <SummaryCard
          label="Registered Agents"
          value={isLoading ? "—" : isError ? "!" : agents.length.toString()}
          detail={isError ? "Unable to load agents" : "Connected to control plane"}
          icon={Bot}
        />

        <SummaryCard
          label="Active Agents"
          value={isLoading ? "—" : isError ? "!" : activeAgents.toString()}
          detail={isError ? "Unable to load agents" : "Currently active"}
          icon={Activity}
        />

        <SummaryCard
          label="Fleet Status"
          value={isLoading ? "—" : isError ? "!" : "MONITORED"}
          detail="Runtime security monitoring"
          icon={ShieldCheck}
        />
      </section>

      {/* Agent list */}
      <section className="overflow-hidden rounded-xl border border-white/[0.06] bg-white/[0.02]">
        <div className="flex items-center justify-between border-b border-white/[0.06] px-5 py-4">
          <div>
            <div className="flex items-center gap-2">
              <Bot className="size-4 text-cyan-300" />

              <h2 className="text-sm font-medium text-slate-200">
                Registered Agents
              </h2>
            </div>

            <p className="mt-1 text-[10px] text-slate-600">
              Agents registered under the current security account
            </p>
          </div>

          {!isLoading && !isError && (
            <span className="rounded-full border border-white/[0.06] bg-white/[0.03] px-2.5 py-1 font-mono text-[9px] text-slate-500">
              {agents.length} TOTAL
            </span>
          )}
        </div>

        {isLoading ? (
          <AgentsLoadingState />
        ) : isError ? (
          <AgentsErrorState />
        ) : agents.length === 0 ? (
          <AgentsEmptyState />
        ) : (
          <div className="divide-y divide-white/[0.05]">
            {agents.map((agent) => (
              <article
                key={agent.id}
                className="group px-5 py-4 transition-colors hover:bg-white/[0.02]"
              >
                <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
                  {/* Identity */}
                  <div className="flex min-w-0 items-start gap-3">
                    <div className="flex size-10 shrink-0 items-center justify-center rounded-lg border border-cyan-400/10 bg-cyan-400/[0.05]">
                      <Bot className="size-5 text-cyan-300" />
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

                  {/* Metadata */}
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
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

function SummaryCard({
  label,
  value,
  detail,
  icon: Icon,
}: {
  label: string;
  value: string;
  detail: string;
  icon: typeof Bot;
}) {
  return (
    <div className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-4">
      <div className="flex items-center justify-between">
        <span className="text-[9px] font-medium uppercase tracking-[0.16em] text-slate-600">
          {label}
        </span>

        <div className="flex size-8 items-center justify-center rounded-lg border border-cyan-400/10 bg-cyan-400/[0.05]">
          <Icon className="size-4 text-cyan-300" />
        </div>
      </div>

      <div className="mt-3 text-2xl font-semibold tracking-tight text-white">
        {value}
      </div>

      <div className="mt-1 text-[10px] text-slate-600">{detail}</div>
    </div>
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

function AgentsLoadingState() {
  return (
    <div className="flex min-h-64 flex-col items-center justify-center">
      <LoaderCircle className="size-5 animate-spin text-cyan-400" />

      <p className="mt-3 text-[10px] uppercase tracking-[0.16em] text-slate-600">
        Loading agent fleet
      </p>
    </div>
  );
}

function AgentsErrorState() {
  return (
    <div className="flex min-h-64 flex-col items-center justify-center px-6 text-center">
      <div className="flex size-10 items-center justify-center rounded-full border border-red-400/10 bg-red-400/[0.05]">
        <CircleAlert className="size-5 text-red-300" />
      </div>

      <p className="mt-3 text-sm font-medium text-slate-300">
        Unable to load agents
      </p>

      <p className="mt-1 max-w-sm text-[10px] text-slate-600">
        SentinelX could not retrieve the registered agent fleet. Check the
        security session and backend connection.
      </p>
    </div>
  );
}

function AgentsEmptyState() {
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