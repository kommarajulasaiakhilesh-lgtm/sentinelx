"use client";

import { useState } from "react";
import { motion } from "motion/react";
import {
  Bot,
  Download,
  FileText,
  KeyRound,
  LoaderCircle,
  LogIn,
  Power,
  ScrollText,
  ShieldCheck,
  Trash2,
  TriangleAlert,
} from "lucide-react";

import { useAuth } from "@/hooks/use-auth";
import { useAuditLog } from "@/features/audit/use-audit";
import {
  exportAuditLog,
  verifyAuditIntegrity,
  type AuditEntry,
} from "@/features/audit/audit-api";
import { useToast } from "@/components/ui/toast";

const actionMeta: Record<
  string,
  { icon: typeof Bot; tint: string; ring: string; label: string }
> = {
  USER_LOGIN: {
    icon: LogIn,
    tint: "text-indigo-600 dark:text-indigo-400",
    ring: "border-indigo-200 dark:border-indigo-500/30 bg-indigo-50 dark:bg-indigo-500/10",
    label: "Login",
  },
  AGENT_CREATED: {
    icon: Bot,
    tint: "text-emerald-600 dark:text-emerald-400",
    ring: "border-emerald-200 dark:border-emerald-500/30 bg-emerald-50 dark:bg-emerald-500/10",
    label: "Agent created",
  },
  AGENT_STATUS_CHANGED: {
    icon: Power,
    tint: "text-amber-600 dark:text-amber-400",
    ring: "border-amber-200 dark:border-amber-500/30 bg-amber-50 dark:bg-amber-500/10",
    label: "Status changed",
  },
  POLICY_CREATED: {
    icon: FileText,
    tint: "text-emerald-600 dark:text-emerald-400",
    ring: "border-emerald-200 dark:border-emerald-500/30 bg-emerald-50 dark:bg-emerald-500/10",
    label: "Policy created",
  },
  POLICY_UPDATED: {
    icon: FileText,
    tint: "text-indigo-600 dark:text-indigo-400",
    ring: "border-indigo-200 dark:border-indigo-500/30 bg-indigo-50 dark:bg-indigo-500/10",
    label: "Policy updated",
  },
  POLICY_DELETED: {
    icon: Trash2,
    tint: "text-red-600 dark:text-red-400",
    ring: "border-red-200 dark:border-red-500/30 bg-red-50 dark:bg-red-500/10",
    label: "Policy deleted",
  },
};

const fallbackMeta = {
  icon: KeyRound,
  tint: "text-slate-600 dark:text-slate-300",
  ring: "border-slate-200 dark:border-slate-800 bg-slate-100 dark:bg-slate-800",
  label: "Event",
};

