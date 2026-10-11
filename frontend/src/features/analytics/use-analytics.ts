
"use client";

import {
  useMutation,
  useQueries,
  useQueryClient,
} from "@tanstack/react-query";
import type { UseQueryResult } from "@tanstack/react-query";
import { useAuth } from "@/hooks/use-auth";
import { useMyAgents } from "@/features/agents/use-agents";
import {
  getAgentAnalytics,
  refreshAgentAnalytics,
} from "./analytics-api";
import type { SecurityMetrics } from "@/types/api";

export function useAnalytics() {
  const { token } = useAuth();

  const {
    data: agents = [],
    isLoading: agentsLoading,
  } = useMyAgents();

  const analyticsQueries = useQueries({
    queries: agents.map((agent) => ({
      queryKey: ["analytics", agent.id],
      queryFn: () => getAgentAnalytics(token as string, agent.id),
      enabled: Boolean(token),
    })),
  }) as UseQueryResult<SecurityMetrics, Error>[];

  const metrics: SecurityMetrics[] = analyticsQueries
    .map((query) => query.data)
    .filter(
      (metric): metric is SecurityMetrics =>
        metric !== undefined,
    );

  const isLoading =
    agentsLoading ||
    analyticsQueries.some((query) => query.isLoading);

  const isError = analyticsQueries.some(
    (query) => query.isError,
  );

  return {
    agents,
    metrics,
    isLoading,
    isError,
  };
}

export function useRefreshAgentAnalytics() {
  const { token } = useAuth();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      agentId,
      periodStart,
      periodEnd,
    }: {
      agentId: number;
      periodStart: string;
      periodEnd: string;
    }) => {
      if (!token) {
        throw new Error("Authentication is required to refresh analytics.");
      }

      return refreshAgentAnalytics(
        token,
        agentId,
        periodStart,
        periodEnd,
      );
    },
    onSuccess: (_data, variables) =>
      queryClient.invalidateQueries({
        queryKey: ["analytics", variables.agentId],
      }),
  });
}
