export type AgentStatus =
  | "ACTIVE"
  | "SUSPENDED"
  | "INACTIVE"
  | string;

export type PolicyAction = "ALLOW" | "BLOCK" | "WARN";

export type SecurityDecision =
  | "ALLOWED"
  | "BLOCKED"
  | "WARN"
  | string;

export interface Agent {
  id: number;
  owner_id: number;
  name: string;
  description?: string | null;
  status: AgentStatus;
  created_at?: string;
  updated_at?: string;
}
export interface Tool {
  id: number;
  agent_id: number;
  name: string;
  description?: string | null;
  tool_type: string;
  enabled: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface Policy {
  id: number;
  name: string;
  description?: string | null;
  policy_type: string;
  action: PolicyAction;
  priority: number;
  condition?: string | null;
  enabled: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface SecurityEvent {
  id: number;
  agent_id: number;
  policy_id?: number | null;
  event_type: string;
  action?: string | null;
  decision: SecurityDecision;
  reason?: string | null;
  event_metadata?: Record<string, unknown> | null;
  created_at: string;
}

export interface SecurityAlert {
  id: number;
  agent_id?: number | null;
  alert_type: string;
  severity: string;
  status: string;
  title: string;
  description?: string | null;
  created_at: string;
  resolved_at?: string | null;
}
export interface SecurityMetrics {
  agent_id: number;
  period_start: string;
  period_end: string;
  total_events: number;
  allowed_events: number;
  blocked_events: number;
  suspicious_events: number;
  policy_violations: number;
  risk_score: number;
  risk_level: string;
  block_rate: number;
  violation_rate: number;
}
export interface SecurityTestScenario {
  id: number;
  name: string;
  category: string;
  description?: string | null;
  attack_input?: string | null;
  agent_id?: number | null;
  tool_name?: string | null;
  action?: string | null;
  resource?: string | null;
  expected_decision: string;
  enabled: boolean;
  created_at: string;
  updated_at: string;
}

export interface SecurityTestRun {
  id: number;
  scenario_id: number;
  actual_decision?: string | null;
  expected_decision: string;
  result: string;
  details?: string | null;
  executed_at: string;
}