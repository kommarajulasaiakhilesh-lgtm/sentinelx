"use client";

import { useQuery } from "@tanstack/react-query";
import {
  AlertTriangle,
  CheckCircle2,
  FileCheck2,
  Shield,
  Target,
} from "lucide-react";
import type { ComponentType } from "react";

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
      return "border-red-400/20 bg-red-400/10 text-red-300";

    case "NOT_IMPLEMENTED":
      return "border-red-400/20 bg-red-400/10 text-red-300";

    case "NOT_APPLICABLE":
      return "border-slate-400/20 bg-slate-400/10 text-slate-400";

    default:
      return "border-slate-400/20 bg-slate-400/10 text-slate-300";
  }
}

function CoverageBar({
  label,
  percentage,
}: {
  label: string;
  percentage: number;
}) {
  return (
    <div>
      <div className="mb-2 flex items-center justify-between">
        <span className="text-xs text-slate-400">{label}</span>

        <span className="text-xs font-semibold text-slate-200">
          {percentage.toFixed(2)}%
        </span>
      </div>

      <div className="h-2 overflow-hidden rounded-full bg-white/5">
        <div
          className="h-full rounded-full bg-cyan-400 transition-all"
          style={{
            width: `${Math.min(Math.max(percentage, 0), 100)}%`,
          }}
        />
      </div>
    </div>
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
      get<FrameworkCoverage[]>("/api/compliance/coverage", token ?? undefined),
    enabled: Boolean(token),
  });

  if (isLoading) {
    return (
      <main className="space-y-6">
        <PageHeader />

        <div className="rounded-2xl border border-white/10 bg-white/[0.02] p-8 text-sm text-slate-400">
          Loading compliance coverage...
        </div>
      </main>
    );
  }

  if (isError) {
    return (
      <main className="space-y-6">
        <PageHeader />

        <div className="rounded-2xl border border-red-400/20 bg-red-400/5 p-6">
          <div className="flex items-center gap-3">
            <AlertTriangle className="size-5 text-red-300" />

            <div>
              <h2 className="font-medium text-red-200">
                Compliance data unavailable
              </h2>

              <p className="mt-1 text-sm text-slate-400">
                {error instanceof Error
                  ? error.message
                  : "Unable to load compliance coverage."}
              </p>
            </div>
          </div>
        </div>
      </main>
    );
  }

  const data = frameworks ?? [];

  return (
    <main className="space-y-6">
      <PageHeader />

      <div className="rounded-2xl border border-cyan-400/10 bg-cyan-400/[0.03] p-5">
        <div className="flex items-start gap-3">
          <FileCheck2 className="mt-0.5 size-5 text-cyan-300" />

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
      </div>

      <section className="grid gap-4 md:grid-cols-3">
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
    </main>
  );
}

function PageHeader() {
  return (
    <div>
      <div className="flex items-center gap-3">
        <div className="flex size-10 items-center justify-center rounded-xl border border-cyan-400/20 bg-cyan-400/10">
          <FileCheck2 className="size-5 text-cyan-300" />
        </div>

        <div>
          <p className="text-xs uppercase tracking-[0.18em] text-cyan-400/70">
            Governance
          </p>

          <h1 className="mt-1 text-2xl font-semibold text-white">
            Compliance Center
          </h1>
        </div>
      </div>

      <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-400">
        Review SentinelX control mappings, supporting evidence, implementation
        status, and identified framework gaps.
      </p>
    </div>
  );
}

function FrameworkCard({
  framework,
}: {
  framework: FrameworkCoverage;
}) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.02] p-5">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-[0.14em] text-slate-500">
            Framework
          </p>

          <h2 className="mt-2 text-base font-semibold text-white">
            {framework.framework_name}
          </h2>

          <p className="mt-1 text-xs text-slate-500">
            Version: {framework.framework_version ?? "N/A"}
          </p>
        </div>

        <Shield className="size-5 text-cyan-300" />
      </div>

      <div className="mt-6 space-y-4">
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

      <div className="mt-5 grid grid-cols-2 gap-3">
        <Metric
          label="Controls"
          value={framework.total_controls}
          icon={Target}
        />

        <Metric
          label="Evidence-backed"
          value={framework.evidence_backed_controls}
          icon={CheckCircle2}
        />
      </div>
    </div>
  );
}

function Metric({
  label,
  value,
  icon: Icon,
}: {
  label: string;
  value: number;
  icon: ComponentType<{ className?: string }>;
}) {
  return (
    <div className="rounded-xl border border-white/5 bg-black/10 p-3">
      <div className="flex items-center gap-2">
        <Icon className="size-3.5 text-slate-500" />

        <span className="text-[11px] text-slate-500">
          {label}
        </span>
      </div>

      <p className="mt-1 text-lg font-semibold text-slate-200">
        {value}
      </p>
    </div>
  );
}

function FrameworkDetails({
  framework,
}: {
  framework: FrameworkCoverage;
}) {
  return (
    <div className="overflow-hidden rounded-2xl border border-white/10 bg-white/[0.02]">
      <div className="border-b border-white/10 px-5 py-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="text-base font-semibold text-white">
              {framework.framework_name}
            </h2>

            <p className="mt-1 text-xs text-slate-500">
              {framework.total_controls} framework controls mapped to
              SentinelX controls
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

      <div className="divide-y divide-white/5">
        {framework.controls.map((control) => (
          <div
            key={control.framework_control_id}
            className="px-5 py-4"
          >
            <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
              <div className="min-w-0">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="rounded-md border border-white/10 bg-white/5 px-2 py-1 font-mono text-[10px] text-cyan-300">
                    {control.control_id}
                  </span>

                  <h3 className="text-sm font-medium text-slate-200">
                    {control.title}
                  </h3>
                </div>

                <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-[11px] text-slate-500">
                  {control.function && (
                    <span>
                      Function: {control.function}
                    </span>
                  )}

                  {control.category && (
                    <span>
                      Category: {control.category}
                    </span>
                  )}

                  {control.reference && (
                    <span>
                      Ref: {control.reference}
                    </span>
                  )}
                </div>
              </div>

              <div className="flex flex-wrap items-center gap-2">
                {control.mapping_statuses.map((status) => (
                  <span
                    key={`${control.framework_control_id}-${status}`}
                    className={`rounded-full border px-2.5 py-1 text-[10px] font-medium ${getStatusClass(
                      status,
                    )}`}
                  >
                    {status.replaceAll("_", " ")}
                  </span>
                ))}

                <span
                  className={`rounded-full border px-2.5 py-1 text-[10px] ${
                    control.evidence_available
                      ? "border-emerald-400/20 bg-emerald-400/10 text-emerald-300"
                      : "border-red-400/20 bg-red-400/10 text-red-300"
                  }`}
                >
                  {control.evidence_available
                    ? "Evidence available"
                    : "Evidence missing"}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
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
      className={`rounded-full border px-2.5 py-1 text-[10px] font-medium ${getStatusClass(
        status,
      )}`}
    >
      {label}: {count}
    </span>
  );
}