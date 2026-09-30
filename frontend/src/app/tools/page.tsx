"use client";

import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  CircleAlert,
  Database,
  Globe,
  LoaderCircle,
  LockKeyhole,
  ShieldCheck,
  Terminal,
  Wrench,
} from "lucide-react";

import { useTools } from "@/features/tools/use-tools";
import type { Tool } from "@/types/api";

export default function ToolsPage() {
  const {
    tools = [],
    agents = [],
    isLoading,
    isError,
  } = useTools();

  const enabledTools = tools.filter((tool) => tool.enabled);

  const highRiskTools = tools.filter(
    (tool) => getRisk(tool) === "HIGH",
  );

  const mediumRiskTools = tools.filter(
    (tool) => getRisk(tool) === "MEDIUM",
  );

  const protectedAgents = new Set(
    tools.map((tool) => tool.agent_id),
  ).size;

  const enabledCoverage =
    tools.length === 0
      ? 0
      : Math.round((enabledTools.length / tools.length) * 100);

  const capabilityState = isLoading
    ? "Synchronizing"
    : isError
      ? "Degraded"
      : "Operational";

  return (
    <div className="space-y-6">
      {/* Header */}
      <section className="relative overflow-hidden rounded-2xl border border-white/[0.06] bg-white/[0.02]">
        <div className="security-grid absolute inset-0 opacity-40" />

        <div className="absolute -right-20 -top-20 size-56 rounded-full border border-cyan-400/[0.05]" />
        <div className="absolute -right-10 -top-10 size-36 rounded-full border border-cyan-400/[0.06]" />

        <div className="relative p-6 sm:p-7">
          <div className="flex flex-col justify-between gap-5 lg:flex-row lg:items-end">
            <div>
              <div className="flex items-center gap-2 text-[10px] font-medium uppercase tracking-[0.2em] text-cyan-400">
                <Wrench className="size-3.5" />
                Capability Security
              </div>

              <h1 className="mt-2 text-2xl font-semibold tracking-tight text-white sm:text-3xl">
                Tool &amp; Action Security
              </h1>

              <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">
                Monitor the tools and capabilities exposed to SentinelX
                agents, including their activation state and runtime risk.
              </p>
            </div>

            <div className="flex items-center gap-2 self-start rounded-full border border-emerald-400/10 bg-emerald-400/[0.05] px-3 py-1.5 lg:self-auto">
              <span
                className={`size-1.5 rounded-full ${
                  isError
                    ? "bg-amber-400"
                    : "animate-pulse bg-emerald-400"
                }`}
              />

              <span
                className={`text-[9px] font-medium uppercase tracking-[0.16em] ${
                  isError ? "text-amber-300" : "text-emerald-300"
                }`}
              >
                Capability engine {capabilityState}
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* Metrics */}
      <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard
          label="Registered Tools"
          value={isLoading ? "—" : isError ? "!" : tools.length}
          detail="Capabilities in registry"
          icon={<Wrench className="size-4" />}
          tone="cyan"
        />

        <MetricCard
          label="Enabled"
          value={isLoading ? "—" : isError ? "!" : enabledTools.length}
          detail="Currently executable"
          icon={<CheckCircle2 className="size-4" />}
          tone="emerald"
        />

        <MetricCard
          label="High Risk"
          value={isLoading ? "—" : isError ? "!" : highRiskTools.length}
          detail="Elevated execution exposure"
          icon={<AlertTriangle className="size-4" />}
          tone="red"
        />

        <MetricCard
          label="Protected Agents"
          value={
            isLoading
              ? "—"
              : isError
                ? "!"
                : protectedAgents
          }
          detail={`${agents.length} agents available`}
          icon={<ShieldCheck className="size-4" />}
          tone="violet"
        />
      </section>

      {/* Main capability area */}
      <section className="grid gap-6 xl:grid-cols-[minmax(0,1.55fr)_minmax(300px,0.45fr)]">
        {/* Registry */}
        <section className="security-surface overflow-hidden">
          <div className="border-b border-white/[0.06] p-5 sm:p-6">
            <div className="flex flex-wrap items-end justify-between gap-4">
              <div>
                <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-500">
                  Capability Registry
                </p>

                <h2 className="mt-2 text-lg font-semibold text-white">
                  Registered tools
                </h2>

                <p className="mt-1 text-xs leading-5 text-slate-500">
                  Runtime capabilities currently exposed through the
                  SentinelX control plane.
                </p>
              </div>

              <span className="rounded-full border border-white/[0.06] bg-black/20 px-3 py-1.5 font-mono text-[10px] uppercase tracking-[0.14em] text-slate-500">
                {tools.length}{" "}
                {tools.length === 1 ? "capability" : "capabilities"}
              </span>
            </div>
          </div>

          {isLoading ? (
            <LoadingState />
          ) : isError ? (
            <ErrorState />
          ) : tools.length === 0 ? (
            <EmptyState />
          ) : (
            <div className="divide-y divide-white/[0.05]">
              {tools.map((tool) => (
                <ToolRow key={tool.id} tool={tool} />
              ))}
            </div>
          )}
        </section>

        {/* Capability posture */}
        <section className="security-surface p-5 sm:p-6">
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-500">
                Capability Posture
              </p>

              <h2 className="mt-2 text-lg font-semibold text-white">
                Execution exposure
              </h2>

              <p className="mt-1 text-xs leading-5 text-slate-500">
                Current exposure across registered runtime tools.
              </p>
            </div>

            <LockKeyhole className="size-5 text-cyan-300" />
          </div>

          <div className="mt-7">
            <div className="flex items-center justify-between">
              <span className="text-xs text-slate-500">
                Enabled coverage
              </span>

              <span className="font-mono text-sm font-medium text-slate-200">
                {enabledCoverage}%
              </span>
            </div>

            <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-slate-800">
              <div
                className="h-full rounded-full bg-cyan-400 transition-all duration-500"
                style={{
                  width: `${enabledCoverage}%`,
                }}
              />
            </div>
          </div>

          <div className="mt-7 space-y-3">
            <PostureRow
              label="Enabled capabilities"
              value={enabledTools.length}
              tone="emerald"
            />

            <PostureRow
              label="Disabled capabilities"
              value={tools.length - enabledTools.length}
              tone="slate"
            />

            <PostureRow
              label="High-risk capabilities"
              value={highRiskTools.length}
              tone="red"
            />

            <PostureRow
              label="Medium-risk capabilities"
              value={mediumRiskTools.length}
              tone="amber"
            />
          </div>

          <div className="mt-6 rounded-xl border border-amber-400/10 bg-amber-400/[0.035] p-4">
            <div className="flex items-start gap-3">
              <AlertTriangle className="mt-0.5 size-4 shrink-0 text-amber-300" />

              <div>
                <p className="text-xs font-medium text-amber-200">
                  Execution boundary
                </p>

                <p className="mt-1 text-[11px] leading-5 text-slate-500">
                  Tool capabilities represent potential agent actions.
                  Runtime policy and guardrail controls remain the
                  enforcement boundary for execution decisions.
                </p>
              </div>
            </div>
          </div>
        </section>
      </section>

      {/* Operational signals */}
      <section className="grid gap-3 sm:grid-cols-3">
        <OperationalSignal
          label="Capability telemetry"
          value={isError ? "Degraded" : "Available"}
          tone={isError ? "amber" : "emerald"}
        />

        <OperationalSignal
          label="Policy boundary"
          value="Enforced"
          tone="cyan"
        />

        <OperationalSignal
          label="Runtime protection"
          value="Active"
          tone="emerald"
        />
      </section>
    </div>
  );
}

