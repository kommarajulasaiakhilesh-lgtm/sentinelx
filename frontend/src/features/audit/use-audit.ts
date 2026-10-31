"use client";

import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@/hooks/use-auth";
import { getAuditLog } from "./audit-api";

export function useAuditLog(action?: string) {
  const { token } = useAuth();

  return useQuery({
    queryKey: ["audit", action ?? "all"],
    queryFn: () => getAuditLog(token as string, action),
    enabled: Boolean(token),
  });
}
