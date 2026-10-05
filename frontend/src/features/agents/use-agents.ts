"use client";

import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@/hooks/use-auth";
import { getAgentApiKeys, getMyAgents } from "./agents-api";

export function useMyAgents() {
  const { token } = useAuth();

  return useQuery({
    queryKey: ["agents", "my-agents"],
    queryFn: () => getMyAgents(token as string),
    enabled: Boolean(token),
  });
}

export function useAgentApiKeys(agentId: number | null) {
  const { token } = useAuth();

  return useQuery({
    queryKey: ["agent-api-keys", agentId],
    queryFn: () => getAgentApiKeys(token as string, agentId as number),
    enabled: Boolean(token) && agentId !== null,
  });
}