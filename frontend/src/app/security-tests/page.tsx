"use client";

import {
  AlertTriangle,
  CheckCircle2,
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
  icon: Icon,
}: {
  label: string;
  value: string | number;
  detail: string;
  icon: typeof FlaskConical;
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

function getCategoryClass(category: string) {
  switch (category.toUpperCase()) {
    case "PROMPT_INJECTION":
      return "border-red-400/20 bg-red-400/10 text-red-300";

    case "UNAUTHORIZED_TOOL":
      return "border-orange-400/20 bg-orange-400/10 text-orange-300";

    case "POLICY_BYPASS":
      return "border-amber-400/20 bg-amber-400/10 text-amber-300";

    case "RATE_LIMIT":
      return "border-purple-400/20 bg-purple-400/10 text-purple-300";

    case "REPEATED_BLOCK":
      return "border-blue-400/20 bg-blue-400/10 text-blue-300";

    case "SUSPICIOUS_ACTION":
      return "border-yellow-400/20 bg-yellow-400/10 text-yellow-300";

    default:
      return "border-white/10 bg-white/[0.04] text-slate-300";
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

  const enabledScenarios = scenarios.filter(
    (scenario) => scenario.enabled,
  );

  const categories = new Set(
    scenarios.map((scenario) => scenario.category),
  );

  const passedLastRun =
    lastRun?.result === "PASSED";

  async function handleRun(
    scenario: SecurityTestScenario,
  ) {
    setSelectedScenario(scenario.id);

    try {
      await runScenario(scenario.id);
    } finally {
      setSelectedScenario(null);
    }
  }

  return (
    <div className="space-y-8">
      {/* HERO */}
      <section className="relative overflow-hidden rounded-3xl border border-cyan-400/10 bg-gradient-to-br from-cyan-400/[0.08] via-transparent to-blue-500/[0.05] p-6 sm:p-8">
        <div className="absolute -right-20 -top-24 h-72 w-72 rounded-full bg-cyan-400/10 blur-3xl" />
        <div className="absolute -bottom-24 left-1/3 h-56 w-56 rounded-full bg-blue-500/10 blur-3xl" />

        <div className="relative">
          <div className="flex flex-wrap items-center gap-3">
            <div className="flex items-center gap-2 rounded-full border border-cyan-400/20 bg-cyan-400/10 px-3 py-1.5 text-xs font-medium text-cyan-300">
              <FlaskConical className="h-3.5 w-3.5" />
              Security Testing
            </div>

            <div className="flex items-center gap-2 text-xs text-emerald-400">
              <span className="h-2 w-2 animate-pulse rounded-full bg-emerald-400" />
              Attack simulation online
            </div>
          </div>

          <h1 className="mt-5 text-3xl font-semibold tracking-tight text-white sm:text-4xl">
            Security Testing & Attack Simulation
          </h1>

          <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-400">
            Execute controlled security scenarios against SentinelX
            defenses and verify that runtime controls respond as
            expected.
          </p>

          <div className="mt-6 flex items-center gap-3 text-xs text-slate-500">
            <ShieldCheck className="h-4 w-4 text-cyan-400" />
            Scenario → Attack simulation → Enforcement → Test result
          </div>
        </div>
      </section>

      {/* STATS */}
      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          label="Scenarios"
          value={isLoading ? "—" : isError ? "!" : scenarios.length}
          detail="Registered security tests"
          icon={FlaskConical}
        />

        <StatCard
          label="Enabled"
          value={
            isLoading
              ? "—"
              : isError
                ? "!"
                : enabledScenarios.length
          }
          detail="Ready for execution"
          icon={CheckCircle2}
        />

        <StatCard
          label="Attack Types"
          value={
            isLoading
              ? "—"
              : isError
                ? "!"
                : categories.size
          }
          detail="Simulation categories"
          icon={Target}
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
            lastRun
              ? `Scenario #${lastRun.scenario_id}`
              : "No test executed yet"
          }
          icon={lastRun?.result === "PASSED" ? ShieldCheck : ShieldAlert}
        />
      </section>

      {/* LAST RESULT */}
      {lastRun && (
        <section
          className={`rounded-2xl border p-5 ${
            passedLastRun
              ? "border-emerald-400/15 bg-emerald-400/[0.04]"
              : "border-red-400/15 bg-red-400/[0.04]"
          }`}
        >
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-start gap-3">
              {passedLastRun ? (
                <CheckCircle2 className="mt-0.5 h-5 w-5 text-emerald-400" />
              ) : (
                <XCircle className="mt-0.5 h-5 w-5 text-red-400" />
              )}

              <div>
                <p className="font-semibold text-white">
                  Latest simulation: {lastRun.result}
                </p>

                <p className="mt-1 text-xs text-slate-500">
                  Expected {lastRun.expected_decision} · Actual{" "}
                  {lastRun.actual_decision || "UNKNOWN"}
                </p>
              </div>
            </div>

            <span className="rounded-full border border-white/10 px-3 py-1.5 text-[10px] font-semibold tracking-[0.16em] text-slate-400">
              RUN #{lastRun.id}
            </span>
          </div>

          {lastRun.details && (
            <p className="mt-4 border-t border-white/5 pt-4 text-xs leading-5 text-slate-500">
              {lastRun.details}
            </p>
          )}
        </section>
      )}

      {/* ERROR */}
      {runError && (
        <section className="rounded-2xl border border-red-400/15 bg-red-400/[0.04] p-5">
          <div className="flex items-start gap-3">
            <AlertTriangle className="mt-0.5 h-5 w-5 text-red-400" />

            <div>
              <p className="font-medium text-red-200">
                Security test execution failed
              </p>

              <p className="mt-1 text-xs text-slate-500">
                {runError.message}
              </p>
            </div>
          </div>
        </section>
      )}

      {/* SCENARIOS */}
      <section className="overflow-hidden rounded-2xl border border-white/10 bg-white/[0.025]">
        <div className="flex flex-col gap-3 border-b border-white/10 px-5 py-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="font-semibold text-white">
              Attack Simulation Scenarios
            </h2>

            <p className="mt-1 text-xs text-slate-500">
              Controlled tests mapped to SentinelX security controls
            </p>
          </div>

          <div className="rounded-lg border border-white/10 px-3 py-1.5 text-[10px] font-semibold tracking-[0.16em] text-slate-500">
            {scenarios.length} SCENARIOS
          </div>
        </div>

        {isLoading ? (
          <div className="flex min-h-72 items-center justify-center">
            <div className="flex items-center gap-2 text-sm text-slate-500">
              <LoaderCircle className="h-4 w-4 animate-spin" />
              Loading security scenarios...
            </div>
          </div>
        ) : isError ? (
          <div className="flex min-h-72 items-center justify-center px-6 text-center">
            <div>
              <AlertTriangle className="mx-auto h-8 w-8 text-amber-400" />

              <p className="mt-3 font-medium text-white">
                Security testing unavailable
              </p>

              <p className="mt-1 text-sm text-slate-500">
                SentinelX could not retrieve the registered attack
                simulation scenarios.
              </p>
            </div>
          </div>
        ) : scenarios.length === 0 ? (
          <div className="flex min-h-72 items-center justify-center px-6 text-center">
            <div className="max-w-md">
              <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl border border-cyan-400/15 bg-cyan-400/10">
                <FlaskConical className="h-6 w-6 text-cyan-300" />
              </div>

              <h3 className="mt-4 font-semibold text-white">
                No security scenarios
              </h3>

              <p className="mt-2 text-sm leading-6 text-slate-500">
                No attack simulation scenarios have been registered
                with SentinelX yet.
              </p>
            </div>
          </div>
        ) : (
          <div className="divide-y divide-white/5">
            {scenarios.map((scenario) => {
              const isSelected =
                selectedScenario === scenario.id;

              return (
                <div
                  key={scenario.id}
                  className="group px-5 py-5 transition hover:bg-white/[0.025]"
                >
                  <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
                    <div className="min-w-0">
                      <div className="flex flex-wrap items-center gap-2">
                        <p className="font-medium text-white">
                          {scenario.name}
                        </p>

                        <span
                          className={`rounded-full border px-2 py-0.5 text-[9px] font-semibold tracking-[0.14em] ${getCategoryClass(
                            scenario.category,
                          )}`}
                        >
                          {formatCategory(
                            scenario.category,
                          )}
                        </span>

                        <span
                          className={`rounded-full border px-2 py-0.5 text-[9px] font-semibold tracking-[0.14em] ${
                            scenario.enabled
                              ? "border-emerald-400/20 bg-emerald-400/10 text-emerald-300"
                              : "border-white/10 bg-white/[0.03] text-slate-500"
                          }`}
                        >
                          {scenario.enabled
                            ? "ENABLED"
                            : "DISABLED"}
                        </span>
                      </div>

                      <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">
                        {scenario.description ||
                          "No scenario description provided."}
                      </p>

                      <div className="mt-3 flex flex-wrap gap-x-5 gap-y-2 text-[11px] text-slate-600">
                        <span>
                          Expected:{" "}
                          <span className="text-slate-400">
                            {scenario.expected_decision}
                          </span>
                        </span>

                        {scenario.tool_name && (
                          <span>
                            Tool:{" "}
                            <span className="text-slate-400">
                              {scenario.tool_name}
                            </span>
                          </span>
                        )}

                        {scenario.action && (
                          <span>
                            Action:{" "}
                            <span className="text-slate-400">
                              {scenario.action}
                            </span>
                          </span>
                        )}

                        {scenario.resource && (
                          <span>
                            Resource:{" "}
                            <span className="text-slate-400">
                              {scenario.resource}
                            </span>
                          </span>
                        )}

                        <span>
                          Created:{" "}
                          <span className="text-slate-400">
                            {formatDate(
                              scenario.created_at,
                            )}
                          </span>
                        </span>
                      </div>
                    </div>

                    <button
                      type="button"
                      disabled={
                        !scenario.enabled ||
                        isRunning
                      }
                      onClick={() =>
                        handleRun(scenario)
                      }
                      className="inline-flex shrink-0 items-center justify-center gap-2 rounded-xl border border-cyan-400/20 bg-cyan-400/10 px-4 py-2.5 text-xs font-semibold text-cyan-300 transition hover:bg-cyan-400/15 disabled:cursor-not-allowed disabled:opacity-40"
                    >
                      {isSelected && isRunning ? (
                        <>
                          <LoaderCircle className="h-4 w-4 animate-spin" />
                          Running
                        </>
                      ) : (
                        <>
                          <Play className="h-4 w-4" />
                          Run Test
                        </>
                      )}
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </section>
    </div>
  );
}