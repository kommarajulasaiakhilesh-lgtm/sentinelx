import { get } from "@/lib/api-client";
import type { SecurityEvent } from "@/types/api";

export interface SecurityEventListResponse {
  items: SecurityEvent[];
  page: number;
  page_size: number;
  total: number;
  pages: number;
}

export function getSecurityEvents(
  token: string,
  page = 1,
  pageSize = 5,
) {
  return get<SecurityEventListResponse>(
    `/api/security-events?page=${page}&page_size=${pageSize}`,
    token,
  );
}

export function getBlockedSecurityEvents(token: string) {
  return get<SecurityEventListResponse>(
    `/api/security-events?decision=BLOCKED&page=1&page_size=1`,
    token,
  );
}