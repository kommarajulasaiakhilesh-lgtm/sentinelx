
"use client";

import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";

import { useAuth } from "@/hooks/use-auth";
import {
  createDetectionRule,
  deleteDetectionRule,
  getDetectionRules,
  updateDetectionRule,
  type DetectionRulePayload,
} from "./detection-rules-api";

export const detectionRulesQueryKey = ["detection-rules"];

export function useDetectionRules() {
  const { token } = useAuth();

  return useQuery({
    queryKey: detectionRulesQueryKey,
    queryFn: () => getDetectionRules(token as string),
    enabled: Boolean(token),
  });
}

export function useCreateDetectionRule() {
  const { token } = useAuth();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: DetectionRulePayload) =>
      createDetectionRule(token as string, payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: detectionRulesQueryKey,
      });
    },
  });
}

export function useUpdateDetectionRule() {
  const { token } = useAuth();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      id,
      enabled,
    }: {
      id: number;
      enabled: boolean;
    }) => updateDetectionRule(token as string, id, { enabled }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: detectionRulesQueryKey,
      });
    },
  });
}

export function useDeleteDetectionRule() {
  const { token } = useAuth();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) =>
      deleteDetectionRule(token as string, id),
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: detectionRulesQueryKey,
      });
    },
  });
}
