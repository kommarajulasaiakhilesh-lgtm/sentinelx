import { get } from "@/lib/api-client";
import type { Policy } from "@/types/api";

export function getAgentPolicies(token: string, agentId: number) {
  return get<Policy[]>(
    `/api/policies/agent/${agentId}`,
    token,
  );
}