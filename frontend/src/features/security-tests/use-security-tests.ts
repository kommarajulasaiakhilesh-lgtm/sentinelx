"use client";

import { useMutation, useQuery } from "@tanstack/react-query";

import { useAuth } from "@/hooks/use-auth";

import {
  getSecurityTestScenario,
  getSecurityTestScenarios,
  runSecurityTestScenario,
} from "./security-tests-api";

export function useSecurityTests() {
  const { token } = useAuth();

  const scenariosQuery = useQuery({
    queryKey: ["security-test-scenarios"],
    queryFn: () =>
      getSecurityTestScenarios(token as string),
    enabled: Boolean(token),
  });

  const runMutation = useMutation({
    mutationFn: (scenarioId: number) =>
      runSecurityTestScenario(
        token as string,
        scenarioId,
      ),
  });

  return {
    scenarios: scenariosQuery.data ?? [],
    isLoading: scenariosQuery.isLoading,
    isError: scenariosQuery.isError,
    runScenario: runMutation.mutateAsync,
    isRunning: runMutation.isPending,
    lastRun: runMutation.data,
    runError: runMutation.error,
  };
}

export function useSecurityTestScenario(
  scenarioId: number | null,
) {
  const { token } = useAuth();

  return useQuery({
    queryKey: [
      "security-test-scenario",
      scenarioId,
    ],
    queryFn: () =>
      getSecurityTestScenario(
        token as string,
        scenarioId as number,
      ),
    enabled:
      Boolean(token) &&
      scenarioId !== null,
  });
}