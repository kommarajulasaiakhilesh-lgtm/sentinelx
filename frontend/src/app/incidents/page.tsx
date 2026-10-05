"use client";

import {
  AlertTriangle,
  CheckCircle2,
  Clock3,
  LoaderCircle,
  MessageSquare,
  RotateCcw,
  ShieldAlert,
  ShieldCheck,
  Siren,
  UserRound,
  Wrench,
  XCircle,
  type LucideIcon,
} from "lucide-react";
import { useState } from "react";

import {
  useAgentApiKeys,
  useMyAgents,
} from "@/features/agents/use-agents";
import { useAgentTools } from "@/features/tools/use-tools";
import {
  useAddIncidentTimelineEntry,
  useCreateIncidentResponseAction,
  useIncident,
  useIncidentResponseActions,
  useIncidentTimeline,
  useIncidents,
} from "@/features/incidents/use-incidents";

type IncidentMetric = [
  label: string,
  value: string | number,
  detail: string,
  Icon: LucideIcon,
  tone: string,
];

type ResponseActionType =
  | "SUSPEND_AGENT"
  | "DISABLE_TOOL"
  | "ROTATE_AGENT_API_KEY";

function formatDate(value?: string | null) {
  if (!value) return "—";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat("en-IN", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

function severityClass(value: string) {
  switch (value.toUpperCase()) {
    case "CRITICAL":
      return "border-red-400/20 bg-red-400/10 text-red-300";
    case "HIGH":
      return "border-orange-400/20 bg-orange-400/10 text-orange-300";
    case "MEDIUM":
      return "border-amber-400/20 bg-amber-400/10 text-amber-300";
    default:
      return "border-slate-700 bg-slate-800/50 text-slate-300";
  }
}

function statusClass(value: string) {
  switch (value.toUpperCase()) {
    case "OPEN":
      return "border-red-400/20 bg-red-400/10 text-red-300";
    case "INVESTIGATING":
      return "border-amber-400/20 bg-amber-400/10 text-amber-300";
    case "CONTAINED":
      return "border-cyan-400/20 bg-cyan-400/10 text-cyan-300";
    case "RESOLVED":
      return "border-emerald-400/20 bg-emerald-400/10 text-emerald-300";
    default:
      return "border-slate-700 bg-slate-800/50 text-slate-300";
  }
}

function Badge({
  children,
  className,
}: {
  children: React.ReactNode;
  className: string;
}) {
  return (
    <span
      className={`inline-flex rounded-full border px-2.5 py-1 text-[9px] font-semibold uppercase tracking-[0.14em] ${className}`}
    >
      {children}
    </span>
  );
}

export default function IncidentsPage() {
  const [status, setStatus] = useState("ALL");
  const [severity, setSeverity] = useState("ALL");
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [note, setNote] = useState("");
  const [actionReason, setActionReason] = useState("");
  const [actionType, setActionType] =
    useState<ResponseActionType>("SUSPEND_AGENT");
  const [selectedToolId, setSelectedToolId] = useState<string>("");
  const [selectedApiKeyId, setSelectedApiKeyId] = useState<string>("");

  const incidentsQuery = useIncidents(1, 20, status, severity);

  const incidents = incidentsQuery.data?.items ?? [];

  const activeId = selectedId ?? incidents[0]?.id ?? null;

  const incidentQuery = useIncident(activeId);
  const timelineQuery = useIncidentTimeline(activeId);
  const actionsQuery = useIncidentResponseActions(activeId);

  const addNote = useAddIncidentTimelineEntry(activeId ?? 0);

  const responseAction = useCreateIncidentResponseAction(
    activeId ?? 0,
  );

  const activeIncident =
    incidentQuery.data ??
    incidents.find((item) => item.id === activeId);

  const { data: agents = [] } = useMyAgents();

  const activeAgent = activeIncident
    ? agents.find((agent) => agent.id === activeIncident.agent_id)
    : undefined;

  const toolsQuery = useAgentTools(
    activeIncident?.agent_id ?? null,
  );

  const apiKeysQuery = useAgentApiKeys(
    activeIncident?.agent_id ?? null,
  );

  const tools = toolsQuery.data ?? [];
  const apiKeys = apiKeysQuery.data ?? [];

  const openCount = incidents.filter(
    (item) =>
      item.status === "OPEN" ||
      item.status === "INVESTIGATING",
  ).length;

  const criticalCount = incidents.filter(
    (item) => item.severity === "CRITICAL",
  ).length;

  const containedCount = incidents.filter(
    (item) => item.status === "CONTAINED",
  ).length;

  async function submitNote() {
    if (!activeId || !note.trim()) return;

    await addNote.mutateAsync(note.trim());

    setNote("");
  }

  const targetMissing =
    actionType === "DISABLE_TOOL"
      ? !selectedToolId
      : actionType === "ROTATE_AGENT_API_KEY"
        ? !selectedApiKeyId
        : false;

  async function executeAction() {
    if (
      !activeId ||
      !activeIncident ||
      !actionReason.trim() ||
      targetMissing
    ) {
      return;
    }

    const payload = {
      action_type: actionType,
      reason: actionReason.trim(),
      agent_id: activeIncident.agent_id,
      ...(actionType === "DISABLE_TOOL"
        ? { tool_id: Number(selectedToolId) }
        : {}),
      ...(actionType === "ROTATE_AGENT_API_KEY"
        ? { api_key_id: Number(selectedApiKeyId) }
        : {}),
    };

    await responseAction.mutateAsync(payload);

    setActionReason("");
    setSelectedToolId("");
    setSelectedApiKeyId("");
  }

  const metrics: IncidentMetric[] = [
    [
      "Total Incidents",
      incidentsQuery.data?.total ?? 0,
      "Correlated incidents",
      ShieldAlert,
      "text-cyan-300",
    ],
    [
      "Active",
      openCount,
      "Open or investigating",
      AlertTriangle,
      "text-orange-300",
    ],
    [
      "Critical",
      criticalCount,
      "Critical severity",
      Siren,
      "text-red-300",
    ],
  ];

  return (
    <div className="space-y-6 sm:space-y-8">
      <section className="relative overflow-hidden rounded-2xl border border-red-400/10 bg-red-400/[0.025] p-6 sm:p-8">
        <div className="security-grid absolute inset-0 opacity-25" />

        <div className="pointer-events-none absolute -right-24 -top-24 size-64 rounded-full bg-red-400/5 blur-3xl" />

        <div className="relative">
          <div className="flex flex-wrap items-center gap-3">
            <span className="inline-flex items-center gap-2 rounded-full border border-red-400/20 bg-red-400/[0.06] px-3 py-1.5 text-[10px] font-semibold uppercase tracking-[0.18em] text-red-300">
              <Siren className="size-3.5" />
              Security Operations
            </span>

            <span className="inline-flex items-center gap-2 text-[10px] font-medium uppercase tracking-[0.16em] text-emerald-400">
              <span className="size-1.5 animate-pulse rounded-full bg-emerald-400" />
              Incident control online
            </span>
          </div>

          <div className="mt-5">
            <h1 className="text-2xl font-semibold tracking-tight text-white sm:text-3xl">
              Incident Response
            </h1>

            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">
              Investigate correlated security incidents, review their
              timeline, and execute authorized containment actions.
            </p>
          </div>
        </div>
      </section>

      <section className="grid gap-3 sm:grid-cols-3">
        {metrics.map(([label, value, detail, Icon, tone]) => (
          <article
            key={label}
            className="security-surface security-surface-hover p-5"
          >
            <div className="flex items-start justify-between">
              <div>
                <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-500">
                  {label}
                </p>

                <p className="mt-3 text-3xl font-semibold text-white">
                  {String(value)}
                </p>

                <p className="mt-1 text-xs text-slate-500">
                  {detail}
                </p>
              </div>

              <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-3">
                <Icon className={`size-5 ${tone}`} />
              </div>
            </div>
          </article>
        ))}
      </section>

      <section className="grid gap-5 xl:grid-cols-[minmax(0,0.9fr)_minmax(0,1.5fr)]">
        <div className="security-surface overflow-hidden">
          <div className="border-b border-slate-800/80 p-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-red-400">
                  Case queue
                </p>

                <h2 className="mt-1 text-lg font-semibold text-white">
                  Incidents
                </h2>
              </div>

              <span className="text-[10px] uppercase tracking-[0.15em] text-slate-600">
                {incidents.length} loaded
              </span>
            </div>

            <div className="mt-4 grid grid-cols-2 gap-2">
              <select
                value={status}
                onChange={(event) => setStatus(event.target.value)}
                className="rounded-xl border border-slate-800 bg-slate-950 px-3 py-2 text-xs text-slate-300 outline-none focus:border-cyan-400/40"
              >
                <option value="ALL">All statuses</option>
                <option value="OPEN">Open</option>
                <option value="INVESTIGATING">
                  Investigating
                </option>
                <option value="CONTAINED">Contained</option>
                <option value="RESOLVED">Resolved</option>
              </select>

              <select
                value={severity}
                onChange={(event) =>
                  setSeverity(event.target.value)
                }
                className="rounded-xl border border-slate-800 bg-slate-950 px-3 py-2 text-xs text-slate-300 outline-none focus:border-cyan-400/40"
              >
                <option value="ALL">All severities</option>
                <option value="CRITICAL">Critical</option>
                <option value="HIGH">High</option>
                <option value="MEDIUM">Medium</option>
                <option value="LOW">Low</option>
              </select>
            </div>
          </div>

          {incidentsQuery.isLoading ? (
            <div className="flex min-h-72 items-center justify-center">
              <LoaderCircle className="size-5 animate-spin text-cyan-400" />
            </div>
          ) : incidentsQuery.isError ? (
            <div className="p-8 text-center">
              <XCircle className="mx-auto size-8 text-red-400" />

              <p className="mt-3 text-sm font-semibold text-white">
                Incident telemetry unavailable
              </p>

              <p className="mt-2 text-xs text-slate-500">
                Verify that the backend is running and authenticated.
              </p>
            </div>
          ) : incidents.length === 0 ? (
            <div className="p-10 text-center">
              <ShieldCheck className="mx-auto size-9 text-emerald-300" />

              <p className="mt-4 text-sm font-semibold text-white">
                No incidents found
              </p>

              <p className="mt-2 text-xs text-slate-500">
                No incidents match the selected filters.
              </p>
            </div>
          ) : (
            <div className="max-h-[650px] divide-y divide-slate-800/60 overflow-y-auto">
              {incidents.map((incident) => (
                <button
                  key={incident.id}
                  type="button"
                  onClick={() => {
                    setSelectedId(incident.id);
                    setSelectedToolId("");
                    setSelectedApiKeyId("");
                    setActionType("SUSPEND_AGENT");
                    setActionReason("");
                  }}
                  className={`w-full border-l-2 p-5 text-left transition ${
                    activeId === incident.id
                      ? "border-l-cyan-400 bg-cyan-400/[0.035]"
                      : "border-l-transparent hover:bg-white/[0.015]"
                  }`}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="min-w-0">
                      <p className="truncate text-sm font-semibold text-white">
                        {incident.title}
                      </p>

                      <p className="mt-1 font-mono text-[10px] text-slate-600">
                        INC-{incident.id}
                      </p>
                    </div>

                    <Badge
                      className={severityClass(
                        incident.severity,
                      )}
                    >
                      {incident.severity}
                    </Badge>
                  </div>

                  <div className="mt-3 flex items-center justify-between gap-3">
                    <Badge
                      className={statusClass(incident.status)}
                    >
                      {incident.status}
                    </Badge>

                    <span className="text-[10px] text-slate-600">
                      {formatDate(incident.updated_at)}
                    </span>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>

        <div className="security-surface overflow-hidden">
          {!activeIncident ? (
            <div className="flex min-h-[650px] items-center justify-center p-8 text-center">
              <div>
                <ShieldAlert className="mx-auto size-10 text-slate-700" />

                <p className="mt-4 text-sm text-slate-500">
                  Select an incident to investigate.
                </p>
              </div>
            </div>
          ) : (
            <>
              <div className="border-b border-slate-800/80 p-5 sm:p-6">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="font-mono text-[10px] text-slate-600">
                    INC-{activeIncident.id}
                  </span>

                  <Badge
                    className={severityClass(
                      activeIncident.severity,
                    )}
                  >
                    {activeIncident.severity}
                  </Badge>

                  <Badge
                    className={statusClass(
                      activeIncident.status,
                    )}
                  >
                    {activeIncident.status}
                  </Badge>
                </div>

                <h2 className="mt-4 text-xl font-semibold text-white">
                  {activeIncident.title}
                </h2>

                <p className="mt-2 text-sm leading-6 text-slate-500">
                  {activeIncident.description ||
                    "No incident description provided."}
                </p>

                <div className="mt-4 flex flex-wrap gap-4 text-[10px] text-slate-600">
                  <span>Agent #{activeIncident.agent_id}</span>

                  {activeAgent && (
                    <span>{activeAgent.name}</span>
                  )}

                  <span>
                    Created {formatDate(activeIncident.created_at)}
                  </span>

                  <span>
                    Updated {formatDate(activeIncident.updated_at)}
                  </span>
                </div>
              </div>

              <div className="grid gap-5 p-5 sm:p-6">
                <div>
                  <div className="flex items-center gap-2">
                    <Clock3 className="size-4 text-cyan-300" />

                    <h3 className="text-sm font-semibold text-white">
                      Investigation Timeline
                    </h3>
                  </div>

                  <div className="mt-4 space-y-3">
                    {timelineQuery.isLoading ? (
                      <LoaderCircle className="size-4 animate-spin text-cyan-400" />
                    ) : (timelineQuery.data ?? []).length === 0 ? (
                      <p className="text-xs text-slate-600">
                        No timeline entries yet.
                      </p>
                    ) : (
                      timelineQuery.data?.map((entry) => (
                        <div
                          key={entry.id}
                          className="relative rounded-xl border border-slate-800 bg-slate-950/40 p-4"
                        >
                          <div className="flex items-center justify-between gap-3">
                            <span className="text-[9px] font-semibold uppercase tracking-[0.15em] text-cyan-400">
                              {entry.entry_type.replaceAll(
                                "_",
                                " ",
                              )}
                            </span>

                            <span className="text-[10px] text-slate-600">
                              {formatDate(entry.created_at)}
                            </span>
                          </div>

                          <p className="mt-2 text-sm leading-6 text-slate-400">
                            {entry.description}
                          </p>
                        </div>
                      ))
                    )}
                  </div>
                </div>

                <div className="rounded-xl border border-slate-800 bg-slate-950/30 p-4">
                  <div className="flex items-center gap-2">
                    <MessageSquare className="size-4 text-cyan-300" />

                    <h3 className="text-sm font-semibold text-white">
                      Operator Note
                    </h3>
                  </div>

                  <textarea
                    value={note}
                    onChange={(event) =>
                      setNote(event.target.value)
                    }
                    placeholder="Record an investigation observation..."
                    rows={3}
                    className="mt-3 w-full resize-none rounded-xl border border-slate-800 bg-slate-950 px-3 py-3 text-sm text-slate-300 outline-none placeholder:text-slate-700 focus:border-cyan-400/40"
                  />

                  <button
                    type="button"
                    disabled={!note.trim() || addNote.isPending}
                    onClick={submitNote}
                    className="mt-3 inline-flex items-center gap-2 rounded-xl border border-cyan-400/20 bg-cyan-400/10 px-4 py-2.5 text-xs font-semibold text-cyan-300 transition hover:bg-cyan-400/15 disabled:cursor-not-allowed disabled:opacity-40"
                  >
                    {addNote.isPending ? (
                      <LoaderCircle className="size-4 animate-spin" />
                    ) : (
                      <MessageSquare className="size-4" />
                    )}

                    Add timeline note
                  </button>
                </div>

                <div className="rounded-xl border border-orange-400/10 bg-orange-400/[0.025] p-4">
                  <div className="flex items-center gap-2">
                    <ShieldAlert className="size-4 text-orange-300" />

                    <h3 className="text-sm font-semibold text-white">
                      Authorized Response
                    </h3>
                  </div>

                  <p className="mt-1 text-xs leading-5 text-slate-600">
                    Actions below execute existing SentinelX controls and
                    are recorded in the incident audit trail.
                  </p>

                  <div className="mt-4">
                    <label
                      htmlFor="response-action"
                      className="text-[9px] font-semibold uppercase tracking-[0.15em] text-slate-500"
                    >
                      Response action
                    </label>

                    <select
                      id="response-action"
                      value={actionType}
                      onChange={(event) => {
                        const nextActionType =
                          event.target.value as ResponseActionType;

                        setActionType(nextActionType);
                        setSelectedToolId("");
                        setSelectedApiKeyId("");
                      }}
                      className="mt-2 w-full rounded-xl border border-slate-800 bg-slate-950 px-3 py-2.5 text-xs text-slate-300 outline-none focus:border-orange-400/40"
                    >
                      <option value="SUSPEND_AGENT">
                        Suspend agent
                      </option>

                      <option value="DISABLE_TOOL">
                        Disable tool
                      </option>

                      <option value="ROTATE_AGENT_API_KEY">
                        Rotate API key
                      </option>
                    </select>
                  </div>

                  {actionType === "DISABLE_TOOL" && (
                    <div className="mt-3">
                      <label
                        htmlFor="target-tool"
                        className="text-[9px] font-semibold uppercase tracking-[0.15em] text-slate-500"
                      >
                        Tool target
                      </label>

                      {toolsQuery.isLoading ? (
                        <div className="mt-2 flex items-center gap-2 rounded-xl border border-slate-800 bg-slate-950 px-3 py-2.5 text-xs text-slate-600">
                          <LoaderCircle className="size-3.5 animate-spin text-cyan-400" />
                          Loading agent tools...
                        </div>
                      ) : tools.length === 0 ? (
                        <div className="mt-2 rounded-xl border border-orange-400/10 bg-orange-400/[0.025] px-3 py-2.5 text-xs text-orange-300">
                          No tools are available for this agent.
                        </div>
                      ) : (
                        <select
                          id="target-tool"
                          value={selectedToolId}
                          onChange={(event) =>
                            setSelectedToolId(event.target.value)
                          }
                          className="mt-2 w-full rounded-xl border border-slate-800 bg-slate-950 px-3 py-2.5 text-xs text-slate-300 outline-none focus:border-orange-400/40"
                        >
                          <option value="">
                            Select a tool...
                          </option>

                          {tools.map((tool) => (
                            <option
                              key={tool.id}
                              value={tool.id}
                            >
                              #{tool.id} — {tool.name}
                            </option>
                          ))}
                        </select>
                      )}
                    </div>
                  )}

                  {actionType === "ROTATE_AGENT_API_KEY" && (
                    <div className="mt-3">
                      <label
                        htmlFor="target-api-key"
                        className="text-[9px] font-semibold uppercase tracking-[0.15em] text-slate-500"
                      >
                        API key target
                      </label>

                      {apiKeysQuery.isLoading ? (
                        <div className="mt-2 flex items-center gap-2 rounded-xl border border-slate-800 bg-slate-950 px-3 py-2.5 text-xs text-slate-600">
                          <LoaderCircle className="size-3.5 animate-spin text-cyan-400" />
                          Loading API key metadata...
                        </div>
                      ) : apiKeys.length === 0 ? (
                        <div className="mt-2 rounded-xl border border-orange-400/10 bg-orange-400/[0.025] px-3 py-2.5 text-xs text-orange-300">
                          No API keys are available for this agent.
                        </div>
                      ) : (
                        <select
                          id="target-api-key"
                          value={selectedApiKeyId}
                          onChange={(event) =>
                            setSelectedApiKeyId(event.target.value)
                          }
                          className="mt-2 w-full rounded-xl border border-slate-800 bg-slate-950 px-3 py-2.5 text-xs text-slate-300 outline-none focus:border-orange-400/40"
                        >
                          <option value="">
                            Select an API key...
                          </option>

                          {apiKeys.map((apiKey) => (
                            <option
                              key={apiKey.id}
                              value={apiKey.id}
                            >
                              #{apiKey.id} —{" "}
                              {apiKey.is_active
                                ? "Active"
                                : "Inactive"}{" "}
                              — expires{" "}
                              {formatDate(apiKey.expires_at)}
                            </option>
                          ))}
                        </select>
                      )}

                      <p className="mt-2 text-[9px] text-slate-600">
                        Only API-key metadata is displayed. The existing
                        secret is never exposed.
                      </p>
                    </div>
                  )}

                  <input
                    value={actionReason}
                    onChange={(event) =>
                      setActionReason(event.target.value)
                    }
                    placeholder="Required reason for response action"
                    className="mt-4 w-full rounded-xl border border-slate-800 bg-slate-950 px-3 py-2.5 text-xs text-slate-300 outline-none placeholder:text-slate-700 focus:border-orange-400/40"
                  />

                  <button
                    type="button"
                    disabled={
                      !actionReason.trim() ||
                      targetMissing ||
                      responseAction.isPending ||
                      (actionType === "DISABLE_TOOL" &&
                        tools.length === 0) ||
                      (actionType === "ROTATE_AGENT_API_KEY" &&
                        apiKeys.length === 0)
                    }
                    onClick={executeAction}
                    className="mt-3 inline-flex w-full items-center justify-center gap-2 rounded-xl border border-orange-400/20 bg-orange-400/10 px-4 py-2.5 text-[10px] font-semibold uppercase tracking-[0.1em] text-orange-300 transition hover:bg-orange-400/15 disabled:cursor-not-allowed disabled:opacity-40"
                  >
                    {responseAction.isPending ? (
                      <LoaderCircle className="size-4 animate-spin" />
                    ) : actionType === "SUSPEND_AGENT" ? (
                      <UserRound className="size-4" />
                    ) : actionType === "DISABLE_TOOL" ? (
                      <Wrench className="size-4" />
                    ) : (
                      <RotateCcw className="size-4" />
                    )}

                    {actionType === "SUSPEND_AGENT"
                      ? "Suspend Agent"
                      : actionType === "DISABLE_TOOL"
                        ? "Disable Selected Tool"
                        : "Rotate Selected API Key"}
                  </button>
                </div>

                <div>
                  <div className="flex items-center gap-2">
                    <ShieldCheck className="size-4 text-emerald-300" />

                    <h3 className="text-sm font-semibold text-white">
                      Response Audit
                    </h3>
                  </div>

                  <div className="mt-4 space-y-2">
                    {actionsQuery.data?.length ? (
                      actionsQuery.data.map((action) => (
                        <div
                          key={action.id}
                          className="rounded-xl border border-slate-800 bg-slate-950/40 p-4"
                        >
                          <div className="flex flex-wrap items-center justify-between gap-2">
                            <span className="text-[10px] font-semibold uppercase tracking-[0.14em] text-slate-300">
                              {action.action_type.replaceAll(
                                "_",
                                " ",
                              )}
                            </span>

                            <span
                              className={`text-[9px] font-semibold uppercase tracking-[0.14em] ${
                                action.result === "SUCCESS"
                                  ? "text-emerald-300"
                                  : "text-red-300"
                              }`}
                            >
                              {action.result}
                            </span>
                          </div>

                          <p className="mt-2 text-xs text-slate-500">
                            {action.reason}
                          </p>

                          <p className="mt-2 text-[10px] text-slate-700">
                            Authorized by user #
                            {action.authorized_by_user_id}
                            {" · "}
                            {formatDate(action.created_at)}
                          </p>
                        </div>
                      ))
                    ) : (
                      <p className="text-xs text-slate-600">
                        No response actions recorded.
                      </p>
                    )}
                  </div>
                </div>

                {containedCount > 0 && (
                  <div className="flex items-center gap-2 rounded-xl border border-cyan-400/10 bg-cyan-400/[0.025] p-3 text-xs text-cyan-300">
                    <CheckCircle2 className="size-4" />

                    {containedCount} contained incident
                    {containedCount === 1 ? "" : "s"} in the current
                    queue.
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      </section>
    </div>
  );
}