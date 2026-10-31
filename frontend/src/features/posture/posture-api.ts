import { get } from "@/lib/api-client";

export type PostureFinding = {
  code: string;
  severity: "LOW" | "MEDIUM" | "HIGH";
  title: string;
  detail: string;
};

export type PostureSignals = {
  enabled_policies: number;
  policy_types: string[];
  enabled_tools: number;
  risky_tools: number;
  recent_blocked_events: number;
  recent_suspicious_events: number;
  open_alerts: number;
};

export type AgentPosture = {
  agent_id: number;
  agent_name: string;
  status: string;
  score: number;
  grade: string;
  level: "STRONG" | "MODERATE" | "WEAK" | "CRITICAL";
  signals: PostureSignals;
  findings: PostureFinding[];
  evaluated_at: string;
};

export type FleetPosture = {
  owner_id: number;
  agent_count: number;
  average_score: number;
  average_grade: string;
  level_distribution: Record<string, number>;
  weakest_agents: AgentPosture[];
  agents: AgentPosture[];
};

export function getFleetPosture(token: string) {
  return get<FleetPosture>("/api/posture", token);
}
