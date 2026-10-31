
"use client";

import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  LoaderCircle,
  Plus,
  RefreshCw,
  ShieldCheck,
  Trash2,
  ToggleLeft,
  ToggleRight,
  XCircle,
} from "lucide-react";
import { useState, type FormEvent } from "react";

import {
  useCreateDetectionRule,
  useDeleteDetectionRule,
  useDetectionRules,
  useUpdateDetectionRule,
} from "@/features/detection-rules/use-detection-rules";
import type {
  DetectionRule,
  DetectionRulePayload,
  DetectionSeverity,
} from "@/features/detection-rules/detection-rules-api";

const initialConditions = '{\n  "event_type": "TOOL_ACTION"\n}';

function formatDate(value: string) {
  const date = new Date(value);

  return Number.isNaN(date.getTime())
    ? value
    : new Intl.DateTimeFormat("en-IN", {
        dateStyle: "medium",
        timeStyle: "short",
      }).format(date);
}

function severityClass(severity: string) {
  switch (severity) {
    case "CRITICAL":
      return "border-red-400/20 bg-red-400/10 text-red-600";
    case "HIGH":
      return "border-orange-400/20 bg-orange-400/10 text-orange-300";
    case "MEDIUM":
      return "border-amber-400/20 bg-amber-400/10 text-amber-600";
    default:
      return "border-slate-700 bg-slate-100/50 text-slate-700";
  }
}

function getErrorMessage(error: unknown) {
  return error instanceof Error ? error.message : "An unexpected error occurred.";
}

function FieldLabel({ children }: { children: React.ReactNode }) {
  return (
    <span className="mb-2 block text-[10px] font-semibold uppercase tracking-[0.15em] text-slate-500">
      {children}
    </span>
  );
}

function InputClass() {
  return "w-full rounded-xl border border-slate-800 bg-slate-100 px-3 py-2.5 text-sm text-slate-800 outline-none placeholder:text-slate-400 focus:border-indigo-400/40";
}

