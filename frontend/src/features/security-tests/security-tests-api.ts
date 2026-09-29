import { get, post } from "@/lib/api-client";
import type {
  SecurityTestRun,
  SecurityTestScenario,
} from "@/types/api";

export function getSecurityTestScenarios(token: string) {
  return get<SecurityTestScenario[]>(
    "/api/security-tests/scenarios",
    token,
  );
}

export function getSecurityTestScenario(
  token: string,
  scenarioId: number,
) {
  return get<SecurityTestScenario>(
    `/api/security-tests/scenarios/${scenarioId}`,
    token,
  );
}

export function runSecurityTestScenario(
  token: string,
  scenarioId: number,
) {
  return post<SecurityTestRun>(
    `/api/security-tests/scenarios/${scenarioId}/run`,
    {},
    token,
  );
}