function ToolRow({ tool }: { tool: Tool }) {
  const risk = getRisk(tool);
  const riskStyles = getRiskStyles(risk);

  return (
    <article className="group px-5 py-5 transition-colors duration-200 hover:bg-white/[0.015] sm:px-6">
      <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
        <div className="flex min-w-0 items-start gap-3">
          <div
            className={`flex size-10 shrink-0 items-center justify-center rounded-xl border ${riskStyles.iconBorder} ${riskStyles.iconBackground}`}
          >
            <ToolIcon
              toolType={tool.tool_type}
              className={`size-5 ${riskStyles.icon}`}
            />
          </div>

          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <h3 className="truncate text-sm font-medium text-slate-200">
                {tool.name}
              </h3>

              <StatusBadge enabled={tool.enabled} />

              <span
                className={`rounded-full border px-2 py-0.5 text-[8px] font-medium uppercase tracking-[0.12em] ${riskStyles.badge}`}
              >
                {risk} risk
              </span>
            </div>

            <p className="mt-1 max-w-2xl text-xs leading-5 text-slate-500">
              {tool.description || "No tool description provided."}
            </p>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-x-8 gap-y-3 pl-[52px] lg:min-w-[300px] lg:pl-0">
          <MetadataItem
            label="Agent"
            value={`#${tool.agent_id}`}
          />

          <MetadataItem
            label="Type"
            value={tool.tool_type}
          />

          <MetadataItem
            label="Tool ID"
            value={`#${tool.id}`}
          />

          <MetadataItem
            label="State"
            value={tool.enabled ? "EXECUTABLE" : "DISABLED"}
          />
        </div>
      </div>
    </article>
  );
}

