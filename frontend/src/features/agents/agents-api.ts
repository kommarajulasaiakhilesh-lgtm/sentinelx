import { get } from "@/lib/api-client";
import type { Agent, AgentAPIKey } from "@/types/api";

export function getMyAgents(token: string) {
  return get<Agent[]>("/api/agents/my-agents", token);
}

export function getAgentApiKeys(token: string, agentId: number) {
  return get<AgentAPIKey[]>(
    `/api/agents/${agentId}/api-keys`,
    token,
  );
}