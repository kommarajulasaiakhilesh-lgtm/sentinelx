import { get } from "@/lib/api-client";
import type { Agent } from "@/types/api";

export function getMyAgents(token: string) {
  return get<Agent[]>("/api/agents/my-agents", token);
}