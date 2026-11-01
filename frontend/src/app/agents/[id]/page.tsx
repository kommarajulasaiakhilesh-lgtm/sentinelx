"use client";

import { use } from "react";
import Link from "next/link";
import { motion } from "motion/react";
import { useQuery } from "@tanstack/react-query";
import {
  ArrowLeft,
  Activity,
  Bot,
  LoaderCircle,
  Shield,
  Wrench,
} from "lucide-react";

import { get } from "@/lib/api-client";
import { useAuth } from "@/hooks/use-auth";
import { useMyAgents } from "@/features/agents/use-agents";
import { ApiKeysPanel } from "@/components/agents/api-keys-panel";
import { AttackBatteryPanel } from "@/components/agents/attack-battery-panel";
import type { AgentPosture } from "@/features/posture/posture-api";
import type { Policy, SecurityEvent, Tool } from "@/types/api";

const decisionColor: Record<string, string> = {
  ALLOW: "text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-500/10 border-emerald-200 dark:border-emerald-500/30",
  BLOCK: "text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-500/10 border-red-200 dark:border-red-500/30",
  SUSPICIOUS: "text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-500/10 border-amber-200 dark:border-amber-500/30",
};

const levelColor: Record<string, string> = {
  STRONG: "text-emerald-600 dark:text-emerald-400",
  MODERATE: "text-indigo-600 dark:text-indigo-400",
  WEAK: "text-amber-600 dark:text-amber-400",
  CRITICAL: "text-red-600 dark:text-red-400",
};

export default function AgentDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const agentId = Number(id);
  const { token } = useAuth();

  const { data: agents = [] } = useMyAgents();
  const agent = agents.find((a) => a.id === agentId);

  const { data: posture } = useQuery({
    queryKey: ["posture", "agent", agentId],
    queryFn: () => get<AgentPosture>(`/api/posture/agents/${agentId}`, token as string),
    enabled: Boolean(token),
  });
  const { data: policies = [] } = useQuery({
    queryKey: ["policies", "agent", agentId],
    queryFn: () => get<Policy[]>(`/api/policies/agent/${agentId}`, token as string),
    enabled: Boolean(token),
  });
  const { data: tools = [] } = useQuery({
    queryKey: ["tools", "agent", agentId],
    queryFn: () => get<Tool[]>(`/api/agents/${agentId}/tools`, token as string),
    enabled: Boolean(token),
  });
  const { data: eventsResp } = useQuery({
    queryKey: ["events", "agent", agentId],
    queryFn: () =>
      get<{ items: SecurityEvent[] }>(
        `/api/security-events?agent_id=${agentId}&page=1&page_size=8`,
        token as string,
      ),
    enabled: Boolean(token),
  });
  const events = eventsResp?.items ?? [];

  if (!agent) {
    return (
      <div className="security-surface flex items-center justify-center gap-3 py-16 text-sm text-slate-500 dark:text-slate-400">
        <LoaderCircle className="size-4 animate-spin text-indigo-600 dark:text-indigo-400" />
        Loading agent…
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <Link
        href="/agents"
        className="inline-flex items-center gap-1.5 text-xs font-medium text-slate-500 dark:text-slate-400 transition hover:text-indigo-600 dark:hover:text-indigo-400"
      >
        <ArrowLeft className="size-3.5" />
        Back to agents
      </Link>

      {/* Header */}
      <motion.section
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35 }}
        className="security-surface flex flex-col gap-4 p-6 sm:flex-row sm:items-center sm:justify-between"
      >
        <div className="flex items-center gap-4">
          <div className="flex size-14 items-center justify-center rounded-2xl border border-indigo-200 dark:border-indigo-500/30 bg-indigo-50 dark:bg-indigo-500/10">
            <Bot className="size-7 text-indigo-600 dark:text-indigo-400" />
          </div>
          <div>
            <h1 className="text-2xl font-semibold tracking-tight text-slate-900 dark:text-slate-100">
              {agent.name}
            </h1>
            <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
              {agent.description || "No description provided"}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <span
            className={`rounded-md border px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.1em] ${
              agent.status === "ACTIVE"
                ? "border-emerald-200 dark:border-emerald-500/30 bg-emerald-50 dark:bg-emerald-500/10 text-emerald-700 dark:text-emerald-400"
                : "border-amber-200 dark:border-amber-500/30 bg-amber-50 dark:bg-amber-500/10 text-amber-700 dark:text-amber-400"
            }`}
          >
            {agent.status}
          </span>
          {posture && (
            <div className="text-right">
              <div className={`text-2xl font-semibold ${levelColor[posture.level]}`}>
                {posture.score}
              </div>
              <div className="text-[10px] uppercase tracking-[0.12em] text-slate-500 dark:text-slate-400">
                Posture · {posture.grade}
              </div>
            </div>
          )}
        </div>
      </motion.section>

      {/* Signal tiles */}
      <section className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <Stat label="Policies" value={policies.length} icon={Shield} />
        <Stat label="Tools" value={tools.length} icon={Wrench} />
        <Stat
          label="Open alerts"
          value={posture?.signals.open_alerts ?? 0}
          icon={Activity}
          warn={(posture?.signals.open_alerts ?? 0) > 0}
        />
        <Stat
          label="Recent blocks"
          value={posture?.signals.recent_blocked_events ?? 0}
          icon={Activity}
          warn={(posture?.signals.recent_blocked_events ?? 0) > 0}
        />
      </section>

      <div className="grid gap-4 lg:grid-cols-2">
        <Panel title="Policies" count={policies.length}>
          {policies.length === 0 ? (
            <Empty>No policies attached.</Empty>
          ) : (
            policies.map((p) => (
              <Row key={p.id} title={p.name} subtitle={p.policy_type}>
                <Badge enabled={p.enabled} text={p.action} />
              </Row>
            ))
          )}
        </Panel>

        <Panel title="Tools" count={tools.length}>
          {tools.length === 0 ? (
            <Empty>No tools granted.</Empty>
          ) : (
            tools.map((t) => (
              <Row key={t.id} title={t.name} subtitle={t.tool_type}>
                <Badge enabled={t.enabled} text={t.enabled ? "Enabled" : "Disabled"} />
              </Row>
            ))
          )}
        </Panel>
      </div>

      <AttackBatteryPanel agentId={agentId} />

      <ApiKeysPanel agentId={agentId} />

      <Panel title="Recent security events" count={events.length}>
        {events.length === 0 ? (
          <Empty>No recent events for this agent.</Empty>
        ) : (
          events.map((e) => (
            <Row
              key={e.id}
              title={e.event_type}
              subtitle={e.reason || e.action}
            >
              <span
                className={`rounded-md border px-2 py-0.5 text-[10px] font-semibold ${
                  decisionColor[e.decision] ?? "border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50 text-slate-600 dark:text-slate-300"
                }`}
              >
                {e.decision}
              </span>
            </Row>
          ))
        )}
      </Panel>
    </div>
  );
}

