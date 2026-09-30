"use client";

import type { ReactNode } from "react";
import {
  AlertTriangle,
  CheckCircle2,
  Clock3,
  FlaskConical,
  LoaderCircle,
  Play,
  ShieldAlert,
  ShieldCheck,
  Target,
  XCircle,
} from "lucide-react";
import { useState } from "react";

import { useSecurityTests } from "@/features/security-tests/use-security-tests";
import type { SecurityTestScenario } from "@/types/api";

function StatCard({
  label,
  value,
  detail,
  icon,
  tone = "cyan",
}: {
  label: string;
  value: string | number;
  detail: string;
  icon: ReactNode;
  tone?: "cyan" | "emerald" | "red" | "violet";
}) {
  const toneClasses = {
    cyan: "border-cyan-400/15 bg-cyan-400/10 text-cyan-300",
    emerald: "border-emerald-400/15 bg-emerald-400/10 text-emerald-300",
    red: "border-red-400/15 bg-red-400/10 text-red-300",
    violet: "border-violet-400/15 bg-violet-400/10 text-violet-300",
  };

  return (
    <article className="security-surface security-surface-hover relative overflow-hidden p-5">
      <div
        className={`pointer-events-none absolute -right-8 -top-8 size-24 rounded-full blur-2xl ${
          tone === "red"
            ? "bg-red-400/5"
            : tone === "violet"
              ? "bg-violet-400/5"
              : tone === "emerald"
                ? "bg-emerald-400/5"
                : "bg-cyan-400/5"
        }`}
      />

      <div className="relative flex items-start justify-between gap-4">
        <div>
          <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-500">
            {label}
          </p>

          <p className="mt-3 text-3xl font-semibold tracking-tight text-white">
            {value}
          </p>

          <p className="mt-1 text-xs text-slate-500">{detail}</p>
        </div>

        <div className={`rounded-xl border p-3 ${toneClasses[tone]}`}>
          {icon}
        </div>
      </div>
    </article>
  );
}

function getCategoryClass(category: string) {
  switch (category.toUpperCase()) {
    case "PROMPT_INJECTION":
      return "border-red-400/20 bg-red-400/10 text-red-300";

    case "UNAUTHORIZED_TOOL":
      return "border-orange-400/20 bg-orange-400/10 text-orange-300";

    case "POLICY_BYPASS":
      return "border-amber-400/20 bg-amber-400/10 text-amber-300";

    case "RATE_LIMIT":
      return "border-violet-400/20 bg-violet-400/10 text-violet-300";

    case "REPEATED_BLOCK":
      return "border-blue-400/20 bg-blue-400/10 text-blue-300";

    case "SUSPICIOUS_ACTION":
      return "border-yellow-400/20 bg-yellow-400/10 text-yellow-300";

    default:
      return "border-slate-700 bg-slate-900/60 text-slate-300";
  }
}

function formatCategory(category: string) {
  return category.replaceAll("_", " ");
}

