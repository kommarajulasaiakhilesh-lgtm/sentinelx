import { get } from "@/lib/api-client";

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
