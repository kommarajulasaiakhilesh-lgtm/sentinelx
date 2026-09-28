import { get } from "@/lib/api-client";
import type { Tool } from "@/types/api";

export function getAgentTools(token: string, agentId: number) {
  return get<Tool[]>(
    `/api/tools/agent/${agentId}`,
    token,
  );
}