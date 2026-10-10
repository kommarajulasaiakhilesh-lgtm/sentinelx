
import { apiRequest } from "@/lib/api-client";

export type DetectionSeverity =
  | "LOW"
  | "MEDIUM"
  | "HIGH"
  | "CRITICAL";

export interface DetectionRule {
  id: number;
  owner_id: number | null;
  name: string;
  description: string | null;
  enabled: boolean;
  severity: DetectionSeverity;
  alert_type: string;
  title: string;
  conditions: string | null;
  threshold: number;
  window_seconds: number;
  created_at: string;
  updated_at: string;
}

export interface DetectionRulePayload {
  name: string;
  description: string | null;
  enabled: boolean;
  severity: DetectionSeverity;
  alert_type: string;
  title: string;
  conditions: Record<string, string | number | boolean | string[] | number[]>;
  threshold: number;
  window_seconds: number;
}

export function getDetectionRules(token: string) {
  return apiRequest<DetectionRule[]>("/api/detection-rules", {
    method: "GET",
    token,
  });
}

export function createDetectionRule(
  token: string,
  payload: DetectionRulePayload,
) {
  return apiRequest<DetectionRule>("/api/detection-rules", {
    method: "POST",
    body: JSON.stringify(payload),
    token,
  });
}

export function updateDetectionRule(
  token: string,
  id: number,
  payload: Partial<Pick<DetectionRule, "enabled">>,
) {
  return apiRequest<DetectionRule>(`/api/detection-rules/${id}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
    token,
  });
}

export function deleteDetectionRule(token: string, id: number) {
  return apiRequest<{ message: string; rule_id: number }>(
    `/api/detection-rules/${id}`,
    {
      method: "DELETE",
      token,
    },
  );
}
