import { get, post } from "@/lib/api-client";
import type {
  Incident,
  IncidentAlert,
  IncidentResponseAction,
  IncidentTimelineEntry,
} from "@/types/api";

export interface IncidentListResponse {
  items: Incident[];
  page: number;
  page_size: number;
  total: number;
  pages: number;
}

export interface IncidentTimelineListResponse {
  items: IncidentTimelineEntry[];
}

export interface IncidentResponseActionListResponse {
  items: IncidentResponseAction[];
}

export interface IncidentAlertListResponse {
  items: IncidentAlert[];
}

export interface IncidentTimelineCreate {
  entry_type: "OPERATOR_NOTE";
  description: string;
}

export interface IncidentResponseActionCreate {
  action_type:
    | "SUSPEND_AGENT"
    | "DISABLE_TOOL"
    | "ROTATE_AGENT_API_KEY";
  reason: string;
  agent_id?: number;
  tool_id?: number;
  api_key_id?: number;
}

export function getIncidents(
  token: string,
  page = 1,
  pageSize = 20,
  status?: string,
  severity?: string,
) {
  const params = new URLSearchParams({
    page: String(page),
    page_size: String(pageSize),
  });

  if (status && status !== "ALL") {
    params.set("status", status);
  }

  if (severity && severity !== "ALL") {
    params.set("severity", severity);
  }

  return get<IncidentListResponse>(
    `/api/incidents?${params.toString()}`,
    token,
  );
}

export function getIncident(token: string, incidentId: number) {
  return get<Incident>(
    `/api/incidents/${incidentId}`,
    token,
  );
}

export function getIncidentTimeline(
  token: string,
  incidentId: number,
) {
  return get<IncidentTimelineEntry[]>(
    `/api/incidents/${incidentId}/timeline`,
    token,
  );
}

export function addIncidentTimelineEntry(
  token: string,
  incidentId: number,
  body: IncidentTimelineCreate,
) {
  return post<IncidentTimelineEntry>(
    `/api/incidents/${incidentId}/timeline`,
    body,
    token,
  );
}

export function getIncidentResponseActions(
  token: string,
  incidentId: number,
) {
  return get<IncidentResponseAction[]>(
    `/api/incidents/${incidentId}/response-actions`,
    token,
  );
}

export function createIncidentResponseAction(
  token: string,
  incidentId: number,
  body: IncidentResponseActionCreate,
) {
  return post<IncidentResponseAction>(
    `/api/incidents/${incidentId}/response-actions`,
    body,
    token,
  );
}

export function getIncidentAlerts(
  token: string,
  incidentId: number,
) {
  return get<IncidentAlert[]>(
    `/api/incidents/${incidentId}/alerts`,
    token,
  );
}