export default function DetectionRulesPage() {
  const rulesQuery = useDetectionRules();
  const createRule = useCreateDetectionRule();
  const updateRule = useUpdateDetectionRule();
  const deleteRule = useDeleteDetectionRule();

  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [severity, setSeverity] = useState<DetectionSeverity>("HIGH");
  const [alertType, setAlertType] = useState("DETECTION_RULE");
  const [title, setTitle] = useState("");
  const [conditionsText, setConditionsText] = useState(initialConditions);
  const [threshold, setThreshold] = useState("1");
  const [windowSeconds, setWindowSeconds] = useState("0");
  const [formError, setFormError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [pendingDelete, setPendingDelete] = useState<number | null>(null);

  const rules = rulesQuery.data ?? [];
  const enabledCount = rules.filter((rule) => rule.enabled).length;
  const disabledCount = rules.length - enabledCount;
  const criticalCount = rules.filter(
    (rule) => rule.severity === "CRITICAL",
  ).length;

  async function submitRule(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setFormError("");
    setSuccessMessage("");

    let conditions: DetectionRulePayload["conditions"];

    try {
      const parsed: unknown = JSON.parse(conditionsText);

      if (
        parsed === null ||
        typeof parsed !== "object" ||
        Array.isArray(parsed) ||
        Object.keys(parsed).length === 0
      ) {
        throw new Error("Conditions must be a non-empty JSON object.");
      }

      conditions = parsed as DetectionRulePayload["conditions"];
    } catch (error) {
      setFormError(
        error instanceof Error
          ? `Invalid conditions JSON: ${error.message}`
          : "Conditions must be valid JSON.",
      );
      return;
    }

    const thresholdValue = Number(threshold);
    const windowValue = Number(windowSeconds);

    if (
      !Number.isInteger(thresholdValue) ||
      thresholdValue < 1 ||
      !Number.isInteger(windowValue) ||
      windowValue < 0
    ) {
      setFormError("Threshold must be at least 1 and the time window cannot be negative.");
      return;
    }

    const payload: DetectionRulePayload = {
      name: name.trim(),
      description: description.trim() || null,
      enabled: true,
      severity,
      alert_type: alertType.trim(),
      title: title.trim(),
      conditions,
      threshold: thresholdValue,
      window_seconds: windowValue,
    };

    try {
      await createRule.mutateAsync(payload);
      setName("");
      setDescription("");
      setSeverity("HIGH");
      setAlertType("DETECTION_RULE");
      setTitle("");
      setConditionsText(initialConditions);
      setThreshold("1");
      setWindowSeconds("0");
      setSuccessMessage("Detection rule created successfully.");
    } catch (error) {
      setFormError(getErrorMessage(error));
    }
  }

  async function toggleRule(rule: DetectionRule) {
    setFormError("");
    setSuccessMessage("");

    try {
      await updateRule.mutateAsync({
        id: rule.id,
        enabled: !rule.enabled,
      });
      setSuccessMessage(
        `Rule "${rule.name}" ${rule.enabled ? "disabled" : "enabled"}.`,
      );
    } catch (error) {
      setFormError(getErrorMessage(error));
    }
  }

  async function removeRule(rule: DetectionRule) {
    const confirmed = window.confirm(
      `Delete the rule "${rule.name}"? This cannot be undone.`,
    );

    if (!confirmed) return;

    setPendingDelete(rule.id);
    setFormError("");
    setSuccessMessage("");

    try {
      await deleteRule.mutateAsync(rule.id);
      setSuccessMessage(`Rule "${rule.name}" deleted.`);
    } catch (error) {
      setFormError(getErrorMessage(error));
    } finally {
      setPendingDelete(null);
    }
  }

  return (
    <div className="space-y-6 sm:space-y-8">
      <section className="relative overflow-hidden rounded-2xl border border-indigo-400/10 bg-indigo-400/[0.025] p-6 sm:p-8">
        <div className="security-grid pointer-events-none absolute inset-0 opacity-20" />
        <div className="relative">
          <div className="inline-flex items-center gap-2 rounded-full border border-indigo-400/20 bg-indigo-400/[0.06] px-3 py-1.5 text-[10px] font-semibold uppercase tracking-[0.18em] text-indigo-600">
            <Activity className="size-3.5" />
            Detection Engineering
          </div>

          <h1 className="mt-5 text-2xl font-semibold tracking-tight text-slate-900 sm:text-3xl">
            Detection Rules
          </h1>

          <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
            Configure deterministic security rules, inspect their conditions,
            and control which rules are active for your agents.
          </p>
        </div>
      </section>

      <section className="grid gap-3 sm:grid-cols-3">
        {[
          { label: "Total rules", value: rules.length, detail: "Configured rules", Icon: ShieldCheck },
          { label: "Enabled", value: enabledCount, detail: "Eligible for detection", Icon: CheckCircle2 },
          { label: "Critical rules", value: criticalCount, detail: `${disabledCount} disabled`, Icon: AlertTriangle },
        ].map(({ label, value, detail, Icon }) => (
          <article key={label} className="security-surface p-5">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-500">
                  {label}
                </p>
                <p className="mt-3 text-3xl font-semibold text-slate-900">
                  {value}
                </p>
                <p className="mt-1 text-xs text-slate-500">{detail}</p>
              </div>
              <div className="rounded-xl border border-slate-800 bg-slate-100/60 p-3">
                <Icon className="size-5 text-indigo-600" />
              </div>
            </div>
          </article>
        ))}
      </section>

      {(formError || createRule.isError || updateRule.isError || deleteRule.isError) && (
        <div role="alert" className="flex items-start gap-3 rounded-xl border border-red-400/20 bg-red-400/[0.05] p-4 text-sm text-red-600">
          <XCircle className="mt-0.5 size-4 shrink-0" />
          <span>{formError || "The requested operation failed."}</span>
        </div>
      )}

      {successMessage && (
        <div role="status" className="flex items-center gap-3 rounded-xl border border-emerald-400/20 bg-emerald-400/[0.04] p-4 text-sm text-emerald-600">
          <CheckCircle2 className="size-4 shrink-0" />
          {successMessage}
        </div>
      )}

      <section className="security-surface p-5 sm:p-6">
        <div className="flex items-center gap-3">
          <div className="rounded-xl border border-indigo-400/20 bg-indigo-400/[0.06] p-2.5">
            <Plus className="size-4 text-indigo-600" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-slate-900">Create detection rule</h2>
            <p className="mt-1 text-xs text-slate-500">
              Conditions must be a non-empty JSON object supported by the backend.
            </p>
          </div>
        </div>

        <form onSubmit={submitRule} className="mt-6 grid gap-4 md:grid-cols-2">
          <label>
            <FieldLabel>Rule name</FieldLabel>
            <input required maxLength={150} value={name} onChange={(event) => setName(event.target.value)} className={InputClass()} placeholder="Repeated blocked tool actions" />
          </label>

          <label>
            <FieldLabel>Alert title</FieldLabel>
            <input required maxLength={200} value={title} onChange={(event) => setTitle(event.target.value)} className={InputClass()} placeholder="Suspicious tool activity detected" />
          </label>

          <label>
            <FieldLabel>Alert type</FieldLabel>
            <input required maxLength={100} value={alertType} onChange={(event) => setAlertType(event.target.value)} className={InputClass()} placeholder="DETECTION_RULE" />
          </label>

          <label>
            <FieldLabel>Severity</FieldLabel>
            <select value={severity} onChange={(event) => setSeverity(event.target.value as DetectionSeverity)} className={InputClass()}>
              <option value="LOW">Low</option>
              <option value="MEDIUM">Medium</option>
              <option value="HIGH">High</option>
              <option value="CRITICAL">Critical</option>
            </select>
          </label>

          <label>
            <FieldLabel>Threshold — matching events</FieldLabel>
            <input type="number" required min={1} max={1000000} value={threshold} onChange={(event) => setThreshold(event.target.value)} className={InputClass()} />
          </label>

          <label>
            <FieldLabel>Time window — seconds (0 = no lower time limit)</FieldLabel>
            <input type="number" required min={0} max={31536000} value={windowSeconds} onChange={(event) => setWindowSeconds(event.target.value)} className={InputClass()} />
          </label>

          <label className="md:col-span-2">
            <FieldLabel>Description (optional)</FieldLabel>
            <textarea rows={2} value={description} onChange={(event) => setDescription(event.target.value)} className={InputClass()} placeholder="Explain the activity this rule is intended to detect." />
          </label>

          <label className="md:col-span-2">
            <FieldLabel>Conditions — JSON</FieldLabel>
            <textarea required rows={5} value={conditionsText} onChange={(event) => setConditionsText(event.target.value)} spellCheck={false} className={`${InputClass()} font-mono text-xs leading-6`} />
            <span className="mt-2 block text-[11px] leading-5 text-slate-500">
              Supported fields: event_type, action, decision, reason, agent_id, policy_id.
              Values can be strings, integers, or lists of values.
            </span>
          </label>

          <div className="md:col-span-2">
            <button type="submit" disabled={createRule.isPending} className="inline-flex items-center gap-2 rounded-xl border border-indigo-400/20 bg-indigo-400/10 px-5 py-3 text-xs font-semibold text-indigo-600 transition hover:bg-indigo-400/15 disabled:cursor-not-allowed disabled:opacity-50">
              {createRule.isPending ? <LoaderCircle className="size-4 animate-spin" /> : <Plus className="size-4" />}
              {createRule.isPending ? "Creating rule..." : "Create rule"}
            </button>
          </div>
        </form>
      </section>

      <section className="security-surface overflow-hidden">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800/80 p-5">
          <div>
            <h2 className="text-lg font-semibold text-slate-900">Configured rules</h2>
            <p className="mt-1 text-xs text-slate-500">Rules returned for your authenticated account.</p>
          </div>
          <button type="button" onClick={() => void rulesQuery.refetch()} disabled={rulesQuery.isFetching} className="inline-flex items-center gap-2 rounded-lg border border-slate-800 px-3 py-2 text-xs text-slate-600 transition hover:border-indigo-400/20 hover:text-indigo-600 disabled:opacity-50">
            <RefreshCw className={`size-3.5 ${rulesQuery.isFetching ? "animate-spin" : ""}`} />
            Refresh
          </button>
        </div>

        {rulesQuery.isLoading ? (
          <div className="flex min-h-48 items-center justify-center gap-3 text-sm text-slate-500">
            <LoaderCircle className="size-5 animate-spin text-indigo-600" />
            Loading detection rules...
          </div>
        ) : rulesQuery.isError ? (
          <div className="p-8 text-center">
            <XCircle className="mx-auto size-8 text-red-600" />
            <p className="mt-3 text-sm font-semibold text-slate-900">Rules unavailable</p>
            <p className="mt-2 text-xs text-slate-500">{getErrorMessage(rulesQuery.error)}</p>
            <button type="button" onClick={() => void rulesQuery.refetch()} className="mt-4 rounded-lg border border-slate-700 px-4 py-2 text-xs text-slate-700">Try again</button>
          </div>
        ) : rules.length === 0 ? (
          <div className="p-10 text-center">
            <ShieldCheck className="mx-auto size-9 text-slate-500" />
            <p className="mt-4 text-sm font-semibold text-slate-900">No custom rules yet</p>
            <p className="mt-2 text-xs text-slate-500">Create a rule above to begin configuring deterministic detection.</p>
          </div>
        ) : (
          <div className="divide-y divide-slate-800/70">
            {rules.map((rule) => (
              <article key={rule.id} className="p-5 sm:p-6">
                <div className="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
                  <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="font-mono text-[10px] text-slate-500">RULE-{rule.id}</span>
                      <span className={`rounded-full border px-2.5 py-1 text-[9px] font-semibold uppercase tracking-[0.12em] ${severityClass(rule.severity)}`}>{rule.severity}</span>
                      <span className={`rounded-full border px-2.5 py-1 text-[9px] font-semibold uppercase tracking-[0.12em] ${rule.enabled ? "border-emerald-400/20 bg-emerald-400/10 text-emerald-600" : "border-slate-700 bg-slate-100/50 text-slate-600"}`}>
                        {rule.enabled ? "Enabled" : "Disabled"}
                      </span>
                    </div>

                    <h3 className="mt-3 text-base font-semibold text-slate-900">{rule.name}</h3>
                    <p className="mt-1 text-sm text-slate-600">{rule.title}</p>
                    {rule.description && <p className="mt-2 text-xs leading-5 text-slate-500">{rule.description}</p>}

                    <div className="mt-4 grid gap-3 sm:grid-cols-3">
                      <div className="rounded-lg border border-slate-800 bg-slate-100/50 p-3">
                        <p className="text-[9px] uppercase tracking-[0.14em] text-slate-500">Alert type</p>
                        <p className="mt-1 break-words text-xs text-slate-700">{rule.alert_type}</p>
                      </div>
                      <div className="rounded-lg border border-slate-800 bg-slate-100/50 p-3">
                        <p className="text-[9px] uppercase tracking-[0.14em] text-slate-500">Threshold</p>
                        <p className="mt-1 text-xs text-slate-700">{rule.threshold} event(s) · {rule.window_seconds === 0 ? "No lower time limit" : `${rule.window_seconds}s window`}</p>
                      </div>
                      <div className="rounded-lg border border-slate-800 bg-slate-100/50 p-3">
                        <p className="text-[9px] uppercase tracking-[0.14em] text-slate-500">Updated</p>
                        <p className="mt-1 text-xs text-slate-700">{formatDate(rule.updated_at)}</p>
                      </div>
                    </div>

                    <details className="mt-4">
                      <summary className="cursor-pointer text-xs font-medium text-indigo-600 hover:text-indigo-600">Inspect matching conditions</summary>
                      <pre className="mt-3 overflow-x-auto rounded-xl border border-slate-800 bg-slate-100 p-4 text-xs leading-5 text-slate-700">{(() => {
                        try {
                          return JSON.stringify(JSON.parse(rule.conditions ?? "null"), null, 2);
                        } catch {
                          return rule.conditions ?? "No conditions stored";
                        }
                      })()}</pre>
                    </details>
                  </div>

                  <div className="flex shrink-0 flex-wrap gap-2 xl:flex-col">
                    <button type="button" onClick={() => void toggleRule(rule)} disabled={updateRule.isPending} className="inline-flex items-center gap-2 rounded-lg border border-slate-700 px-3 py-2.5 text-xs text-slate-700 transition hover:border-indigo-400/30 hover:text-indigo-600 disabled:opacity-50">
                      {rule.enabled ? <ToggleRight className="size-4 text-emerald-600" /> : <ToggleLeft className="size-4" />}
                      {rule.enabled ? "Disable" : "Enable"}
                    </button>
                    <button type="button" onClick={() => void removeRule(rule)} disabled={deleteRule.isPending || pendingDelete === rule.id} className="inline-flex items-center gap-2 rounded-lg border border-red-400/15 px-3 py-2.5 text-xs text-red-600 transition hover:border-red-400/30 hover:bg-red-400/[0.05] disabled:opacity-50">
                      {pendingDelete === rule.id ? <LoaderCircle className="size-4 animate-spin" /> : <Trash2 className="size-4" />}
                      Delete
                    </button>
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
