"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@/hooks/use-auth";
import {
  addIncidentTimelineEntry,
  createIncidentResponseAction,
  getIncident,
  getIncidentAlerts,
  getIncidentResponseActions,
  getIncidents,
  getIncidentTimeline,
} from "./incidents-api";

export function useIncidents(
  page = 1,
  pageSize = 20,
  status = "ALL",
  severity = "ALL",
) {
  const { token } = useAuth();

  return useQuery({
    queryKey: ["incidents", page, pageSize, status, severity],
    queryFn: () =>
      getIncidents(
        token as string,
        page,
        pageSize,
        status,
        severity,
      ),
    enabled: Boolean(token),
  });
}

export function useIncident(incidentId: number | null) {
  const { token } = useAuth();

  return useQuery({
    queryKey: ["incident", incidentId],
    queryFn: () => getIncident(token as string, incidentId as number),
    enabled: Boolean(token && incidentId),
  });
}

export function useIncidentTimeline(incidentId: number | null) {
  const { token } = useAuth();

  return useQuery({
    queryKey: ["incident-timeline", incidentId],
    queryFn: () =>
      getIncidentTimeline(token as string, incidentId as number),
    enabled: Boolean(token && incidentId),
  });
}

export function useIncidentResponseActions(
  incidentId: number | null,
) {
  const { token } = useAuth();

  return useQuery({
    queryKey: ["incident-response-actions", incidentId],
    queryFn: () =>
      getIncidentResponseActions(
        token as string,
        incidentId as number,
      ),
    enabled: Boolean(token && incidentId),
  });
}

export function useIncidentAlerts(incidentId: number | null) {
  const { token } = useAuth();

  return useQuery({
    queryKey: ["incident-alerts", incidentId],
    queryFn: () =>
      getIncidentAlerts(token as string, incidentId as number),
    enabled: Boolean(token && incidentId),
  });
}

export function useAddIncidentTimelineEntry(
  incidentId: number,
) {
  const { token } = useAuth();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (description: string) =>
      addIncidentTimelineEntry(
        token as string,
        incidentId,
        {
          entry_type: "OPERATOR_NOTE",
          description,
        },
      ),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["incident-timeline", incidentId],
      });
      queryClient.invalidateQueries({
        queryKey: ["incident", incidentId],
      });
    },
  });
}

export function useCreateIncidentResponseAction(
  incidentId: number,
) {
  const { token } = useAuth();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (body: Parameters<typeof createIncidentResponseAction>[2]) =>
      createIncidentResponseAction(
        token as string,
        incidentId,
        body,
      ),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["incident-response-actions", incidentId],
      });
      queryClient.invalidateQueries({
        queryKey: ["incident-timeline", incidentId],
      });
      queryClient.invalidateQueries({
        queryKey: ["incident", incidentId],
      });
      queryClient.invalidateQueries({
        queryKey: ["incidents"],
      });
    },
  });
}
