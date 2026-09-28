import { get } from "@/lib/api-client";
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