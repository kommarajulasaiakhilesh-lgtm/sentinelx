"use client";

import type { ReactNode } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  AlertTriangle,
  CheckCircle2,
  FileCheck2,
  Shield,
  Target,
} from "lucide-react";

import { useAuth } from "@/hooks/use-auth";
import { get } from "@/lib/api-client";

type StatusCounts = {
  IMPLEMENTED: number;
  PARTIALLY_IMPLEMENTED: number;
  GAP_IDENTIFIED: number;
  NOT_IMPLEMENTED: number;
  NOT_APPLICABLE: number;
};

type ComplianceControl = {
  framework_control_id: number;
  control_id: string;
  title: string;
  function: string | null;
  category: string | null;
  reference: string | null;
  mapped: boolean;
  evidence_available: boolean;
  mapping_statuses: string[];
};

type FrameworkCoverage = {
  framework_id: number;
  framework_name: string;
  framework_version: string | null;
  total_controls: number;
  mapped_controls: number;
  mapped_percentage: number;
  evidence_backed_controls: number;
  evidence_coverage_percentage: number;
  implementation_coverage_percentage: number;
  status_counts: StatusCounts;
  controls: ComplianceControl[];
};

function getStatusClass(status: string) {
  switch (status) {
    case "IMPLEMENTED":
      return "border-emerald-400/20 bg-emerald-400/10 text-emerald-300";

    case "PARTIALLY_IMPLEMENTED":
      return "border-amber-400/20 bg-amber-400/10 text-amber-300";

    case "GAP_IDENTIFIED":
    case "NOT_IMPLEMENTED":
      return "border-red-400/20 bg-red-400/10 text-red-300";

    case "NOT_APPLICABLE":
      return "border-slate-400/20 bg-slate-400/10 text-slate-400";

    default:
      return "border-slate-400/20 bg-slate-400/10 text-slate-300";
  }
}

function getStatusDot(status: string) {
  switch (status) {
    case "IMPLEMENTED":
      return "bg-emerald-400";

    case "PARTIALLY_IMPLEMENTED":
      return "bg-amber-400";

    case "GAP_IDENTIFIED":
    case "NOT_IMPLEMENTED":
      return "bg-red-400";

    default:
      return "bg-slate-500";
  }
}

function CoverageBar({
  label,
  percentage,
}: {
  label: string;
  percentage: number;
}) {
  const safePercentage = Math.min(Math.max(percentage, 0), 100);

  return (
    <div>
      <div className="mb-2 flex items-center justify-between gap-3">
        <span className="text-xs text-slate-400">{label}</span>

        <span className="text-xs font-semibold text-slate-200">
          {percentage.toFixed(2)}%
        </span>
      </div>

      <div className="h-1.5 overflow-hidden rounded-full bg-slate-800">
        <div
          className="h-full rounded-full bg-cyan-400 transition-all duration-500"
          style={{ width: `${safePercentage}%` }}
        />
      </div>
    </div>
  );
}

function Metric({
  label,
  value,
  icon,
}: {
  label: string;
  value: number;
  icon: ReactNode;
}) {
  return (
    <div className="rounded-xl border border-slate-800/70 bg-slate-950/40 p-3">
      <div className="flex items-center gap-2">
        <span className="text-slate-500">{icon}</span>

        <span className="text-[10px] text-slate-500">{label}</span>
      </div>

      <p className="mt-1 text-lg font-semibold text-slate-200">{value}</p>
    </div>
  );
}