function ToolIcon({
  toolType,
  className,
}: {
  toolType: string;
  className?: string;
}) {
  const type = toolType.toLowerCase();

  if (
    type.includes("database") ||
    type.includes("sql") ||
    type.includes("db")
  ) {
    return <Database className={className} />;
  }

  if (
    type.includes("http") ||
    type.includes("api") ||
    type.includes("web") ||
    type.includes("network")
  ) {
    return <Globe className={className} />;
  }

  if (
    type.includes("terminal") ||
    type.includes("shell") ||
    type.includes("command") ||
    type.includes("exec")
  ) {
    return <Terminal className={className} />;
  }

  return <Wrench className={className} />;
}

function getRisk(tool: Tool): "HIGH" | "MEDIUM" | "LOW" {
  const type = tool.tool_type.toLowerCase();

  if (
    type.includes("terminal") ||
    type.includes("shell") ||
    type.includes("command") ||
    type.includes("exec")
  ) {
    return "HIGH";
  }

  if (
    type.includes("database") ||
    type.includes("sql") ||
    type.includes("db") ||
    type.includes("network") ||
    type.includes("http") ||
    type.includes("api") ||
    type.includes("web")
  ) {
    return "MEDIUM";
  }

  return "LOW";
}

function getRiskStyles(risk: "HIGH" | "MEDIUM" | "LOW") {
  if (risk === "HIGH") {
    return {
      iconBorder: "border-red-400/10",
      iconBackground: "bg-red-400/[0.05]",
      icon: "text-red-300",
      badge: "border-red-400/10 bg-red-400/[0.05] text-red-300",
    };
  }

  if (risk === "MEDIUM") {
    return {
      iconBorder: "border-amber-400/10",
      iconBackground: "bg-amber-400/[0.05]",
      icon: "text-amber-300",
      badge: "border-amber-400/10 bg-amber-400/[0.05] text-amber-300",
    };
  }

  return {
    iconBorder: "border-emerald-400/10",
    iconBackground: "bg-emerald-400/[0.05]",
    icon: "text-emerald-300",
    badge:
      "border-emerald-400/10 bg-emerald-400/[0.05] text-emerald-300",
  };
}

function MetricCard({
  label,
  value,
  detail,
  icon,
  tone,
}: {
  label: string;
  value: number | string;
  detail: string;
  icon: React.ReactNode;
  tone: "cyan" | "emerald" | "red" | "violet";
}) {
  const toneStyles = {
    cyan: {
      border: "border-cyan-400/10",
      background: "bg-cyan-400/[0.04]",
      icon: "text-cyan-300",
      value: "text-white",
    },
    emerald: {
      border: "border-emerald-400/10",
      background: "bg-emerald-400/[0.035]",
      icon: "text-emerald-300",
      value: "text-white",
    },
    red: {
      border: "border-red-400/10",
      background: "bg-red-400/[0.035]",
      icon: "text-red-300",
      value: "text-red-200",
    },
    violet: {
      border: "border-violet-400/10",
      background: "bg-violet-400/[0.035]",
      icon: "text-violet-300",
      value: "text-white",
    },
  }[tone];

  return (
    <div className="security-surface security-surface-hover p-5">
      <div className="flex items-start justify-between gap-3">
        <span className="text-[9px] font-semibold uppercase tracking-[0.17em] text-slate-500">
          {label}
        </span>

        <div
          className={`flex size-8 items-center justify-center rounded-lg border ${toneStyles.border} ${toneStyles.background} ${toneStyles.icon}`}
        >
          {icon}
        </div>
      </div>

      <div
        className={`mt-4 font-mono text-2xl font-semibold tracking-tight ${toneStyles.value}`}
      >
        {value}
      </div>

      <p className="mt-1 text-[10px] text-slate-600">{detail}</p>
    </div>
  );
}

