"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Copy, KeyRound, Plus, ShieldOff } from "lucide-react";

import { useAuth } from "@/hooks/use-auth";
import {
  createAgentApiKey,
  getAgentApiKeys,
  revokeAgentApiKey,
} from "@/features/agents/agents-api";
import { useToast } from "@/components/ui/toast";
import { ConfirmDialog } from "@/components/ui/confirm-dialog";

function fmt(iso?: string | null): string {
  if (!iso) return "never";
  const d = new Date(/[zZ]|[+-]\d{2}:?\d{2}$/.test(iso) ? iso : `${iso}Z`);
  return d.toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function ApiKeysPanel({ agentId }: { agentId: number }) {
  const { token } = useAuth();
  const toast = useToast();
  const qc = useQueryClient();
  const [newKey, setNewKey] = useState<string | null>(null);
  const [revokeId, setRevokeId] = useState<number | null>(null);

  const { data: keys = [] } = useQuery({
    queryKey: ["api-keys", agentId],
    queryFn: () => getAgentApiKeys(token as string, agentId),
    enabled: Boolean(token),
  });

  const createMut = useMutation({
    mutationFn: () => createAgentApiKey(token as string, agentId),
    onSuccess: (data) => {
      setNewKey(data.api_key);
      qc.invalidateQueries({ queryKey: ["api-keys", agentId] });
      toast({ variant: "success", title: "API key generated" });
    },
    onError: () =>
      toast({ variant: "error", title: "Could not generate key" }),
  });

  const revokeMut = useMutation({
    mutationFn: (keyId: number) =>
      revokeAgentApiKey(token as string, agentId, keyId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["api-keys", agentId] });
      toast({ variant: "success", title: "API key revoked" });
    },
    onError: () => toast({ variant: "error", title: "Could not revoke key" }),
  });

  const copy = (value: string) => {
    navigator.clipboard?.writeText(value);
    toast({ variant: "info", title: "Copied to clipboard" });
  };

  return (
    <section className="security-surface overflow-hidden">
      <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 px-5 py-3.5">
        <div className="flex items-center gap-2">
          <KeyRound className="size-4 text-indigo-600 dark:text-indigo-400" />
          <span className="text-sm font-semibold text-slate-900 dark:text-slate-100">API keys</span>
          <span className="text-[11px] text-slate-500 dark:text-slate-400">{keys.length}</span>
        </div>
        <button
          type="button"
          onClick={() => createMut.mutate()}
          disabled={createMut.isPending}
          className="inline-flex h-8 items-center gap-1.5 rounded-lg bg-indigo-600 px-3 text-xs font-medium text-white transition hover:bg-indigo-700 disabled:opacity-60"
        >
          <Plus className="size-3.5" />
          {createMut.isPending ? "Generating…" : "Generate key"}
        </button>
      </div>

      {newKey && (
        <div className="border-b border-amber-200 dark:border-amber-500/30 bg-amber-50 dark:bg-amber-500/10 px-5 py-3.5">
          <div className="mb-1.5 text-[11px] font-semibold text-amber-700 dark:text-amber-400">
            Copy this key now — it will not be shown again.
          </div>
          <div className="flex items-center gap-2">
            <code className="min-w-0 flex-1 truncate rounded-md border border-amber-200 dark:border-amber-500/30 bg-white dark:bg-slate-900 px-3 py-2 font-mono text-xs text-slate-800 dark:text-slate-100">
              {newKey}
            </code>
            <button
              type="button"
              onClick={() => copy(newKey)}
              className="inline-flex size-9 items-center justify-center rounded-lg border border-amber-200 dark:border-amber-500/30 bg-white dark:bg-slate-900 text-amber-700 dark:text-amber-400 transition hover:bg-amber-100"
              aria-label="Copy API key"
            >
              <Copy className="size-4" />
            </button>
          </div>
        </div>
      )}

      {keys.length === 0 ? (
        <div className="px-5 py-8 text-center text-xs text-slate-400 dark:text-slate-500">
          No API keys. Generate one to let this agent authenticate.
        </div>
      ) : (
        <div className="divide-y divide-slate-100 dark:divide-slate-800">
          {keys.map((k) => (
            <div
              key={k.id}
              className="flex items-center justify-between px-5 py-3"
            >
              <div className="min-w-0">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-sm text-slate-800 dark:text-slate-100">
                    key #{k.id}
                  </span>
                  <span
                    className={`rounded-md border px-2 py-0.5 text-[10px] font-semibold ${
                      k.is_active
                        ? "border-emerald-200 dark:border-emerald-500/30 bg-emerald-50 dark:bg-emerald-500/10 text-emerald-700 dark:text-emerald-400"
                        : "border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50 text-slate-500 dark:text-slate-400"
                    }`}
                  >
                    {k.is_active ? "ACTIVE" : "REVOKED"}
                  </span>
                </div>
                <div className="mt-1 text-[11px] text-slate-500 dark:text-slate-400">
                  Created {fmt(k.created_at)} · Last used {fmt(k.last_used_at)}
                </div>
              </div>
              {k.is_active && (
                <button
                  type="button"
                  onClick={() => setRevokeId(k.id)}
                  className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 dark:border-slate-800 px-2.5 py-1.5 text-xs font-medium text-red-600 dark:text-red-400 transition hover:border-red-300 hover:bg-red-50 dark:hover:bg-red-500/10"
                >
                  <ShieldOff className="size-3.5" />
                  Revoke
                </button>
              )}
            </div>
          ))}
        </div>
      )}

      <ConfirmDialog
        open={revokeId !== null}
        variant="danger"
        title="Revoke this API key?"
        description="The agent will no longer be able to authenticate with it. This cannot be undone."
        confirmLabel="Revoke key"
        onConfirm={() => {
          if (revokeId !== null) revokeMut.mutate(revokeId);
          setRevokeId(null);
        }}
        onCancel={() => setRevokeId(null)}
      />
    </section>
  );
}