function relativeTime(iso: string | null): string {
  if (!iso) return "—";
  // Backend timestamps are UTC; if the ISO string carries no timezone
  // designator, treat it as UTC so relative times are correct locally.
  const hasTz = /[zZ]|[+-]\d{2}:?\d{2}$/.test(iso);
  const then = new Date(hasTz ? iso : `${iso}Z`).getTime();
  const diff = Date.now() - then;
  const mins = Math.round(diff / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.round(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.round(hrs / 24);
  return `${days}d ago`;
}

function prettyAction(action: string): string {
  return actionMeta[action]?.label ?? action.replaceAll("_", " ").toLowerCase();
}

export default function AuditPage() {
  const [filter, setFilter] = useState<string | undefined>(undefined);
  const { data, isLoading, isError } = useAuditLog(filter);
  const { token } = useAuth();
  const toast = useToast();

  const handleExport = async () => {
    try {
      const res = await exportAuditLog(token as string);
      const csvHeader = "id,actor,action,resource_type,resource_id,summary,created_at";
      const rows = res.entries.map((e) =>
        [
          e.id,
          e.actor_username,
          e.action,
          e.resource_type,
          e.resource_id ?? "",
          `"${(e.summary ?? "").replace(/"/g, '""')}"`,
          e.created_at ?? "",
        ].join(","),
      );
      const blob = new Blob([[csvHeader, ...rows].join("\n")], {
        type: "text/csv;charset=utf-8;",
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "sentinelx-audit-log.csv";
      a.click();
      URL.revokeObjectURL(url);
      toast({ variant: "success", title: `Exported ${res.count} audit entries` });
    } catch {
      toast({ variant: "error", title: "Export failed" });
    }
  };

  const handleVerify = async () => {
    try {
      const res = await verifyAuditIntegrity(token as string);
      if (res.ok) {
        toast({
          variant: "success",
          title: "Audit log verified",
          description: `${res.verified} entries intact${res.legacy_unhashed ? `, ${res.legacy_unhashed} legacy` : ""}.`,
        });
      } else {
        toast({
          variant: "error",
          title: "Tampering detected",
          description: `${res.tampered_ids.length} entries failed verification.`,
        });
      }
    } catch {
      toast({ variant: "error", title: "Verification failed" });
    }
  };

  return (
    <div className="space-y-6">
      <section className="security-surface relative overflow-hidden">
        <div className="absolute inset-0 security-grid opacity-40" />
        <div className="relative flex flex-col gap-4 px-6 py-6 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <div className="mb-2 flex items-center gap-2 text-[10px] font-semibold uppercase tracking-[0.2em] text-indigo-600 dark:text-indigo-400">
              <ScrollText className="size-3.5" />
              Governance Evidence
            </div>
            <h1 className="text-3xl font-semibold tracking-tight text-slate-900 dark:text-slate-100">
              Audit Log
            </h1>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500 dark:text-slate-400">
              An append-only trail of security-relevant actions — agent
              lifecycle, policy changes, and authentication — scoped to your
              operator account for compliance and investigation.
            </p>
          </div>
          <div className="flex shrink-0 items-center gap-2">
            <button
              type="button"
              onClick={handleVerify}
              className="inline-flex h-9 items-center gap-1.5 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 px-3 text-xs font-medium text-slate-600 dark:text-slate-300 transition hover:border-indigo-300 hover:text-indigo-600 dark:hover:text-indigo-400"
            >
              <ShieldCheck className="size-3.5" />
              Verify integrity
            </button>
            <button
              type="button"
              onClick={handleExport}
              className="inline-flex h-9 items-center gap-1.5 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 px-3 text-xs font-medium text-slate-600 dark:text-slate-300 transition hover:border-indigo-300 hover:text-indigo-600 dark:hover:text-indigo-400"
            >
              <Download className="size-3.5" />
              Export CSV
            </button>
          </div>
        </div>
      </section>

      {/* Filters */}
      {data && data.available_actions.length > 0 && (
        <div className="flex flex-wrap gap-2">
          <FilterChip
            label="All events"
            active={filter === undefined}
            onClick={() => setFilter(undefined)}
          />
          {data.available_actions.map((action) => (
            <FilterChip
              key={action}
              label={prettyAction(action)}
              active={filter === action}
              onClick={() => setFilter(action)}
            />
          ))}
        </div>
      )}

      {isLoading && (
        <div className="security-surface flex items-center justify-center gap-3 py-16 text-sm text-slate-500 dark:text-slate-400">
          <LoaderCircle className="size-4 animate-spin text-indigo-600 dark:text-indigo-400" />
          Loading audit trail…
        </div>
      )}

      {isError && (
        <div className="security-surface flex items-center gap-3 border-red-200 dark:border-red-500/30 px-6 py-5 text-sm text-red-600 dark:text-red-400">
          <TriangleAlert className="size-4" />
          Unable to load the audit log.
        </div>
      )}

      {data && data.entries.length === 0 && !isLoading && (
        <div className="security-surface flex flex-col items-center justify-center gap-2 py-16 text-center">
          <ShieldCheck className="size-6 text-slate-300" />
          <p className="text-sm text-slate-500 dark:text-slate-400">
            No audit events recorded yet for this filter.
          </p>
        </div>
      )}

      {data && data.entries.length > 0 && (
        <section className="security-surface p-6">
          <div className="mb-5 flex items-center justify-between">
            <span className="text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-500 dark:text-slate-400">
              {data.count} event{data.count === 1 ? "" : "s"}
            </span>
          </div>
          <ol className="relative space-y-1">
            <span
              aria-hidden
              className="absolute bottom-2 left-[19px] top-2 w-px bg-slate-200"
            />
            {data.entries.map((entry, i) => (
              <TimelineRow key={entry.id} entry={entry} index={i} />
            ))}
          </ol>
        </section>
      )}
    </div>
  );
}

function FilterChip({
  label,
  active,
  onClick,
}: {
  label: string;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`rounded-full border px-3.5 py-1.5 text-xs font-medium capitalize transition-colors ${
        active
          ? "border-indigo-300 bg-indigo-50 dark:bg-indigo-500/10 text-indigo-700 dark:text-indigo-300"
          : "border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-500 dark:text-slate-400 hover:border-slate-300 hover:text-slate-700 dark:hover:text-slate-300"
      }`}
    >
      {label}
    </button>
  );
}

function TimelineRow({ entry, index }: { entry: AuditEntry; index: number }) {
  const meta = actionMeta[entry.action] ?? fallbackMeta;
  const Icon = meta.icon;

  return (
    <motion.li
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.3, delay: Math.min(index * 0.04, 0.4), ease: [0.22, 1, 0.36, 1] }}
      className="relative flex items-start gap-4 rounded-xl px-2 py-2.5 transition-colors hover:bg-slate-50 dark:hover:bg-slate-800/50"
    >
      <div
        className={`relative z-10 flex size-10 shrink-0 items-center justify-center rounded-full border ${meta.ring}`}
      >
        <Icon className={`size-[18px] ${meta.tint}`} />
      </div>
      <div className="min-w-0 flex-1 pt-1">
        <div className="flex flex-wrap items-center gap-x-2 gap-y-1">
          <span className="text-sm font-medium text-slate-800 dark:text-slate-100">
            {entry.summary}
          </span>
        </div>
        <div className="mt-1 flex flex-wrap items-center gap-2 text-[11px] text-slate-500 dark:text-slate-400">
          <span className="font-medium text-slate-600 dark:text-slate-300">
            {entry.actor_username}
          </span>
          <span className="text-slate-300">·</span>
          <span className="rounded border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50 px-1.5 py-0.5 font-mono text-[10px] text-slate-500 dark:text-slate-400">
            {entry.action}
          </span>
          <span className="text-slate-300">·</span>
          <span>{relativeTime(entry.created_at)}</span>
        </div>
      </div>
    </motion.li>
  );
}