function Stat({
  label,
  value,
  icon: Icon,
  warn = false,
}: {
  label: string;
  value: number;
  icon: typeof Bot;
  warn?: boolean;
}) {
  return (
    <div className="security-surface flex items-center justify-between p-4">
      <div>
        <div className={`text-2xl font-semibold ${warn ? "text-amber-600 dark:text-amber-400" : "text-slate-900 dark:text-slate-100"}`}>
          {value}
        </div>
        <div className="mt-0.5 text-[10px] font-medium uppercase tracking-[0.1em] text-slate-500 dark:text-slate-400">
          {label}
        </div>
      </div>
      <Icon className="size-5 text-slate-300" />
    </div>
  );
}

function Panel({
  title,
  count,
  children,
}: {
  title: string;
  count: number;
  children: React.ReactNode;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35 }}
      className="security-surface overflow-hidden"
    >
      <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 px-5 py-3.5">
        <span className="text-sm font-semibold text-slate-900 dark:text-slate-100">{title}</span>
        <span className="text-[11px] font-medium text-slate-500 dark:text-slate-400">{count}</span>
      </div>
      <div className="divide-y divide-slate-100 dark:divide-slate-800">{children}</div>
    </motion.div>
  );
}

function Row({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle?: string | null;
  children?: React.ReactNode;
}) {
  return (
    <div className="flex items-center justify-between px-5 py-3 hover:bg-slate-50 dark:hover:bg-slate-800/50">
      <div className="min-w-0">
        <div className="truncate text-sm font-medium text-slate-800 dark:text-slate-100">{title}</div>
        {subtitle && (
          <div className="truncate text-[11px] text-slate-500 dark:text-slate-400">{subtitle}</div>
        )}
      </div>
      {children}
    </div>
  );
}

function Badge({ enabled, text }: { enabled: boolean; text: string }) {
  return (
    <span
      className={`rounded-md border px-2 py-0.5 text-[10px] font-semibold ${
        enabled
          ? "border-indigo-200 dark:border-indigo-500/30 bg-indigo-50 dark:bg-indigo-500/10 text-indigo-700 dark:text-indigo-300"
          : "border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50 text-slate-500 dark:text-slate-400"
      }`}
    >
      {text}
    </span>
  );
}

function Empty({ children }: { children: React.ReactNode }) {
  return <div className="px-5 py-8 text-center text-xs text-slate-400 dark:text-slate-500">{children}</div>;
}
