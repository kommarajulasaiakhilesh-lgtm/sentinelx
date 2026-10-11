"use client";

import {
  useEffect,
  useState,
  type FormEvent,
  type ReactNode,
} from "react";
import {
  AlertTriangle,
  CheckCircle2,
  Gauge,
  LoaderCircle,
  LockKeyhole,
  Save,
  ShieldCheck,
  SlidersHorizontal,
} from "lucide-react";

import {
  useEffectiveRiskConfiguration,
  useGlobalRiskConfiguration,
  useMyRiskConfiguration,
  useSaveGlobalRiskConfiguration,
  useSaveMyRiskConfiguration,
} from "@/features/risk-configurations/use-risk-configurations";

import type {
  RiskScoringConfiguration,
  RiskScoringConfigurationUpdate,
} from "@/features/risk-configurations/risk-configurations-api";

type ConfigurationScope = "personal" | "global";

type ThresholdField =
  | "low_max"
  | "medium_max"
  | "high_max"
  | "critical_max";

const defaultConfiguration: RiskScoringConfigurationUpdate = {
  name: "My Risk Configuration",
  enabled: true,
  blocked_event_weight: 10,
  suspicious_event_weight: 20,
  policy_violation_weight: 15,
  score_cap: 100,
  low_max: 19,
  medium_max: 49,
  high_max: 79,
  critical_max: 100,
};

const numericFields = [
  {
    key: "blocked_event_weight",
    label: "Blocked event weight",
    description: "Points added for each blocked event.",
    min: 0,
  },
  {
    key: "suspicious_event_weight",
    label: "Suspicious event weight",
    description: "Points added for each suspicious event.",
    min: 0,
  },
  {
    key: "policy_violation_weight",
    label: "Policy violation weight",
    description: "Points added for each policy violation.",
    min: 0,
  },
  {
    key: "score_cap",
    label: "Maximum risk score",
    description: "The maximum score the risk engine can return.",
    min: 1,
  },
] as const;

type NumericField = (typeof numericFields)[number]["key"];

function getErrorMessage(error: unknown): string {
  return error instanceof Error
    ? error.message
    : "An unexpected error occurred.";
}

function toDraft(
  configuration: RiskScoringConfiguration,
): RiskScoringConfigurationUpdate {
  return {
    name: configuration.name,
    enabled: configuration.enabled,
    blocked_event_weight: configuration.blocked_event_weight,
    suspicious_event_weight: configuration.suspicious_event_weight,
    policy_violation_weight: configuration.policy_violation_weight,
    score_cap: configuration.score_cap,
    low_max: configuration.low_max,
    medium_max: configuration.medium_max,
    high_max: configuration.high_max,
    critical_max: configuration.critical_max,
  };
}

function FieldLabel({ children }: { children: ReactNode }) {
  return (
    <label className="mb-2 block text-[10px] font-semibold uppercase tracking-[0.15em] text-slate-500">
      {children}
    </label>
  );
}

function InputClass(): string {
  return "w-full rounded-xl border border-slate-800 bg-slate-950 px-3 py-2.5 text-sm text-slate-200 outline-none transition focus:border-cyan-400/40 disabled:cursor-not-allowed disabled:opacity-50";
}

