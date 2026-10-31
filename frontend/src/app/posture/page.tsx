"use client";

import { motion } from "motion/react";
import {
  AlertTriangle,
  Gauge,
  LoaderCircle,
  ShieldCheck,
  TriangleAlert,
} from "lucide-react";

import { useFleetPosture } from "@/features/posture/use-posture";
import type { AgentPosture } from "@/features/posture/posture-api";

const levelStyles: Record<
  string,
  { text: string; ring: string; chip: string; label: string }
> = {
  STRONG: {
    text: "text-emerald-600",
    ring: "#059669",
    chip: "bg-emerald-50 text-emerald-700 border-emerald-200",
    label: "Strong",
  },
  MODERATE: {
    text: "text-indigo-600",
    ring: "#4f46e5",
    chip: "bg-indigo-50 text-indigo-700 border-indigo-200",
    label: "Moderate",
  },
  WEAK: {
    text: "text-amber-600",
    ring: "#d97706",
    chip: "bg-amber-50 text-amber-700 border-amber-200",
    label: "Weak",
  },
  CRITICAL: {
    text: "text-red-600",
    ring: "#dc2626",
    chip: "bg-red-50 text-red-700 border-red-200",
    label: "Critical",
  },
};

const severityChip: Record<string, string> = {
  HIGH: "bg-red-50 text-red-700 border-red-200",
  MEDIUM: "bg-amber-50 text-amber-700 border-amber-200",
  LOW: "bg-slate-100 text-slate-600 border-slate-200",
};

export default function PosturePage() {
  const { data, isLoading, isError } = useFleetPosture();

  return (
    <div className="space-y-6">
      {/* Header */}
      <section className="security-surface relative overflow-hidden">
        <div className="absolute inset-0 security-grid opacity-40" />
        <div className="relative px-6 py-6">
          <div className="mb-2 flex items-center gap-2 text-[10px] font-semibold uppercase tracking-[0.2em] text-indigo-600">
            <ShieldCheck className="size-3.5" />
            Security Intelligence
          </div>
          <h1 className="text-3xl font-semibold tracking-tight text-slate-900">
            Agent Security Posture
          </h1>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">
            Configuration-centric posture scoring across your agent fleet —
            policy coverage, risky tool exposure, operational status, recent
            blocked activity, and unresolved alerts, evaluated continuously.
          </p>
        </div>
      </section>

      {isLoading && (
        <div className="security-surface flex items-center justify-center gap-3 py-16 text-sm text-slate-500">
          <LoaderCircle className="size-4 animate-spin text-indigo-600" />
          Evaluating fleet posture…
        </div>
      )}

      {isError && (
        <div className="security-surface flex items-center gap-3 border-red-200 px-6 py-5 text-sm text-red-600">
          <TriangleAlert className="size-4" />
          Unable to evaluate posture. Confirm the control plane is reachable.
        </div>
      )}

      {data && (
        <>
          {/* Fleet summary */}
          <section className="grid gap-4 lg:grid-cols-[minmax(0,0.9fr)_minmax(0,1.1fr)]">
            <motion.div
              initial={{ opacity: 0, y: 14 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
              className="security-surface flex items-center gap-6 p-6"
            >
              <ScoreRing score={data.average_score} level={fleetLevel(data.average_score)} size={128} />
              <div>
                <div className="text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-500">
                  Fleet average
                </div>
                <div className="mt-1 text-4xl font-semibold tracking-tight text-slate-900">
                  {data.average_score}
                  <span className="ml-1 text-lg text-slate-400">/ 100</span>
                </div>
                <div className="mt-2 flex items-center gap-2 text-sm text-slate-500">
                  <Gauge className="size-4 text-indigo-600" />
                  Grade {data.average_grade} · {data.agent_count} agent
                  {data.agent_count === 1 ? "" : "s"}
                </div>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 14 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: 0.08, ease: [0.22, 1, 0.36, 1] }}
              className="security-surface p-6"
            >
              <div className="mb-4 text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-500">
                Posture distribution
              </div>
              <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
                {(["STRONG", "MODERATE", "WEAK", "CRITICAL"] as const).map(
                  (level, i) => {
                    const count = data.level_distribution[level] ?? 0;
                    const style = levelStyles[level];
                    return (
                      <motion.div
                        key={level}
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ duration: 0.3, delay: 0.12 + i * 0.06 }}
                        className="rounded-xl border border-slate-200 bg-slate-50 p-4"
                      >
                        <div className={`text-2xl font-semibold ${style.text}`}>
                          {count}
                        </div>
                        <div className="mt-1 text-[10px] font-semibold uppercase tracking-[0.12em] text-slate-500">
                          {style.label}
                        </div>
                      </motion.div>
                    );
                  },
                )}
              </div>
            </motion.div>
          </section>

          {/* Agent cards */}
          <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {data.agents.map((agent, i) => (
              <AgentPostureCard key={agent.agent_id} agent={agent} index={i} />
            ))}
          </section>
        </>
      )}
    </div>
  );
}

