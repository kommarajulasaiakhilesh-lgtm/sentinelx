"use client";

import { useQueries } from "@tanstack/react-query";
import type { UseQueryResult } from "@tanstack/react-query";
import { useAuth } from "@/hooks/use-auth";
import { useMyAgents } from "@/features/agents/use-agents";
import { getAgentAnalytics } from "./analytics-api";
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