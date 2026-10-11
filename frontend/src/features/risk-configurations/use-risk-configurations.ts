"use client";

import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";

import { useAuth } from "@/hooks/use-auth";
import {
  getEffectiveRiskConfiguration,
  getGlobalRiskConfiguration,
  getMyRiskConfiguration,
  saveGlobalRiskConfiguration,
  saveMyRiskConfiguration,
  type RiskScoringConfigurationUpdate,
} from "./risk-configurations-api";

export const riskConfigurationKeys = {
  all: ["risk-configurations"] as const,
  effective: ["risk-configurations", "effective"] as const,
  mine: ["risk-configurations", "mine"] as const,
  global: ["risk-configurations", "global"] as const,
};

export function useEffectiveRiskConfiguration() {
  const { token } = useAuth();

  return useQuery({
    queryKey: riskConfigurationKeys.effective,
    queryFn: () =>
      getEffectiveRiskConfiguration(token as string),
    enabled: Boolean(token),
    retry: false,
  });
}

export function useMyRiskConfiguration() {
  const { token } = useAuth();

  return useQuery({
    queryKey: riskConfigurationKeys.mine,
    queryFn: () =>
      getMyRiskConfiguration(token as string),
    enabled: Boolean(token),
    retry: false,
  });
}

export function useGlobalRiskConfiguration() {
  const { token } = useAuth();

  return useQuery({
    queryKey: riskConfigurationKeys.global,
    queryFn: () =>
      getGlobalRiskConfiguration(token as string),
    enabled: Boolean(token),
    retry: false,
  });
}

export function useSaveMyRiskConfiguration() {
  const { token } = useAuth();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (configuration: RiskScoringConfigurationUpdate) =>
      saveMyRiskConfiguration(token as string, configuration),
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({
          queryKey: riskConfigurationKeys.mine,
        }),
        queryClient.invalidateQueries({
          queryKey: riskConfigurationKeys.effective,
        }),
      ]);
    },
  });
}

export function useSaveGlobalRiskConfiguration() {
  const { token } = useAuth();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (configuration: RiskScoringConfigurationUpdate) =>
      saveGlobalRiskConfiguration(token as string, configuration),
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({
          queryKey: riskConfigurationKeys.global,
        }),
        queryClient.invalidateQueries({
          queryKey: riskConfigurationKeys.effective,
        }),
      ]);
    },
  });
}