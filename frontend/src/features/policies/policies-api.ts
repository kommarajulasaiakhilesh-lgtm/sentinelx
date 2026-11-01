import { get, post } from "@/lib/api-client";
import type { Policy } from "@/types/api";

export function getAgentPolicies(token: string, agentId: number) {
  return get<Policy[]>(
    `/api/policies/agent/${agentId}`,
    token,
  );
}

export type PolicyVersion = {
  id: number;
  version_number: number;
  name: string;
  policy_type: string;
  action: string;
  priority: number;
  enabled: boolean;
  change_note: string;
  created_at: string | null;
};

export function getPolicyVersions(token: string, policyId: number) {
  return get<{ count: number; versions: PolicyVersion[] }>(
    `/api/policies/policy/${policyId}/versions`,
    token,
  );
}

export function rollbackPolicy(
  token: string,
  policyId: number,
  versionNumber: number,
) {
  return post<Policy>(
    `/api/policies/policy/${policyId}/rollback/${versionNumber}`,
    {},
    token,
  );
}