function formatDate(value?: string) {
  if (!value) {
    return "Unknown";
  }

  return new Date(value).toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

function DecisionBadge({
  label,
  tone,
}: {
  label: string;
  tone: "expected" | "actual" | "passed" | "failed";
}) {
  const classes = {
    expected: "border-slate-700 bg-slate-900 text-slate-300",
    actual: "border-cyan-400/15 bg-cyan-400/10 text-cyan-300",
    passed: "border-emerald-400/20 bg-emerald-400/10 text-emerald-300",
    failed: "border-red-400/20 bg-red-400/10 text-red-300",
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[9px] font-semibold uppercase tracking-[0.1em] ${classes[tone]}`}
    >
      {label}
    </span>
  );
}

function PipelineStage({
  number,
  label,
  detail,
}: {
  number: string;
  label: string;
  detail: string;
}) {
  return (
    <div className="relative flex-1 rounded-xl border border-slate-800/80 bg-slate-950/50 p-4">
      <div className="flex items-center gap-3">
        <span className="flex size-7 shrink-0 items-center justify-center rounded-lg border border-violet-400/15 bg-violet-400/10 font-mono text-[10px] font-semibold text-violet-300">
          {number}
        </span>

        <div className="min-w-0">
          <p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-slate-300">
            {label}
          </p>

          <p className="mt-1 text-[10px] leading-4 text-slate-600">
            {detail}
          </p>
        </div>
      </div>
    </div>
  );
}

function ScenarioRow({
  scenario,
  isRunning,
  isSelected,
  onRun,
}: {
  scenario: SecurityTestScenario;
  isRunning: boolean;
  isSelected: boolean;
  onRun: (scenario: SecurityTestScenario) => void;
}) {
  return (
    <article className="group px-5 py-5 transition-colors hover:bg-white/[0.015] sm:px-6">
      <div className="flex flex-col gap-5 xl:flex-row xl:items-center xl:justify-between">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <span className="flex size-7 items-center justify-center rounded-lg border border-violet-400/15 bg-violet-400/10 text-violet-300">
              <Target className="size-3.5" />
            </span>

            <h3 className="font-medium text-white">{scenario.name}</h3>

            <span
              className={`rounded-full border px-2.5 py-1 text-[9px] font-semibold uppercase tracking-[0.12em] ${getCategoryClass(
                scenario.category,
              )}`}
            >
              {formatCategory(scenario.category)}
            </span>

            <span
              className={`rounded-full border px-2.5 py-1 text-[9px] font-semibold uppercase tracking-[0.12em] ${
                scenario.enabled
                  ? "border-emerald-400/20 bg-emerald-400/10 text-emerald-300"
                  : "border-slate-700 bg-slate-900 text-slate-500"
              }`}
            >
              {scenario.enabled ? "Enabled" : "Disabled"}
            </span>
          </div>

          <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-400">
            {scenario.description || "No scenario description provided."}
          </p>

          <div className="mt-4 flex flex-wrap gap-x-5 gap-y-2 text-[10px] text-slate-600">
            <span>
              Expected{" "}
              <span className="text-slate-400">
                {scenario.expected_decision}
              </span>
            </span>

            {scenario.tool_name && (
              <span>
                Tool <span className="text-slate-400">{scenario.tool_name}</span>
              </span>
            )}

            {scenario.action && (
              <span>
                Action <span className="text-slate-400">{scenario.action}</span>
              </span>
            )}

            {scenario.resource && (
              <span>
                Resource{" "}
                <span className="text-slate-400">{scenario.resource}</span>
              </span>
            )}

            <span>
              Created{" "}
              <span className="text-slate-400">
                {formatDate(scenario.created_at)}
              </span>
            </span>
          </div>
        </div>

        <button
          type="button"
          disabled={!scenario.enabled || isRunning}
          onClick={() => onRun(scenario)}
          className="inline-flex shrink-0 items-center justify-center gap-2 rounded-xl border border-violet-400/20 bg-violet-400/10 px-4 py-2.5 text-xs font-semibold text-violet-300 transition-colors hover:bg-violet-400/15 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-violet-400/50 disabled:cursor-not-allowed disabled:opacity-40"
        >
          {isSelected && isRunning ? (
            <>
              <LoaderCircle className="size-4 animate-spin" />
              Executing
            </>
          ) : (
            <>
              <Play className="size-4" />
              Run Test
            </>
          )}
        </button>
      </div>
    </article>
  );
}

export default function SecurityTestsPage() {
  const {
    scenarios,
    isLoading,
    isError,
    runScenario,
    isRunning,
    lastRun,
    runError,
  } = useSecurityTests();

  const [selectedScenario, setSelectedScenario] =
    useState<number | null>(null);

  const enabledScenarios = scenarios.filter((scenario) => scenario.enabled);

  const categories = new Set(
    scenarios.map((scenario) => scenario.category),
  );

  const passedLastRun = lastRun?.result === "PASSED";

  async function handleRun(scenario: SecurityTestScenario) {
    setSelectedScenario(scenario.id);

    try {
      await runScenario(scenario.id);
    } finally {
      setSelectedScenario(null);
    }
  }

  const resultTone =
    lastRun?.result === "PASSED"
      ? "emerald"
      : lastRun
        ? "red"
        : "violet";

  return (
    <main className="space-y-6 sm:space-y-8">
      <section className="relative overflow-hidden rounded-2xl border border-violet-400/10 bg-violet-400/[0.025] p-6 sm:p-8">
        <div className="security-grid absolute inset-0 opacity-20" />

        <div className="pointer-events-none absolute -right-24 -top-24 size-64 rounded-full bg-violet-400/5 blur-3xl" />

        <div className="relative">
          <div className="flex flex-wrap items-center gap-3">
            <span className="inline-flex items-center gap-2 rounded-full border border-violet-400/20 bg-violet-400/[0.06] px-3 py-1.5 text-[10px] font-semibold uppercase tracking-[0.18em] text-violet-300">
              <FlaskConical className="size-3.5" />
              Security Testing
            </span>

            <span className="inline-flex items-center gap-2 text-[10px] font-medium uppercase tracking-[0.16em] text-emerald-400">
              <span className="size-1.5 animate-pulse rounded-full bg-emerald-400" />
              Simulation engine online
            </span>
          </div>

          <div className="mt-5 flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <h1 className="text-2xl font-semibold tracking-tight text-white sm:text-3xl">
                Security Testing &amp; Attack Simulation
              </h1>

              <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">
                Execute controlled attack scenarios against SentinelX defenses
                and verify that runtime security controls respond as expected.
              </p>
            </div>

            <div className="flex shrink-0 items-center gap-3 rounded-xl border border-violet-400/10 bg-violet-400/[0.035] px-4 py-3">
              <ShieldCheck className="size-4 text-violet-300" />

              <div>
                <p className="text-[9px] font-semibold uppercase tracking-[0.16em] text-violet-400">
                  Test boundary
                </p>

                <p className="mt-0.5 text-xs text-slate-400">
                  Controlled simulation only
                </p>
              </div>
            </div>
          </div>

          <div className="mt-7 grid gap-2 sm:grid-cols-4">
            <PipelineStage
              number="01"
              label="Scenario"
              detail="Select controlled test"
            />
            <PipelineStage
              number="02"
              label="Simulation"
              detail="Execute attack pattern"
            />
            <PipelineStage
              number="03"
              label="Enforcement"
              detail="Observe security controls"
            />
            <PipelineStage
              number="04"
              label="Result"
              detail="Compare expected vs actual"
            />
          </div>
        </div>
      </section>

      <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          label="Scenarios"
          value={isLoading ? "—" : isError ? "!" : scenarios.length}
          detail="Registered security tests"
          icon={<FlaskConical className="size-5" />}
        />

        <StatCard
          label="Enabled"
          value={
            isLoading ? "—" : isError ? "!" : enabledScenarios.length
          }
          detail="Ready for execution"
          icon={<CheckCircle2 className="size-5" />}
          tone="emerald"
        />

        <StatCard
          label="Attack Types"
          value={isLoading ? "—" : isError ? "!" : categories.size}
          detail="Simulation categories"
          icon={<Target className="size-5" />}
          tone="violet"
        />

        <StatCard
          label="Last Result"
          value={
            isLoading
              ? "—"
              : isError
                ? "!"
                : lastRun?.result || "READY"
          }
          detail={
            lastRun ? `Scenario #${lastRun.scenario_id}` : "No test executed yet"
          }
          icon={
            lastRun?.result === "PASSED" ? (
              <ShieldCheck className="size-5" />
            ) : (
              <ShieldAlert className="size-5" />
            )
          }
          tone={resultTone}
        />
      </section>

      {lastRun && (
        <section
          className={`rounded-2xl border p-5 ${
            passedLastRun
              ? "border-emerald-400/15 bg-emerald-400/[0.035]"
              : "border-red-400/15 bg-red-400/[0.035]"
          }`}
        >
          <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
            <div className="flex items-start gap-3">
              {passedLastRun ? (
                <CheckCircle2 className="mt-0.5 size-5 shrink-0 text-emerald-400" />
              ) : (
                <XCircle className="mt-0.5 size-5 shrink-0 text-red-400" />
              )}

              <div>
                <div className="flex flex-wrap items-center gap-2">
                  <p className="font-semibold text-white">
                    Latest simulation: {lastRun.result}
                  </p>

                  <DecisionBadge
                    label={
                      passedLastRun
                        ? "Defense behaved as expected"
                        : "Review required"
                    }
                    tone={passedLastRun ? "passed" : "failed"}
                  />
                </div>

                <div className="mt-2 flex flex-wrap items-center gap-2 text-xs text-slate-500">
                  <span>Expected</span>
                  <DecisionBadge
                    label={lastRun.expected_decision}
                    tone="expected"
                  />

                  <span>Actual</span>
                  <DecisionBadge
                    label={lastRun.actual_decision || "UNKNOWN"}
                    tone="actual"
                  />
                </div>
              </div>
            </div>

            <span className="inline-flex items-center gap-2 rounded-full border border-slate-800 bg-slate-950/60 px-3 py-1.5 text-[9px] font-semibold uppercase tracking-[0.16em] text-slate-500">
              <Clock3 className="size-3" />
              Run #{lastRun.id}
            </span>
          </div>

          {lastRun.details && (
            <p className="mt-5 border-t border-white/5 pt-4 text-xs leading-5 text-slate-500">
              {lastRun.details}
            </p>
          )}
        </section>
      )}

      {runError && (
        <section className="rounded-2xl border border-red-400/15 bg-red-400/[0.035] p-5">
          <div className="flex items-start gap-3">
            <AlertTriangle className="mt-0.5 size-5 shrink-0 text-red-400" />

            <div>
              <p className="font-medium text-red-200">
                Security test execution failed
              </p>

              <p className="mt-1 text-xs leading-5 text-slate-500">
                {runError.message}
              </p>
            </div>
          </div>
        </section>
      )}

      <section className="security-surface overflow-hidden">
        <div className="border-b border-slate-800/80 px-5 py-5 sm:px-6">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="text-[9px] font-semibold uppercase tracking-[0.18em] text-violet-400">
                Simulation registry
              </p>

              <h2 className="mt-1 text-base font-semibold text-white">
                Attack Simulation Scenarios
              </h2>

              <p className="mt-1 text-xs text-slate-500">
                Controlled tests mapped to SentinelX security controls
              </p>
            </div>

            <div className="inline-flex items-center gap-2 self-start rounded-full border border-slate-800 bg-slate-950/60 px-3 py-1.5 text-[9px] font-semibold uppercase tracking-[0.16em] text-slate-500">
              <span className="size-1.5 rounded-full bg-violet-400" />
              {scenarios.length} scenarios
            </div>
          </div>
        </div>

        {isLoading ? (
          <div className="flex min-h-72 items-center justify-center">
            <div className="flex items-center gap-3 text-sm text-slate-500">
              <LoaderCircle className="size-4 animate-spin text-violet-400" />
              Loading security scenarios...
            </div>
          </div>
        ) : isError ? (
          <div className="flex min-h-72 items-center justify-center px-6 text-center">
            <div>
              <AlertTriangle className="mx-auto size-8 text-amber-400" />

              <p className="mt-3 font-medium text-white">
                Security testing unavailable
              </p>

              <p className="mt-1 text-sm text-slate-500">
                SentinelX could not retrieve the registered attack simulation
                scenarios.
              </p>
            </div>
          </div>
        ) : scenarios.length === 0 ? (
          <div className="flex min-h-72 items-center justify-center px-6 text-center">
            <div className="max-w-md">
              <div className="mx-auto flex size-14 items-center justify-center rounded-2xl border border-violet-400/15 bg-violet-400/10">
                <FlaskConical className="size-6 text-violet-300" />
              </div>

              <h3 className="mt-4 font-semibold text-white">
                No security scenarios
              </h3>

              <p className="mt-2 text-sm leading-6 text-slate-500">
                No attack simulation scenarios have been registered with
                SentinelX yet.
              </p>
            </div>
          </div>
        ) : (
          <div className="divide-y divide-slate-800/60">
            {scenarios.map((scenario) => (
              <ScenarioRow
                key={scenario.id}
                scenario={scenario}
                isRunning={isRunning}
                isSelected={selectedScenario === scenario.id}
                onRun={handleRun}
              />
            ))}
          </div>
        )}
      </section>

      <section className="rounded-2xl border border-violet-400/10 bg-violet-400/[0.02] p-5">
        <div className="flex items-start gap-3">
          <ShieldAlert className="mt-0.5 size-4 shrink-0 text-violet-300" />

          <div>
            <p className="text-sm font-medium text-violet-200">
              Attack simulation boundary
            </p>

            <p className="mt-1 text-xs leading-5 text-slate-500">
              Security scenarios are controlled validation exercises. Results
              compare the expected security decision with the runtime decision
              returned by SentinelX.
            </p>
          </div>
        </div>
      </section>
    </main>
  );
}