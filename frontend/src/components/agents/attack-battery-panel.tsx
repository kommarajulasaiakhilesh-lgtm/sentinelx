"use client";

import { useMutation } from "@tanstack/react-query";
import { CheckCircle2, Play, ShieldAlert, Swords, XCircle } from "lucide-react";

import { get } from "@/lib/api-client";
import { useAuth } from "@/hooks/use-auth";

type BatteryResult = {
  id: string;
  category: "DIRECT" | "EVASION" | "BENIGN";
  is_attack: boolean;
  payload: string;
  decision: string;
  verdict: "DETECTED" | "MISSED" | "ALLOWED" | "FALSE_POSITIVE";
};

type BatteryReport = {
  agent_name: string;
  summary: {
    total_attacks: number;
    detected: number;
    missed: number;
    benign: number;
    false_positives: number;
    detection_rate_percent: number;
    false_positive_rate_percent: number;
  };
  results: BatteryResult[];
};

const verdictStyle: Record<string, { cls: string; icon: typeof CheckCircle2 }> = {
  DETECTED: { cls: "text-emerald-600", icon: CheckCircle2 },
  ALLOWED: { cls: "text-emerald-600", icon: CheckCircle2 },
  MISSED: { cls: "text-red-600", icon: XCircle },
  FALSE_POSITIVE: { cls: "text-amber-600", icon: ShieldAlert },
};

export function AttackBatteryPanel({ agentId }: { agentId: number }) {
  const { token } = useAuth();

  const mut = useMutation({
    mutationFn: () =>
      get<BatteryReport>(`/api/security-tests/attack-battery/${agentId}`, token as string),
  });

  const report = mut.data;
  const rate = report?.summary.detection_rate_percent ?? 0;
  const rateColor =
    rate >= 80 ? "text-emerald-600" : rate >= 40 ? "text-amber-600" : "text-red-600";

  return (
    <section className="security-surface overflow-hidden">
      <div className="flex items-center justify-between border-b border-slate-200 px-5 py-3.5">
        <div className="flex items-center gap-2">
          <Swords className="size-4 text-indigo-600" />
          <span className="text-sm font-semibold text-slate-900">
            Prompt-injection attack battery
          </span>
        </div>
        <button
          type="button"
          onClick={() => mut.mutate()}
          disabled={mut.isPending}
          className="inline-flex h-8 items-center gap-1.5 rounded-lg bg-indigo-600 px-3 text-xs font-medium text-white transition hover:bg-indigo-700 disabled:opacity-60"
        >
          <Play className="size-3.5" />
          {mut.isPending ? "Running…" : "Run battery"}
        </button>
      </div>

      {!report ? (
        <div className="px-5 py-8 text-center text-xs text-slate-400">
          Run a fixed library of adversarial and benign inputs against this
          agent&apos;s live policy enforcement to measure detection.
        </div>
      ) : (
        <div>
          <div className="grid grid-cols-2 gap-px bg-slate-100 sm:grid-cols-4">
            <Stat label="Detection rate" value={`${rate}%`} cls={rateColor} />
            <Stat
              label="Attacks caught"
              value={`${report.summary.detected}/${report.summary.total_attacks}`}
            />
            <Stat label="Missed" value={report.summary.missed} cls={report.summary.missed ? "text-red-600" : "text-slate-900"} />
            <Stat
              label="False positives"
              value={report.summary.false_positives}
              cls={report.summary.false_positives ? "text-amber-600" : "text-slate-900"}
            />
          </div>
          <div className="divide-y divide-slate-100">
            {report.results.map((r) => {
              const style = verdictStyle[r.verdict] ?? verdictStyle.ALLOWED;
              const Icon = style.icon;
              return (
                <div key={r.id} className="flex items-start gap-3 px-5 py-3">
                  <Icon className={`mt-0.5 size-4 shrink-0 ${style.cls}`} />
                  <div className="min-w-0 flex-1">
                    <div className="truncate text-xs text-slate-700">
                      {r.payload}
                    </div>
                    <div className="mt-0.5 flex items-center gap-2 text-[10px] text-slate-500">
                      <span className="rounded border border-slate-200 bg-slate-50 px-1.5 py-0.5 font-medium">
                        {r.category}
                      </span>
                      <span>decision: {r.decision}</span>
                    </div>
                  </div>
                  <span className={`shrink-0 text-[10px] font-semibold ${style.cls}`}>
                    {r.verdict.replace("_", " ")}
                  </span>
                </div>
              );
            })}
          </div>
          <div className="border-t border-slate-100 bg-slate-50 px-5 py-2.5 text-[10px] text-slate-500">
            Evasion payloads that slip past baseline patterns show real
            detection gaps — this measures, it doesn&apos;t guarantee full coverage.
          </div>
        </div>
      )}
    </section>
  );
}

function Stat({
  label,
  value,
  cls = "text-slate-900",
}: {
  label: string;
  value: string | number;
  cls?: string;
}) {
  return (
    <div className="bg-white px-4 py-3">
      <div className={`text-xl font-semibold ${cls}`}>{value}</div>
      <div className="mt-0.5 text-[10px] font-medium uppercase tracking-[0.1em] text-slate-500">
        {label}
      </div>
    </div>
  );
}
