"use client";

import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@/hooks/use-auth";
import { getFleetPosture } from "./posture-api";

export function useFleetPosture() {
  const { token } = useAuth();

  return useQuery({
    queryKey: ["posture", "fleet"],
    queryFn: () => getFleetPosture(token as string),
    enabled: Boolean(token),
  });
}
