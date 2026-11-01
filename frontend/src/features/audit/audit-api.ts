import { get } from "@/lib/api-client";

export type AuditIntegrity = {
  total: number;
  verified: number;
  legacy_unhashed: number;
  tampered_ids: number[];
  ok: boolean;
};

export type AuditEntry = {
  id: number;
  actor_username: string;
  action: string;
  resource_type: string;
  resource_id: number | null;
  summary: string;
  created_at: string | null;
};

export type AuditResponse = {
  count: number;
  available_actions: string[];
  entries: AuditEntry[];
};

export function getAuditLog(token: string, action?: string) {
  const query = action ? `?action=${encodeURIComponent(action)}` : "";
  return get<AuditResponse>(`/api/audit${query}`, token);
}

export function exportAuditLog(token: string) {
  return get<{ count: number; entries: AuditEntry[] }>(
    "/api/audit/export",
    token,
  );
}

export function verifyAuditIntegrity(token: string) {
  return get<AuditIntegrity>("/api/audit/integrity", token);
}
