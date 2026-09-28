import { get } from "@/lib/api-client";
import type { SecurityAlert } from "@/types/api";

export interface SecurityAlertListResponse {
  items: SecurityAlert[];
  page: number;
  page_size: number;
  total: number;
  pages: number;
}

export function getSecurityAlerts(
  token: string,
  page = 1,
  pageSize = 5,
) {
  return get<SecurityAlertListResponse>(
    `/api/security-alerts?page=${page}&page_size=${pageSize}`,
    token,
  );
}