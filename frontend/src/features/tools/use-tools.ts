"use client";

import { useQueries, useQuery } from "@tanstack/react-query";
import type { UseQueryResult } from "@tanstack/react-query";
import { useAuth } from "@/hooks/use-auth";
import { useMyAgents } from "@/features/agents/use-agents";
import { getAgentTools } from "./tools-api";
import type { Tool } from "@/types/api";

export function useTools() {
  const { token } = useAuth();

  const {
    data: agents = [],
    isLoading: agentsLoading,
  } = useMyAgents();

  const toolQueries = useQueries({
    queries: agents.map((agent) => ({
      queryKey: ["tools", agent.id],
      queryFn: () => getAgentTools(token as string, agent.id),
      enabled: Boolean(token),
    })),
  }) as UseQueryResult<Tool[], Error>[];

  const tools: Tool[] = toolQueries.flatMap(
    (query) => query.data ?? [],
  );

  const isLoading =
    agentsLoading ||
    toolQueries.some((query) => query.isLoading);

  const isError = toolQueries.some(
    (query) => query.isError,
  );

  return {
    tools,
    agents,
    isLoading,
    isError,
  };
}

export function useAgentTools(agentId: number | null) {
  const { token } = useAuth();

  return useQuery({
    queryKey: ["tools", agentId],
    queryFn: () => getAgentTools(token as string, agentId as number),
    enabled: Boolean(token) && agentId !== null,
  });
}