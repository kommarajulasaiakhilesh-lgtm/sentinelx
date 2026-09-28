"use client";

import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@/hooks/use-auth";
import { getSecurityAlerts } from "./alerts-api";

export function useSecurityAlerts(page = 1, pageSize = 5) {
  const { token } = useAuth();

  return useQuery({
    queryKey: ["security-alerts", page, pageSize],
    queryFn: () => getSecurityAlerts(token as string, page, pageSize),
    enabled: Boolean(token),
  });
}