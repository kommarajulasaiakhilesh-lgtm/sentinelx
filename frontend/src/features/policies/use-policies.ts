"use client";

import { useQueries } from "@tanstack/react-query";
import { useAuth } from "@/hooks/use-auth";
import { useMyAgents } from "@/features/agents/use-agents";
import { getAgentPolicies } from "./policies-api";

export function usePolicies() {
  const { token } = useAuth();
  const {
    data: agents = [],
    isLoading: agentsLoading,
    isError: agentsError,
  } = useMyAgents();

  const policyQueries = useQueries({
    queries: agents.map((agent) => ({
      queryKey: ["policies", agent.id],
      queryFn: () => getAgentPolicies(token as string, agent.id),
      enabled: Boolean(token),
    })),
  });

  const policies = policyQueries.flatMap((query) => query.data ?? []);

  const isLoading =
    agentsLoading || policyQueries.some((query) => query.isLoading);

  const isError = agentsError || policyQueries.some((query) => query.isError);

  return {
    policies,
    agents,
    isLoading,
    isError,
  };
}
