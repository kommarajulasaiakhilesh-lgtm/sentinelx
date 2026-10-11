
import { get, post } from "@/lib/api-client";
import type { SecurityMetrics } from "@/types/api";

export function getAgentAnalytics(
  token: string,
  agentId: number,
) {
  return get<SecurityMetrics>(
    `/api/analytics/agents/${agentId}`,
    token,
  );
}

export function refreshAgentAnalytics(
  token: string,
  agentId: number,
  periodStart: string,
  periodEnd: string,
) {
  const params = new URLSearchParams({
    period_start: periodStart,
    period_end: periodEnd,
  });

  return post<SecurityMetrics>(
    `/api/analytics/agents/${agentId}/refresh?${params.toString()}`,
    {},
    token,
  );
}
