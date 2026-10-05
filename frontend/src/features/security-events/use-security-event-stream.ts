"use client";

import { useEffect, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@/hooks/use-auth";
import { API_BASE_URL } from "@/lib/api-config";

type SecurityStreamEvent = {
  event?: string;
  data?: unknown;
};

export type SecurityStreamStatus =
  | "CONNECTING"
  | "CONNECTED"
  | "DISCONNECTED";

function parseSseBlock(block: string): SecurityStreamEvent | null {
  const lines = block.split("\n");

  let event = "message";
  let data = "";

  for (const line of lines) {
    if (line.startsWith("event:")) {
      event = line.slice(6).trim();
    }

    if (line.startsWith("data:")) {
      data += line.slice(5).trim();
    }
  }

  if (!data) {
    return null;
  }

  try {
    return {
      event,
      data: JSON.parse(data),
    };
  } catch {
    return {
      event,
      data,
    };
  }
}

export function useSecurityEventStream() {
  const { token } = useAuth();
  const queryClient = useQueryClient();

  const [status, setStatus] =
    useState<SecurityStreamStatus>("DISCONNECTED");

  useEffect(() => {
    if (!token) {
      return;
    }

    const controller = new AbortController();

    async function connect() {
      setStatus("CONNECTING");

      try {
        const response = await fetch(
          `${API_BASE_URL}/api/security-events/stream`,
          {
            method: "GET",
            headers: {
              Accept: "text/event-stream",
              Authorization: `Bearer ${token}`,
              "Cache-Control": "no-cache",
            },
            signal: controller.signal,
          },
        );

        if (!response.ok || !response.body) {
          throw new Error(
            `Security event stream failed with status ${response.status}`,
          );
        }

        setStatus("CONNECTED");

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        let buffer = "";

        while (!controller.signal.aborted) {
          const { done, value } = await reader.read();

          if (done) {
            break;
          }

          buffer += decoder.decode(value, {
            stream: true,
          });

          const blocks = buffer.split("\n\n");
          buffer = blocks.pop() ?? "";

          for (const block of blocks) {
            const streamEvent = parseSseBlock(block);

            if (!streamEvent?.event) {
              continue;
            }

            handleSecurityEvent(
              streamEvent.event,
              queryClient,
            );
          }
        }

        if (!controller.signal.aborted) {
          setStatus("DISCONNECTED");
        }
      } catch (error) {
        if (!controller.signal.aborted) {
          console.error(
            "SentinelX security event stream disconnected:",
            error,
          );

          setStatus("DISCONNECTED");
        }
      }
    }

    void connect();

    return () => {
      controller.abort();
    };
  }, [token, queryClient]);

  return {
    status,
    connected: status === "CONNECTED",
  };
}

function handleSecurityEvent(
  event: string,
  queryClient: ReturnType<typeof useQueryClient>,
) {
  switch (event) {
    case "SECURITY_EVENT":
      queryClient.invalidateQueries({
        queryKey: ["security-events"],
      });

      queryClient.invalidateQueries({
        queryKey: ["analytics"],
      });

      break;

    case "ALERT_CREATED":
    case "ALERT_UPDATED":
      queryClient.invalidateQueries({
        queryKey: ["alerts"],
      });

      queryClient.invalidateQueries({
        queryKey: ["incidents"],
      });

      break;

    case "INCIDENT_CREATED":
    case "INCIDENT_UPDATED":
      queryClient.invalidateQueries({
        queryKey: ["incidents"],
      });

      queryClient.invalidateQueries({
        queryKey: ["alerts"],
      });

      break;

    case "RESPONSE_ACTION":
      queryClient.invalidateQueries({
        queryKey: ["agents"],
      });

      queryClient.invalidateQueries({
        queryKey: ["incidents"],
      });

      queryClient.invalidateQueries({
        queryKey: ["tools"],
      });

      queryClient.invalidateQueries({
        queryKey: ["agent-api-keys"],
      });

      break;

    default:
      break;
  }
}