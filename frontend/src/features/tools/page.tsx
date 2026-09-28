"use client";

import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  Database,
  Globe,
  LockKeyhole,
  LoaderCircle,
  ShieldCheck,
  Terminal,
  Wrench,
} from "lucide-react";

import { useTools } from "@/features/tools/use-tools";
import type { Tool } from "@/types/api";

function StatCard({
  label,
  value,
  detail,
  icon: Icon,
}: {
  label: string;
  value: string | number;
  detail: string;
  icon: typeof Wrench;
}) {
  return (
    <div className="relative overflow-hidden rounded-2xl border border-white/10 bg-white/[0.035] p-5">
      <div className="absolute right-0 top-0 h-24 w-24 rounded-full bg-cyan-400/5 blur-2xl" />

      <div className="relative flex items-start justify-between">
        <div>
          <p className="text-xs font-medium uppercase tracking-[0.18em] text-slate-500">
            {label}
          </p>

          <p className="mt-3 text-3xl font-semibold tracking-tight text-white">
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

function getToolIcon(toolType: string) {
  const type = toolType.toLowerCase();

  if (type.includes("database") || type.includes("sql")) {
    return Database;
  }

  if (
    type.includes("http") ||
    type.includes("api") ||
    type.includes("web")
  ) {
    return Globe;
  }

  if (
    type.includes("terminal") ||
    type.includes("shell") ||
    type.includes("command")
  ) {
    return Terminal;
  }

  return Wrench;
}

function getRisk(tool: Tool) {
  const type = tool.tool_type.toLowerCase();
  const name = tool.name.toLowerCase();

  if (
    type.includes("shell") ||
    type.includes("terminal") ||
    type.includes("command") ||
    name.includes("exec")
  ) {
    return {
      label: "HIGH",
      className:
        "border-red-400/20 bg-red-400/10 text-red-300",
    };
  }

  if (
    type.includes("database") ||
    type.includes("sql") ||
    type.includes("api")
  ) {
    return {
      label: "MEDIUM",
      className:
        "border-amber-400/20 bg-amber-400/10 text-amber-300",
    };
  }

  return {
    label: "LOW",
    className:
      "border-emerald-400/20 bg-emerald-400/10 text-emerald-300",
  };
}

function formatDate(value?: string) {
  if (!value) {
    return "Unknown";
  }

  return new Date(value).toLocaleDateString(
    undefined,
    {
      month: "short",
      day: "numeric",
      year: "numeric",
    },
  );
}

export default function ToolsPage() {
  const {
    tools,
    agents,
    isLoading,
    isError,
  } = useTools();

  const enabledTools = tools.filter(
    (tool) => tool.enabled,
  );

  const disabledTools = tools.filter(
    (tool) => !tool.enabled,
  );

  const highRiskTools = tools.filter(
    (tool) => getRisk(tool).label === "HIGH",
  );

  const agentName = new Map(
    agents.map((agent) => [agent.id, agent.name]),
  );

  return (
    <div className="space-y-8">
      {/* HERO */}
      <section className="relative overflow-hidden rounded-3xl border border-cyan-400/10 bg-gradient-to-br from-cyan-400/[0.08] via-transparent to-blue-500/[0.05] p-6 sm:p-8">
        <div className="absolute -right-20 -top-24 h-72 w-72 rounded-full bg-cyan-400/10 blur-3xl" />
        <div className="absolute -bottom-24 left-1/3 h-56 w-56 rounded-full bg-blue-500/10 blur-3xl" />

        <div className="relative">
          <div className="flex flex-wrap items-center gap-3">
            <div className="flex items-center gap-2 rounded-full border border-cyan-400/20 bg-cyan-400/10 px-3 py-1.5 text-xs font-medium text-cyan-300">
              <Wrench className="h-3.5 w-3.5" />
              Tool Security
            </div>

            <div className="flex items-center gap-2 text-xs text-emerald-400">
              <span className="h-2 w-2 animate-pulse rounded-full bg-emerald-400" />
              Enforcement online
            </div>
          </div>

          <h1 className="mt-5 text-3xl font-semibold tracking-tight text-white sm:text-4xl">
            Tools & Actions
          </h1>

          <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-400">
            Monitor the capabilities exposed to SentinelX agents
            and understand which tools are available for runtime
            execution.
          </p>

          <div className="mt-6 flex items-center gap-3 text-xs text-slate-500">
            <ShieldCheck className="h-4 w-4 text-cyan-400" />
            Agent → Tool → Action → Policy enforcement
          </div>
        </div>
      </section>

      {/* STATS */}
      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          label="Registered Tools"
          value={isLoading ? "—" : isError ? "!" : tools.length}
          detail="Known agent capabilities"
          icon={Wrench}
        />

        <StatCard
          label="Enabled Tools"
          value={isLoading ? "—" : isError ? "!" : enabledTools.length}
          detail="Currently executable"
          icon={CheckCircle2}
        />

        <StatCard
          label="High Risk"
          value={isLoading ? "—" : isError ? "!" : highRiskTools.length}
          detail="Require stronger controls"
          icon={AlertTriangle}
        />

        <StatCard
          label="Agents"
          value={isLoading ? "—" : isError ? "!" : agents.length}
          detail="Tool-owning agents"
          icon={Activity}
        />
      </section>

      {/* SECURITY MATRIX */}
      <section className="grid gap-6 xl:grid-cols-[1.7fr_1fr]">
        <div className="overflow-hidden rounded-2xl border border-white/10 bg-white/[0.025]">
          <div className="flex items-center justify-between border-b border-white/10 px-5 py-4">
            <div>
              <h2 className="font-semibold text-white">
                Tool Security Matrix
              </h2>

              <p className="mt-1 text-xs text-slate-500">
                Capabilities currently registered with the control plane
              </p>
            </div>

            <div className="rounded-lg border border-white/10 px-3 py-1.5 text-[10px] font-semibold tracking-[0.16em] text-slate-500">
              {tools.length} TOOLS
            </div>
          </div>

          {isLoading ? (
            <div className="flex min-h-72 items-center justify-center">
              <div className="flex items-center gap-2 text-sm text-slate-500">
                <LoaderCircle className="h-4 w-4 animate-spin" />
                Loading tool inventory...
              </div>
            </div>
          ) : isError ? (
            <div className="flex min-h-72 items-center justify-center px-6 text-center">
              <div>
                <AlertTriangle className="mx-auto h-8 w-8 text-amber-400" />
                <p className="mt-3 font-medium text-white">
                  Tool inventory unavailable
                </p>
                <p className="mt-1 text-sm text-slate-500">
                  The control plane could not retrieve the current tool
                  registry.
                </p>
              </div>
            </div>
          ) : tools.length === 0 ? (
            <div className="flex min-h-72 items-center justify-center px-6 text-center">
              <div className="max-w-md">
                <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl border border-cyan-400/15 bg-cyan-400/10">
                  <Wrench className="h-6 w-6 text-cyan-300" />
                </div>

                <h3 className="mt-4 font-semibold text-white">
                  No tools registered
                </h3>

                <p className="mt-2 text-sm leading-6 text-slate-500">
                  SentinelX has not discovered any agent tools yet.
                  Tool capabilities will appear here once they are
                  registered against an agent.
                </p>
              </div>
            </div>
          ) : (
            <div className="divide-y divide-white/5">
              {tools.map((tool) => {
                const Icon = getToolIcon(tool.tool_type);
                const risk = getRisk(tool);

                return (
                  <div
                    key={tool.id}
                    className="group px-5 py-4 transition hover:bg-white/[0.025]"
                  >
                    <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
                      <div className="flex min-w-0 items-center gap-4">
                        <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl border border-white/10 bg-white/[0.04] text-cyan-300">
                          <Icon className="h-5 w-5" />
                        </div>

                        <div className="min-w-0">
                          <div className="flex flex-wrap items-center gap-2">
                            <p className="truncate font-medium text-white">
                              {tool.name}
                            </p>

                            <span
                              className={`rounded-full border px-2 py-0.5 text-[9px] font-semibold tracking-[0.14em] ${risk.className}`}
                            >
                              {risk.label}
                            </span>
                          </div>

                          <p className="mt-1 truncate text-xs text-slate-500">
                            {tool.description ||
                              "No description provided"}
                          </p>
                        </div>
                      </div>

                      <div className="grid grid-cols-2 gap-4 text-xs sm:grid-cols-4 lg:min-w-[430px]">
                        <div>
                          <p className="text-[9px] uppercase tracking-[0.16em] text-slate-600">
                            Type
                          </p>
                          <p className="mt-1 text-slate-300">
                            {tool.tool_type}
                          </p>
                        </div>

                        <div>
                          <p className="text-[9px] uppercase tracking-[0.16em] text-slate-600">
                            Agent
                          </p>
                          <p className="mt-1 truncate text-slate-300">
                            {agentName.get(tool.agent_id) ||
                              `Agent #${tool.agent_id}`}
                          </p>
                        </div>

                        <div>
                          <p className="text-[9px] uppercase tracking-[0.16em] text-slate-600">
                            Status
                          </p>

                          <div className="mt-1 flex items-center gap-1.5">
                            <span
                              className={`h-1.5 w-1.5 rounded-full ${
                                tool.enabled
                                  ? "bg-emerald-400"
                                  : "bg-slate-600"
                              }`}
                            />

                            <span
                              className={
                                tool.enabled
                                  ? "text-emerald-300"
                                  : "text-slate-500"
                              }
                            >
                              {tool.enabled
                                ? "ENABLED"
                                : "DISABLED"}
                            </span>
                          </div>
                        </div>

                        <div>
                          <p className="text-[9px] uppercase tracking-[0.16em] text-slate-600">
                            Registered
                          </p>

                          <p className="mt-1 text-slate-400">
                            {formatDate(tool.created_at)}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* POSTURE */}
        <div className="rounded-2xl border border-white/10 bg-white/[0.025] p-5">
          <div className="flex items-center gap-3">
            <div className="rounded-xl border border-cyan-400/15 bg-cyan-400/10 p-2.5 text-cyan-300">
              <LockKeyhole className="h-5 w-5" />
            </div>

            <div>
              <h2 className="font-semibold text-white">
                Capability Posture
              </h2>

              <p className="text-xs text-slate-500">
                Current tool exposure
              </p>
            </div>
          </div>

          <div className="mt-7 space-y-6">
            <div>
              <div className="flex items-end justify-between">
                <span className="text-xs uppercase tracking-[0.16em] text-slate-500">
                  Enabled coverage
                </span>

                <span className="text-2xl font-semibold text-white">
                  {tools.length
                    ? Math.round(
                        (enabledTools.length / tools.length) * 100,
                      )
                    : 0}
                  %
                </span>
              </div>

              <div className="mt-3 h-2 overflow-hidden rounded-full bg-white/5">
                <div
                  className="h-full rounded-full bg-cyan-400 transition-all"
                  style={{
                    width: `${
                      tools.length
                        ? (enabledTools.length / tools.length) * 100
                        : 0
                    }%`,
                  }}
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="rounded-xl border border-emerald-400/10 bg-emerald-400/[0.04] p-4">
                <p className="text-[10px] uppercase tracking-[0.16em] text-slate-600">
                  Enabled
                </p>

                <p className="mt-2 text-2xl font-semibold text-emerald-300">
                  {enabledTools.length}
                </p>
              </div>

              <div className="rounded-xl border border-white/10 bg-white/[0.02] p-4">
                <p className="text-[10px] uppercase tracking-[0.16em] text-slate-600">
                  Disabled
                </p>

                <p className="mt-2 text-2xl font-semibold text-slate-400">
                  {disabledTools.length}
                </p>
              </div>
            </div>

            <div className="rounded-xl border border-amber-400/10 bg-amber-400/[0.035] p-4">
              <div className="flex gap-3">
                <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-amber-400" />

                <div>
                  <p className="text-sm font-medium text-amber-200">
                    Runtime enforcement
                  </p>

                  <p className="mt-1 text-xs leading-5 text-slate-500">
                    Tool actions flow through SentinelX policy
                    enforcement before execution.
                  </p>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2 border-t border-white/5 pt-5 text-xs text-slate-600">
              <ShieldCheck className="h-4 w-4 text-cyan-400/70" />
              Protected by policy evaluation
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}