function StatusBadge({ enabled }: { enabled: boolean }) {
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-2 py-0.5 text-[8px] font-medium uppercase tracking-[0.12em] ${
        enabled
          ? "border-emerald-400/10 bg-emerald-400/[0.05] text-emerald-300"
          : "border-slate-400/10 bg-slate-400/[0.03] text-slate-500"
      }`}
    >
      <span
        className={`size-1.5 rounded-full ${
          enabled ? "bg-emerald-400" : "bg-slate-600"
        }`}
      />

      {enabled ? "Enabled" : "Disabled"}
    </span>
  );
}

function MetadataItem({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="min-w-0">
      <p className="text-[8px] font-medium uppercase tracking-[0.14em] text-slate-700">
        {label}
      </p>

      <p className="mt-1 truncate font-mono text-[10px] text-slate-400">
        {value}
      </p>
    </div>
  );
}

function PostureRow({
  label,
  value,
  tone,
}: {
  label: string;
  value: number;
  tone: "emerald" | "red" | "amber" | "slate";
}) {
  const dotStyles = {
    emerald: "bg-emerald-400",
    red: "bg-red-400",
    amber: "bg-amber-400",
    slate: "bg-slate-600",
  };

  return (
    <div className="flex items-center justify-between rounded-lg border border-white/[0.04] bg-black/10 px-3 py-2.5">
      <div className="flex items-center gap-2.5">
        <span className={`size-1.5 rounded-full ${dotStyles[tone]}`} />

        <span className="text-xs text-slate-500">{label}</span>
      </div>

      <span className="font-mono text-xs font-medium text-slate-300">
        {value}
      </span>
    </div>
  );
}

function OperationalSignal({
  label,
  value,
  tone,
}: {
  label: string;
  value: string;
  tone: "cyan" | "emerald" | "amber";
}) {
  const dotStyles = {
    cyan: "bg-cyan-400",
    emerald: "bg-emerald-400",
    amber: "bg-amber-400",
  };

  return (
    <div className="security-surface flex items-center justify-between px-4 py-3.5">
      <span className="text-[10px] font-semibold uppercase tracking-[0.16em] text-slate-600">
        {label}
      </span>

      <span className="flex items-center gap-2 text-xs font-medium text-slate-300">
        <span className={`size-1.5 rounded-full ${dotStyles[tone]}`} />

        {value}
      </span>
    </div>
  );
}

function LoadingState() {
  return (
    <div className="flex min-h-64 flex-col items-center justify-center px-6 text-center">
      <LoaderCircle className="size-5 animate-spin text-cyan-400" />

      <p className="mt-3 text-[10px] font-medium uppercase tracking-[0.16em] text-slate-600">
        Loading capability registry
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
        Unable to load tools
      </p>

      <p className="mt-1 max-w-sm text-[10px] leading-5 text-slate-600">
        SentinelX could not retrieve the registered tool capabilities.
        Check the security session and backend connection.
      </p>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="flex min-h-64 flex-col items-center justify-center px-6 text-center">
      <div className="flex size-12 items-center justify-center rounded-xl border border-cyan-400/10 bg-cyan-400/[0.04]">
        <Wrench className="size-6 text-cyan-300/70" />
      </div>

      <p className="mt-4 text-sm font-medium text-slate-300">
        No tools registered
      </p>

      <p className="mt-1 max-w-sm text-[10px] leading-5 text-slate-600">
        No runtime capabilities are currently associated with the
        available SentinelX agents.
      </p>

      <div className="mt-4 flex items-center gap-2 text-[9px] uppercase tracking-[0.14em] text-slate-700">
        <Activity className="size-3" />
        Capability telemetry awaiting registration
      </div>
    </div>
  );
}