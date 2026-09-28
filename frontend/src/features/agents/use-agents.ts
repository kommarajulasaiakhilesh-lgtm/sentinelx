"use client";

import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@/hooks/use-auth";
import { getMyAgents } from "./agents-api";

export function useMyAgents() {
  const { token } = useAuth();

  return useQuery({
    queryKey: ["agents", "my-agents"],
    queryFn: () => getMyAgents(token as string),
    enabled: Boolean(token),
  });
}