export default function RiskConfigurationsPage() {
  const effectiveQuery = useEffectiveRiskConfiguration();
  const personalQuery = useMyRiskConfiguration();
  const globalQuery = useGlobalRiskConfiguration();

  const savePersonal = useSaveMyRiskConfiguration();
  const saveGlobal = useSaveGlobalRiskConfiguration();

  const [scope, setScope] = useState<ConfigurationScope>("personal");
  const [personalDraft, setPersonalDraft] =
    useState<RiskScoringConfigurationUpdate>(defaultConfiguration);
  const [globalDraft, setGlobalDraft] =
    useState<RiskScoringConfigurationUpdate>(defaultConfiguration);
  const [personalInitialized, setPersonalInitialized] = useState(false);
  const [formError, setFormError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  useEffect(() => {
    if (personalQuery.data) {
  // eslint-disable-next-line react-hooks/set-state-in-effect
  setPersonalDraft(toDraft(personalQuery.data));
  setPersonalInitialized(true);
} else if (
      personalQuery.isError &&
      effectiveQuery.data &&
      !personalInitialized
    ) {
      setPersonalDraft({
        ...toDraft(effectiveQuery.data),
        name: "My Risk Configuration",
      });
      setPersonalInitialized(true);
    } else if (
      personalQuery.isError &&
      !effectiveQuery.data &&
      !effectiveQuery.isLoading &&
      !personalInitialized
    ) {
      setPersonalInitialized(true);
    }
  }, [
    personalQuery.data,
    personalQuery.isError,
    effectiveQuery.data,
    effectiveQuery.isLoading,
    personalInitialized,
  ]);

  useEffect(() => {
    if (globalQuery.data) {
  // eslint-disable-next-line react-hooks/set-state-in-effect
  setGlobalDraft(toDraft(globalQuery.data));
}
  }, [globalQuery.data]);

  const activeDraft = scope === "personal" ? personalDraft : globalDraft;
  const activeSave = scope === "personal" ? savePersonal : saveGlobal;
  const activeQuery = scope === "personal" ? personalQuery : globalQuery;

  const isBusy =
    activeSave.isPending ||
    activeQuery.isLoading ||
    (scope === "personal" && !personalInitialized);

  function updateDraft<K extends keyof RiskScoringConfigurationUpdate>(
    key: K,
    value: RiskScoringConfigurationUpdate[K],
  ) {
    setFormError("");
    setSuccessMessage("");

    if (scope === "personal") {
      setPersonalDraft((current) => ({ ...current, [key]: value }));
    } else {
      setGlobalDraft((current) => ({ ...current, [key]: value }));
    }
  }

  function updateNumber(key: NumericField | ThresholdField, rawValue: string) {
    const value = rawValue === "" ? 0 : Number(rawValue);
    updateDraft(key, Number.isFinite(value) ? value : 0);
  }

  async function submitConfiguration(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setFormError("");
    setSuccessMessage("");

    const configuration: RiskScoringConfigurationUpdate = {
      ...activeDraft,
      name: activeDraft.name.trim(),
    };

    if (!configuration.name) {
      setFormError("Configuration name cannot be blank.");
      return;
    }

    const weights = [
      configuration.blocked_event_weight,
      configuration.suspicious_event_weight,
      configuration.policy_violation_weight,
    ];

    if (
      weights.some(
        (value) => !Number.isInteger(value) || value < 0,
      )
    ) {
      setFormError("Weights must be non-negative whole numbers.");
      return;
    }

    const numericValues = [
      configuration.score_cap,
      configuration.low_max,
      configuration.medium_max,
      configuration.high_max,
      configuration.critical_max,
    ];

    if (numericValues.some((value) => !Number.isInteger(value))) {
      setFormError("Score limits must be whole numbers.");
      return;
    }

    if (
      configuration.score_cap < 1 ||
      !(
        0 <= configuration.low_max &&
        configuration.low_max < configuration.medium_max &&
        configuration.medium_max < configuration.high_max &&
        configuration.high_max < configuration.critical_max
      )
    ) {
      setFormError(
        "Thresholds must increase in order: Low, Medium, High, Critical.",
      );
      return;
    }

    if (configuration.critical_max !== configuration.score_cap) {
      setFormError(
        "The Critical maximum must equal the maximum risk score.",
      );
      return;
    }

    try {
      if (scope === "personal") {
        await savePersonal.mutateAsync(configuration);
      } else {
        await saveGlobal.mutateAsync(configuration);
      }

      setSuccessMessage(
        scope === "personal"
          ? "Personal risk configuration saved."
          : "Global risk configuration saved.",
      );
    } catch (error) {
      setFormError(getErrorMessage(error));
    }
  }

  const effective = effectiveQuery.data;

  const globalAccessDenied =
    globalQuery.isError &&
    /403|forbidden|permission|administrator|admin/i.test(
      getErrorMessage(globalQuery.error),
    );

  const globalUnavailable =
    globalQuery.isError && !globalAccessDenied;

  return (
    <div className="space-y-6">
      <section className="security-surface relative overflow-hidden p-6 sm:p-7">
        <div className="security-grid absolute inset-0 opacity-20" />

        <div className="relative">
          <div className="flex flex-wrap items-center gap-2">
            <span className="inline-flex items-center gap-2 rounded-full border border-cyan-400/15 bg-cyan-400/5 px-3 py-1.5 text-[10px] font-semibold uppercase tracking-[0.18em] text-cyan-300">
              <SlidersHorizontal className="size-3.5" />
              Risk intelligence
            </span>

            <span className="rounded-full border border-white/[0.08] bg-white/[0.025] px-3 py-1.5 text-[10px] uppercase tracking-wider text-slate-500">
              Phase 19
            </span>
          </div>

          <h1 className="mt-5 text-2xl font-semibold tracking-tight text-slate-100 sm:text-3xl">
            Risk Scoring Configuration
          </h1>

          <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-400">
            Configure how security events contribute to agent risk scores
            and define the thresholds used to classify risk severity.
          </p>

          <div className="mt-5 flex flex-wrap items-center gap-2 text-xs text-slate-500">
            <ShieldCheck className="size-4 text-cyan-300" />
            <span>Server-side validation and access control</span>
          </div>
        </div>
      </section>

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <div className="security-surface p-5">
          <p className="text-[10px] font-semibold uppercase tracking-[0.15em] text-slate-500">
            Active configuration
          </p>
          <p className="mt-3 text-lg font-semibold text-slate-100">
            {effective?.name ?? "Unavailable"}
          </p>
          <p className="mt-2 text-xs text-slate-500">
            {effective
              ? effective.owner_id === null
                ? "Using global defaults"
                : "Using personal configuration"
              : effectiveQuery.isLoading
                ? "Loading effective settings..."
                : "Could not load effective settings"}
          </p>
        </div>

        <div className="security-surface p-5">
          <p className="text-[10px] font-semibold uppercase tracking-[0.15em] text-slate-500">
            Maximum score
          </p>
          <p className="mt-3 text-3xl font-semibold tabular-nums text-slate-100">
            {effective?.score_cap ?? "—"}
          </p>
          <p className="mt-2 text-xs text-slate-500">
            Upper bound enforced by the risk engine
          </p>
        </div>

        <div className="security-surface p-5">
          <p className="text-[10px] font-semibold uppercase tracking-[0.15em] text-slate-500">
            High-risk threshold
          </p>
          <p className="mt-3 text-3xl font-semibold tabular-nums text-orange-300">
            {effective?.high_max ?? "—"}
          </p>
          <p className="mt-2 text-xs text-slate-500">
            Upper boundary before Critical
          </p>
        </div>

        <div className="security-surface p-5">
          <p className="text-[10px] font-semibold uppercase tracking-[0.15em] text-slate-500">
            Critical threshold
          </p>
          <p className="mt-3 text-3xl font-semibold tabular-nums text-red-300">
            {effective?.critical_max ?? "—"}
          </p>
          <p className="mt-2 text-xs text-slate-500">
            Must equal the score cap
          </p>
        </div>
      </section>

      <section className="security-surface overflow-hidden">
        <div className="border-b border-white/[0.06] p-5 sm:p-6">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <h2 className="text-base font-semibold text-slate-100">
                Configuration editor
              </h2>
              <p className="mt-1 text-xs text-slate-500">
                Personal settings override global settings when enabled.
              </p>
            </div>

            <div className="flex rounded-xl border border-slate-800 bg-slate-950 p-1">
              <button
                type="button"
                onClick={() => {
                  setScope("personal");
                  setFormError("");
                  setSuccessMessage("");
                }}
                className={`rounded-lg px-3 py-2 text-xs font-medium transition ${
                  scope === "personal"
                    ? "bg-cyan-400/10 text-cyan-200"
                    : "text-slate-500 hover:text-slate-200"
                }`}
              >
                Personal
              </button>

              <button
                type="button"
                onClick={() => {
                  setScope("global");
                  setFormError("");
                  setSuccessMessage("");
                }}
                className={`rounded-lg px-3 py-2 text-xs font-medium transition ${
                  scope === "global"
                    ? "bg-cyan-400/10 text-cyan-200"
                    : "text-slate-500 hover:text-slate-200"
                }`}
              >
                Global · Admin
              </button>
            </div>
          </div>
        </div>

        {scope === "global" && globalAccessDenied ? (
          <div className="m-5 rounded-xl border border-amber-400/20 bg-amber-400/[0.06] p-5 sm:m-6">
            <div className="flex items-start gap-3">
              <LockKeyhole className="mt-0.5 size-5 shrink-0 text-amber-300" />
              <div>
                <h3 className="text-sm font-semibold text-amber-200">
                  Administrator access required
                </h3>
                <p className="mt-2 text-sm leading-6 text-slate-400">
                  Global risk settings are restricted by the backend to
                  administrators. You can still manage your personal
                  configuration.
                </p>
              </div>
            </div>
          </div>
        ) : scope === "global" && globalUnavailable ? (
          <div className="m-5 rounded-xl border border-red-400/20 bg-red-400/[0.05] p-5 sm:m-6">
            <h3 className="text-sm font-semibold text-red-200">
              Global configuration unavailable
            </h3>
            <p className="mt-2 text-sm leading-6 text-slate-400">
              {getErrorMessage(globalQuery.error)}. Check that the global
              configuration has been seeded and that the API is available.
            </p>
          </div>
        ) : (
          <form onSubmit={submitConfiguration} className="space-y-6 p-5 sm:p-6">
            <div className="grid gap-5 md:grid-cols-2">
              <div>
                <FieldLabel>Configuration name</FieldLabel>
                <input
                  className={InputClass()}
                  value={activeDraft.name}
                  maxLength={150}
                  required
                  onChange={(event) =>
                    updateDraft("name", event.target.value)
                  }
                  disabled={isBusy}
                />
              </div>

              <div>
                <FieldLabel>Configuration status</FieldLabel>
                <label className="flex min-h-[42px] items-center gap-3 rounded-xl border border-slate-800 bg-slate-950 px-3">
                  <input
                    type="checkbox"
                    checked={activeDraft.enabled}
                    onChange={(event) =>
                      updateDraft("enabled", event.target.checked)
                    }
                    disabled={isBusy}
                    className="size-4 accent-cyan-400"
                  />
                  <span className="text-sm text-slate-300">Enabled</span>
                  <span
                    className={`ml-auto rounded-full px-2 py-1 text-[10px] font-semibold uppercase ${
                      activeDraft.enabled
                        ? "bg-emerald-400/10 text-emerald-300"
                        : "bg-slate-800 text-slate-400"
                    }`}
                  >
                    {activeDraft.enabled ? "Active" : "Disabled"}
                  </span>
                </label>
              </div>
            </div>

            <div>
              <div className="mb-4 flex items-center gap-2">
                <Gauge className="size-4 text-cyan-300" />
                <h3 className="text-sm font-semibold text-slate-200">
                  Event scoring weights
                </h3>
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                {numericFields.map((field) => (
                  <div
                    key={field.key}
                    className="rounded-xl border border-white/[0.06] bg-white/[0.015] p-4"
                  >
                    <FieldLabel>{field.label}</FieldLabel>
                    <input
                      type="number"
                      min={field.min}
                      step={1}
                      required
                      className={InputClass()}
                      value={activeDraft[field.key]}
                      onChange={(event) =>
                        updateNumber(field.key, event.target.value)
                      }
                      disabled={isBusy}
                    />
                    <p className="mt-2 text-xs leading-5 text-slate-500">
                      {field.description}
                    </p>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <div className="mb-4 flex items-center gap-2">
                <AlertTriangle className="size-4 text-amber-300" />
                <h3 className="text-sm font-semibold text-slate-200">
                  Risk severity thresholds
                </h3>
              </div>

              <p className="mb-4 text-xs leading-5 text-slate-500">
                The thresholds must be strictly increasing. Critical must
                equal the configured maximum score.
              </p>

              <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                {(
                  [
                    {
                      key: "low_max",
                      label: "Low maximum",
                      color: "text-emerald-300",
                    },
                    {
                      key: "medium_max",
                      label: "Medium maximum",
                      color: "text-amber-300",
                    },
                    {
                      key: "high_max",
                      label: "High maximum",
                      color: "text-orange-300",
                    },
                    {
                      key: "critical_max",
                      label: "Critical maximum",
                      color: "text-red-300",
                    },
                  ] satisfies {
                    key: ThresholdField;
                    label: string;
                    color: string;
                  }[]
                ).map((field) => (
                  <div
                    key={field.key}
                    className="rounded-xl border border-white/[0.06] bg-white/[0.015] p-4"
                  >
                    <FieldLabel>
                      <span className={field.color}>{field.label}</span>
                    </FieldLabel>
                    <input
                      type="number"
                      min={0}
                      step={1}
                      required
                      className={InputClass()}
                      value={activeDraft[field.key]}
                      onChange={(event) =>
                        updateNumber(field.key, event.target.value)
                      }
                      disabled={isBusy}
                    />
                  </div>
                ))}
              </div>

              <div className="mt-4 grid gap-2 sm:grid-cols-4">
                {[
                  {
                    label: "LOW",
                    value: `0–${activeDraft.low_max}`,
                    color:
                      "border-emerald-400/20 bg-emerald-400/[0.04] text-emerald-300",
                  },
                  {
                    label: "MEDIUM",
                    value: `${activeDraft.low_max + 1}–${activeDraft.medium_max}`,
                    color:
                      "border-amber-400/20 bg-amber-400/[0.04] text-amber-300",
                  },
                  {
                    label: "HIGH",
                    value: `${activeDraft.medium_max + 1}–${activeDraft.high_max}`,
                    color:
                      "border-orange-400/20 bg-orange-400/[0.04] text-orange-300",
                  },
                  {
                    label: "CRITICAL",
                    value: `${activeDraft.high_max + 1}–${activeDraft.critical_max}`,
                    color:
                      "border-red-400/20 bg-red-400/[0.04] text-red-300",
                  },
                ].map((level) => (
                  <div
                    key={level.label}
                    className={`rounded-xl border p-3 ${level.color}`}
                  >
                    <p className="text-[10px] font-semibold tracking-[0.12em]">
                      {level.label}
                    </p>
                    <p className="mt-2 text-lg font-semibold tabular-nums">
                      {level.value}
                    </p>
                  </div>
                ))}
              </div>
            </div>

            {formError && (
              <div
                role="alert"
                className="rounded-xl border border-red-400/20 bg-red-400/[0.06] p-3 text-sm text-red-300"
              >
                {formError}
              </div>
            )}

            {successMessage && (
              <div
                role="status"
                className="flex items-center gap-2 rounded-xl border border-emerald-400/20 bg-emerald-400/[0.06] p-3 text-sm text-emerald-300"
              >
                <CheckCircle2 className="size-4 shrink-0" />
                {successMessage}
              </div>
            )}

            <div className="flex flex-wrap items-center justify-between gap-4 border-t border-white/[0.06] pt-5">
              <p className="max-w-xl text-xs leading-5 text-slate-500">
                Saving validates the configuration on both the frontend and
                backend. Changes affect scoring when this configuration is
                selected by the risk-scoring service.
              </p>

              <button
                type="submit"
                disabled={isBusy}
                className="inline-flex items-center justify-center gap-2 rounded-xl border border-cyan-300/20 bg-cyan-400/10 px-4 py-2.5 text-sm font-semibold text-cyan-200 transition hover:bg-cyan-400/15 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {activeSave.isPending ? (
                  <LoaderCircle className="size-4 animate-spin" />
                ) : (
                  <Save className="size-4" />
                )}
                {activeSave.isPending
                  ? "Saving..."
                  : "Save configuration"}
              </button>
            </div>
          </form>
        )}
      </section>
    </div>
  );
}
