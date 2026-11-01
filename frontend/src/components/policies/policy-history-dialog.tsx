"use client";

import { AnimatePresence, motion } from "motion/react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { History, RotateCcw, X } from "lucide-react";

import { useAuth } from "@/hooks/use-auth";
import {
  getPolicyVersions,
  rollbackPolicy,
  type PolicyVersion,
} from "@/features/policies/policies-api";
import { useToast } from "@/components/ui/toast";

function fmt(iso: string | null): string {
  if (!iso) return "";
  const d = new Date(/[zZ]|[+-]\d{2}:?\d{2}$/.test(iso) ? iso : `${iso}Z`);
  return d.toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function PolicyHistoryDialog({
  policyId,
  policyName,
  open,
  onClose,
}: {
  policyId: number;
  policyName: string;
  open: boolean;
  onClose: () => void;
}) {
  const { token } = useAuth();
  const toast = useToast();
  const qc = useQueryClient();

  const { data } = useQuery({
    queryKey: ["policy-versions", policyId],
    queryFn: () => getPolicyVersions(token as string, policyId),
    enabled: Boolean(token) && open,
  });

  const rollbackMut = useMutation({
    mutationFn: (versionNumber: number) =>
      rollbackPolicy(token as string, policyId, versionNumber),
    onSuccess: (_d, versionNumber) => {
      qc.invalidateQueries({ queryKey: ["policy-versions", policyId] });
      qc.invalidateQueries({ queryKey: ["policies"] });
      toast({
        variant: "success",
        title: "Policy rolled back",
        description: `Restored version ${versionNumber}.`,
      });
    },
    onError: () => toast({ variant: "error", title: "Rollback failed" }),
  });

  const versions = data?.versions ?? [];

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          className="fixed inset-0 z-[95] flex items-center justify-center px-4"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.15 }}
        >
          <div
            className="absolute inset-0 bg-slate-900/40 backdrop-blur-sm"
            onClick={onClose}
            aria-hidden
          />
          <motion.div
            initial={{ opacity: 0, y: 12, scale: 0.97 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 12, scale: 0.97 }}
            transition={{ duration: 0.18, ease: [0.22, 1, 0.36, 1] }}
            className="relative flex max-h-[80vh] w-full max-w-lg flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-2xl shadow-slate-900/20"
          >
            <div className="flex items-center justify-between border-b border-slate-100 px-5 py-4">
              <div className="flex items-center gap-2">
                <History className="size-4 text-indigo-600" />
                <span className="text-sm font-semibold text-slate-900">
                  Version history
                </span>
                <span className="truncate text-xs text-slate-500">
                  · {policyName}
                </span>
              </div>
              <button
                type="button"
                onClick={onClose}
                className="rounded p-1 text-slate-400 transition hover:text-slate-600"
                aria-label="Close"
              >
                <X className="size-4" />
              </button>
            </div>

            <div className="overflow-y-auto">
              {versions.length === 0 ? (
                <div className="px-5 py-10 text-center text-sm text-slate-400">
                  No version history yet.
                </div>
              ) : (
                <ol className="divide-y divide-slate-100">
                  {versions.map((v: PolicyVersion, i) => (
                    <li
                      key={v.id}
                      className="flex items-start justify-between gap-3 px-5 py-3.5"
                    >
                      <div className="min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="rounded-md border border-indigo-200 bg-indigo-50 px-1.5 py-0.5 font-mono text-[10px] font-semibold text-indigo-700">
                            v{v.version_number}
                          </span>
                          <span className="text-sm font-medium text-slate-800">
                            {v.change_note}
                          </span>
                        </div>
                        <div className="mt-1 text-[11px] text-slate-500">
                          {v.action} · priority {v.priority} ·{" "}
                          {v.enabled ? "enabled" : "disabled"} · {fmt(v.created_at)}
                        </div>
                      </div>
                      {i !== 0 && (
                        <button
                          type="button"
                          onClick={() => rollbackMut.mutate(v.version_number)}
                          disabled={rollbackMut.isPending}
                          className="inline-flex shrink-0 items-center gap-1.5 rounded-lg border border-slate-200 px-2.5 py-1.5 text-xs font-medium text-indigo-600 transition hover:border-indigo-300 hover:bg-indigo-50 disabled:opacity-60"
                        >
                          <RotateCcw className="size-3.5" />
                          Restore
                        </button>
                      )}
                    </li>
                  ))}
                </ol>
              )}
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
