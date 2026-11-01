import { get, post } from "@/lib/api-client";
import type { Agent, AgentAPIKey, AgentAPIKeyCreated } from "@/types/api";

export function getMyAgents(token: string) {
  return get<Agent[]>("/api/agents/my-agents", token);
}

export function getAgentApiKeys(token: string, agentId: number) {
  return get<AgentAPIKey[]>(
    `/api/agents/${agentId}/api-keys`,
    token,
  );
}

export function createAgentApiKey(token: string, agentId: number) {
  return post<AgentAPIKeyCreated>(
    `/api/agents/${agentId}/api-keys`,
    {},
    token,
  );
}

export function revokeAgentApiKey(
  token: string,
  agentId: number,
  keyId: number,
) {
  return post<AgentAPIKey>(
    `/api/agents/${agentId}/api-keys/${keyId}/revoke`,
    {},
    token,
  );
}