function fleetLevel(score: number): string {
  if (score >= 85) return "STRONG";
  if (score >= 70) return "MODERATE";
  if (score >= 50) return "WEAK";
  return "CRITICAL";
}

function ScoreRing({
  score,
  level,
  size = 96,
}: {
  score: number;
  level: string;
  size?: number;
}) {
  const style = levelStyles[level] ?? levelStyles.MODERATE;
  const stroke = 9;
  const radius = (size - stroke) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference * (1 - score / 100);

  return (
    <div
      className="relative shrink-0"
      style={{ width: size, height: size }}
    >
      <svg width={size} height={size} className="-rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="#e2e8f0"
          strokeWidth={stroke}
        />
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={style.ring}
          strokeWidth={stroke}
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1.1, ease: [0.22, 1, 0.36, 1] }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className={`text-xl font-semibold ${style.text}`}>{score}</span>
      </div>
    </div>
  );
}

function AgentPostureCard({
  agent,
  index,
}: {
  agent: AgentPosture;
  index: number;
}) {
  const style = levelStyles[agent.level] ?? levelStyles.MODERATE;

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: index * 0.06, ease: [0.22, 1, 0.36, 1] }}
      whileHover={{ y: -3 }}
      className="security-surface security-surface-hover flex flex-col p-5"
    >
      <div className="flex items-center gap-4">
        <ScoreRing score={agent.score} level={agent.level} size={84} />
        <div className="min-w-0">
          <h3 className="truncate text-sm font-semibold text-slate-900">
            {agent.agent_name}
          </h3>
          <div className="mt-1.5 flex flex-wrap items-center gap-1.5">
            <span
              className={`rounded-md border px-2 py-0.5 text-[10px] font-semibold uppercase tracking-[0.1em] ${style.chip}`}
            >
              {style.label} · {agent.grade}
            </span>
            <span className="rounded-md border border-slate-200 bg-slate-50 px-2 py-0.5 text-[10px] font-medium text-slate-500">
              {agent.status}
            </span>
          </div>
        </div>
      </div>

      <div className="mt-4 grid grid-cols-3 gap-2 text-center">
        <Signal label="Policies" value={agent.signals.enabled_policies} />
        <Signal label="Risky tools" value={agent.signals.risky_tools} warn={agent.signals.risky_tools > 0} />
        <Signal label="Open alerts" value={agent.signals.open_alerts} warn={agent.signals.open_alerts > 0} />
      </div>

      {agent.findings.length > 0 ? (
        <div className="mt-4 space-y-2 border-t border-slate-200 pt-4">
          {agent.findings.slice(0, 3).map((finding) => (
            <div key={finding.code} className="flex items-start gap-2">
              <span
                className={`mt-0.5 shrink-0 rounded border px-1.5 py-0.5 text-[8px] font-bold uppercase ${severityChip[finding.severity]}`}
              >
                {finding.severity}
              </span>
              <div className="min-w-0">
                <div className="text-[11px] font-medium text-slate-700">
                  {finding.title}
                </div>
              </div>
            </div>
          ))}
          {agent.findings.length > 3 && (
            <div className="pl-1 text-[10px] text-slate-400">
              +{agent.findings.length - 3} more finding
              {agent.findings.length - 3 === 1 ? "" : "s"}
            </div>
          )}
        </div>
      ) : (
        <div className="mt-4 flex items-center gap-2 border-t border-slate-200 pt-4 text-[11px] text-emerald-600">
          <ShieldCheck className="size-3.5" />
          No posture weaknesses detected
        </div>
      )}
    </motion.div>
  );
}

function Signal({
  label,
  value,
  warn = false,
}: {
  label: string;
  value: number;
  warn?: boolean;
}) {
  return (
    <div className="rounded-lg border border-slate-200 bg-slate-50 py-2">
      <div
        className={`flex items-center justify-center gap-1 text-base font-semibold ${
          warn ? "text-amber-600" : "text-slate-900"
        }`}
      >
        {warn && value > 0 && <AlertTriangle className="size-3" />}
        {value}
      </div>
      <div className="mt-0.5 text-[9px] font-medium uppercase tracking-[0.1em] text-slate-500">
        {label}
      </div>
    </div>
  );
}
