"use client";

import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@/hooks/use-auth";
import {
  getBlockedSecurityEvents,
  getSecurityEvents,
} from "./events-api";

export function useSecurityEvents(page = 1, pageSize = 5) {
  const { token } = useAuth();

  return useQuery({
    queryKey: ["security-events", page, pageSize],
    queryFn: () => getSecurityEvents(token as string, page, pageSize),
    enabled: Boolean(token),
  });
}

export function useBlockedSecurityEvents() {
  const { token } = useAuth();

  return useQuery({
    queryKey: ["security-events", "blocked"],
    queryFn: () => getBlockedSecurityEvents(token as string),
    enabled: Boolean(token),
  });
}