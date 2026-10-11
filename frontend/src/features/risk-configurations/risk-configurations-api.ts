import { get, put } from "@/lib/api-client";

export interface RiskScoringConfiguration {
  id: number;
  owner_id: number | null;
  name: string;
  enabled: boolean;
  blocked_event_weight: number;
  suspicious_event_weight: number;
  policy_violation_weight: number;
  score_cap: number;
  low_max: number;
  medium_max: number;
  high_max: number;
  critical_max: number;
  created_at: string;
  updated_at: string;
}

export interface RiskScoringConfigurationUpdate {
  name: string;
  enabled: boolean;
  blocked_event_weight: number;
  suspicious_event_weight: number;
  policy_violation_weight: number;
  score_cap: number;
  low_max: number;
  medium_max: number;
  high_max: number;
  critical_max: number;
}

export function getEffectiveRiskConfiguration(token: string) {
  return get<RiskScoringConfiguration>(
    "/api/risk-configurations/effective",
    token,
  );
}

export function getMyRiskConfiguration(token: string) {
  return get<RiskScoringConfiguration>(
    "/api/risk-configurations/mine",
    token,
  );
}

export function saveMyRiskConfiguration(
  token: string,
  configuration: RiskScoringConfigurationUpdate,
) {
  return put<RiskScoringConfiguration>(
    "/api/risk-configurations/mine",
    configuration,
    token,
  );
}

export function getGlobalRiskConfiguration(token: string) {
  return get<RiskScoringConfiguration>(
    "/api/risk-configurations/global",
    token,
  );
}

export function saveGlobalRiskConfiguration(
  token: string,
  configuration: RiskScoringConfigurationUpdate,
) {
  return put<RiskScoringConfiguration>(
    "/api/risk-configurations/global",
    configuration,
    token,
  );
}