function StatusBadge({
  label,
  count,
  status,
}: {
  label: string;
  count: number;
  status: string;
}) {
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[9px] font-semibold uppercase tracking-[0.1em] ${getStatusClass(
        status,
      )}`}
    >
      <span className={`size-1.5 rounded-full ${getStatusDot(status)}`} />
      {label}: {count}
    </span>
  );
}

function FrameworkCard({
  framework,
}: {
  framework: FrameworkCoverage;
}) {
  return (
    <article className="security-surface security-surface-hover relative overflow-hidden p-5">
      <div className="pointer-events-none absolute -right-12 -top-12 size-32 rounded-full bg-cyan-400/5 blur-3xl" />

      <div className="relative flex items-start justify-between gap-3">
        <div>
          <p className="text-[9px] font-semibold uppercase tracking-[0.18em] text-cyan-400">
            Framework
          </p>

          <h2 className="mt-2 text-base font-semibold text-white">
            {framework.framework_name}
          </h2>

          <p className="mt-1 text-xs text-slate-500">
            Version: {framework.framework_version ?? "N/A"}
          </p>
        </div>

        <div className="rounded-xl border border-cyan-400/15 bg-cyan-400/10 p-2.5">
          <Shield className="size-5 text-cyan-300" />
        </div>
      </div>

      <div className="relative mt-6 space-y-4">
        <CoverageBar
          label="Control mapping"
          percentage={framework.mapped_percentage}
        />

        <CoverageBar
          label="Evidence coverage"
          percentage={framework.evidence_coverage_percentage}
        />

        <CoverageBar
          label="Implementation coverage"
          percentage={framework.implementation_coverage_percentage}
        />
      </div>

      <div className="relative mt-5 grid grid-cols-2 gap-3">
        <Metric
          label="Controls"
          value={framework.total_controls}
          icon={<Target className="size-3.5" />}
        />

        <Metric
          label="Evidence-backed"
          value={framework.evidence_backed_controls}
          icon={<CheckCircle2 className="size-3.5" />}
        />
      </div>
    </article>
  );
}

function FrameworkDetails({
  framework,
}: {
  framework: FrameworkCoverage;
}) {
  return (
    <section className="security-surface overflow-hidden">
      <div className="border-b border-slate-800/80 px-5 py-5 sm:px-6">
        <div className="flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
          <div>
            <div className="flex flex-wrap items-center gap-3">
              <div>
                <p className="text-[9px] font-semibold uppercase tracking-[0.18em] text-cyan-400">
                  Control registry
                </p>

                <h2 className="mt-1 text-base font-semibold text-white">
                  {framework.framework_name}
                </h2>
              </div>

              <span className="rounded-full border border-slate-800 bg-slate-950/60 px-2.5 py-1 text-[9px] font-semibold uppercase tracking-[0.12em] text-slate-500">
                {framework.total_controls} controls
              </span>
            </div>

            <p className="mt-2 text-xs text-slate-500">
              Framework controls mapped to SentinelX controls and evidence
            </p>
          </div>

          <div className="flex flex-wrap gap-2">
            <StatusBadge
              label="Implemented"
              count={framework.status_counts.IMPLEMENTED}
              status="IMPLEMENTED"
            />

            <StatusBadge
              label="Partial"
              count={framework.status_counts.PARTIALLY_IMPLEMENTED}
              status="PARTIALLY_IMPLEMENTED"
            />

            <StatusBadge
              label="Gaps"
              count={framework.status_counts.GAP_IDENTIFIED}
              status="GAP_IDENTIFIED"
            />
          </div>
        </div>
      </div>

      <div className="divide-y divide-slate-800/60">
        {framework.controls.length === 0 ? (
          <div className="px-6 py-12 text-center">
            <Target className="mx-auto size-7 text-slate-600" />

            <p className="mt-3 text-sm font-medium text-slate-400">
              No framework controls available
            </p>

            <p className="mt-1 text-xs text-slate-600">
              Control mappings have not been returned for this framework.
            </p>
          </div>
        ) : (
          framework.controls.map((control) => (
            <article
              key={control.framework_control_id}
              className="px-5 py-5 transition-colors hover:bg-white/[0.015] sm:px-6"
            >
              <div className="flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
                <div className="min-w-0">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="rounded-md border border-cyan-400/10 bg-cyan-400/[0.04] px-2 py-1 font-mono text-[10px] text-cyan-300">
                      {control.control_id}
                    </span>

                    <h3 className="text-sm font-medium text-slate-200">
                      {control.title}
                    </h3>
                  </div>

                  <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-[11px] text-slate-500">
                    {control.function && (
                      <span>Function: {control.function}</span>
                    )}

                    {control.category && (
                      <span>Category: {control.category}</span>
                    )}

                    {control.reference && (
                      <span>Ref: {control.reference}</span>
                    )}
                  </div>
                </div>

                <div className="flex flex-wrap items-center gap-2 xl:shrink-0">
                  {control.mapping_statuses.map((status) => (
                    <span
                      key={`${control.framework_control_id}-${status}`}
                      className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[9px] font-semibold uppercase tracking-[0.08em] ${getStatusClass(
                        status,
                      )}`}
                    >
                      <span
                        className={`size-1.5 rounded-full ${getStatusDot(status)}`}
                      />

                      {status.replaceAll("_", " ")}
                    </span>
                  ))}

                  <span
                    className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[9px] font-semibold uppercase tracking-[0.08em] ${
                      control.evidence_available
                        ? "border-emerald-400/20 bg-emerald-400/10 text-emerald-300"
                        : "border-red-400/20 bg-red-400/10 text-red-300"
                    }`}
                  >
                    {control.evidence_available ? (
                      <>
                        <CheckCircle2 className="size-3" />
                        Evidence available
                      </>
                    ) : (
                      <>
                        <AlertTriangle className="size-3" />
                        Evidence missing
                      </>
                    )}
                  </span>
                </div>
              </div>
            </article>
          ))
        )}
      </div>
    </section>
  );
}

function PageHeader() {
  return (
    <section className="relative overflow-hidden rounded-2xl border border-cyan-400/10 bg-cyan-400/[0.025] p-6 sm:p-8">
      <div className="security-grid absolute inset-0 opacity-25" />

      <div className="pointer-events-none absolute -right-24 -top-24 size-64 rounded-full bg-cyan-400/5 blur-3xl" />

      <div className="relative">
        <div className="flex flex-wrap items-center gap-3">
          <span className="inline-flex items-center gap-2 rounded-full border border-cyan-400/20 bg-cyan-400/[0.06] px-3 py-1.5 text-[10px] font-semibold uppercase tracking-[0.18em] text-cyan-300">
            <FileCheck2 className="size-3.5" />
            Governance
          </span>

          <span className="inline-flex items-center gap-2 text-[10px] font-medium uppercase tracking-[0.16em] text-emerald-400">
            <span className="size-1.5 rounded-full bg-emerald-400" />
            Alignment telemetry online
          </span>
        </div>

        <div className="mt-5 flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <h1 className="text-2xl font-semibold tracking-tight text-white sm:text-3xl">
              Compliance &amp; Governance
            </h1>

            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">
              Review SentinelX control mappings, supporting evidence,
              implementation status, and identified framework gaps.
            </p>
          </div>

          <div className="flex shrink-0 items-center gap-3 rounded-xl border border-cyan-400/10 bg-cyan-400/[0.035] px-4 py-3">
            <Shield className="size-4 text-cyan-300" />

            <div>
              <p className="text-[9px] font-semibold uppercase tracking-[0.16em] text-cyan-400">
                Governance state
              </p>

              <p className="mt-0.5 text-xs text-slate-400">
                Framework alignment active
              </p>
            </div>
          </div>
        </div>

        <div className="mt-7 grid gap-2 sm:grid-cols-3">
          <div className="rounded-xl border border-slate-800/70 bg-slate-950/30 p-4">
            <p className="text-[9px] font-semibold uppercase tracking-[0.2em] text-cyan-400">
              MAP
            </p>

            <p className="mt-2 text-xs text-slate-400">
              Connect framework controls to SentinelX controls
            </p>
          </div>

          <div className="rounded-xl border border-slate-800/70 bg-slate-950/30 p-4">
            <p className="text-[9px] font-semibold uppercase tracking-[0.2em] text-emerald-400">
              EVIDENCE
            </p>

            <p className="mt-2 text-xs text-slate-400">
              Track evidence-backed implementation
            </p>
          </div>

          <div className="rounded-xl border border-slate-800/70 bg-slate-950/30 p-4">
            <p className="text-[9px] font-semibold uppercase tracking-[0.2em] text-amber-400">
              REVIEW
            </p>

            <p className="mt-2 text-xs text-slate-400">
              Surface partial implementation and gaps
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}

function LoadingState() {
  return (
    <main className="space-y-6">
      <PageHeader />

      <div className="security-surface flex min-h-48 items-center justify-center">
        <div className="flex items-center gap-3 text-sm text-slate-500">
          <div className="size-4 animate-spin rounded-full border-2 border-cyan-400/20 border-t-cyan-400" />
          Loading compliance coverage...
        </div>
      </div>
    </main>
  );
}

function ErrorState({ message }: { message: string }) {
  return (
    <main className="space-y-6">
      <PageHeader />

      <div className="rounded-2xl border border-red-400/15 bg-red-400/[0.04] p-6">
        <div className="flex items-start gap-3">
          <AlertTriangle className="mt-0.5 size-5 shrink-0 text-red-300" />

          <div>
            <h2 className="font-medium text-red-200">
              Compliance data unavailable
            </h2>

            <p className="mt-1 text-sm leading-6 text-slate-400">
              {message}
            </p>
          </div>
        </div>
      </div>
    </main>
  );
}

export default function CompliancePage() {
  const { token } = useAuth();

  const {
    data: frameworks,
    isLoading,
    isError,
    error,
  } = useQuery({
    queryKey: ["compliance-coverage"],
    queryFn: () =>
      get<FrameworkCoverage[]>(
        "/api/compliance/coverage",
        token ?? undefined,
      ),
    enabled: Boolean(token),
  });

  if (isLoading) {
    return <LoadingState />;
  }

  if (isError) {
    return (
      <ErrorState
        message={
          error instanceof Error
            ? error.message
            : "Unable to load compliance coverage."
        }
      />
    );
  }

  const data = frameworks ?? [];

  const totalControls = data.reduce(
    (sum, framework) => sum + framework.total_controls,
    0,
  );

  const mappedControls = data.reduce(
    (sum, framework) => sum + framework.mapped_controls,
    0,
  );

  const evidenceBackedControls = data.reduce(
    (sum, framework) => sum + framework.evidence_backed_controls,
    0,
  );

  const implementationAverage =
    data.length > 0
      ? data.reduce(
          (sum, framework) =>
            sum + framework.implementation_coverage_percentage,
          0,
        ) / data.length
      : 0;

  return (
    <main className="space-y-6 sm:space-y-8">
      <PageHeader />

      <section className="rounded-2xl border border-cyan-400/10 bg-cyan-400/[0.025] p-5">
        <div className="flex items-start gap-3">
          <FileCheck2 className="mt-0.5 size-5 shrink-0 text-cyan-300" />

          <div>
            <h2 className="text-sm font-semibold text-cyan-200">
              Framework Alignment
            </h2>

            <p className="mt-1 text-xs leading-5 text-slate-400">
              SentinelX maps its existing security controls and evidence to
              selected framework areas. These measurements describe internal
              implementation and evidence coverage; they do not represent
              certification or a claim of compliance.
            </p>
          </div>
        </div>
      </section>

      <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard
          label="Frameworks"
          value={data.length}
          detail="Frameworks tracked"
          icon={<Shield className="size-5" />}
          tone="cyan"
        />

        <MetricCard
          label="Controls"
          value={totalControls}
          detail="Framework controls"
          icon={<Target className="size-5" />}
          tone="cyan"
        />

        <MetricCard
          label="Mapped Controls"
          value={mappedControls}
          detail="Controls mapped to SentinelX"
          icon={<FileCheck2 className="size-5" />}
          tone="emerald"
        />

        <MetricCard
          label="Evidence-backed"
          value={evidenceBackedControls}
          detail={`${implementationAverage.toFixed(1)}% average implementation`}
          icon={<CheckCircle2 className="size-5" />}
          tone="emerald"
        />
      </section>

      {data.length === 0 ? (
        <section className="security-surface flex min-h-56 flex-col items-center justify-center px-6 text-center">
          <div className="flex size-14 items-center justify-center rounded-2xl border border-cyan-400/15 bg-cyan-400/10">
            <Shield className="size-7 text-cyan-300" />
          </div>

          <h2 className="mt-4 text-sm font-semibold text-white">
            No frameworks configured
          </h2>

          <p className="mt-2 max-w-md text-sm leading-6 text-slate-500">
            Compliance coverage data has not been returned for the current
            account.
          </p>
        </section>
      ) : (
        <>
          <section className="grid gap-3 md:grid-cols-3">
            {data.map((framework) => (
              <FrameworkCard
                key={framework.framework_id}
                framework={framework}
              />
            ))}
          </section>

          <section className="space-y-4">
            {data.map((framework) => (
              <FrameworkDetails
                key={framework.framework_id}
                framework={framework}
              />
            ))}
          </section>
        </>
      )}

      <section className="rounded-2xl border border-amber-400/10 bg-amber-400/[0.02] p-5">
        <div className="flex items-start gap-3">
          <AlertTriangle className="mt-0.5 size-4 shrink-0 text-amber-400" />

          <div>
            <p className="text-sm font-medium text-amber-200">
              Governance measurement boundary
            </p>

            <p className="mt-1 text-xs leading-5 text-slate-500">
              Coverage metrics describe the current SentinelX implementation,
              mappings, and available evidence. They should not be interpreted
              as certification or an independent compliance determination.
            </p>
          </div>
        </div>
      </section>
    </main>
  );
}

function MetricCard({
  label,
  value,
  detail,
  icon,
  tone,
}: {
  label: string;
  value: string | number;
  detail: string;
  icon: ReactNode;
  tone: "cyan" | "emerald";
}) {
  return (
    <article className="security-surface security-surface-hover relative overflow-hidden p-5">
      <div
        className={`pointer-events-none absolute -right-8 -top-8 size-24 rounded-full blur-2xl ${
          tone === "cyan" ? "bg-cyan-400/5" : "bg-emerald-400/5"
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

        <div
          className={`rounded-xl border p-3 ${
            tone === "cyan"
              ? "border-cyan-400/15 bg-cyan-400/10 text-cyan-300"
              : "border-emerald-400/15 bg-emerald-400/10 text-emerald-300"
          }`}
        >
          {icon}
        </div>
      </div>
    </article>
  );
}