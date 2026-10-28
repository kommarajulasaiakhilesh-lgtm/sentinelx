
"use client";

import { useEffect, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@/hooks/use-auth";
import { API_BASE_URL } from "@/lib/api-config";
import { expireAccessToken } from "@/features/auth/auth-storage";

type SecurityStreamEvent = {
  event?: string;
  data?: unknown;
};

export type SecurityStreamStatus =
  | "CONNECTING"
  | "CONNECTED"
  | "DISCONNECTED";

const INITIAL_RETRY_DELAY_MS = 1_000;
const MAX_RETRY_DELAY_MS = 30_000;
const STABLE_CONNECTION_MS = 30_000;

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

function waitForRetry(
  delayMs: number,
  signal: AbortSignal,
): Promise<void> {
  return new Promise((resolve) => {
    if (signal.aborted) {
      resolve();
      return;
    }

    const finish = () => {
      clearTimeout(timeoutId);
      signal.removeEventListener("abort", finish);
      resolve();
    };

    const timeoutId = setTimeout(finish, delayMs);

    signal.addEventListener("abort", finish, { once: true });
  });
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
    const { signal } = controller;

    let retryDelay = INITIAL_RETRY_DELAY_MS;

    async function connectWithRetry() {
      while (!signal.aborted) {
        let connectedAt: number | null = null;

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
              signal,
            },
          );

          if (!response.ok || !response.body) {
            if (response.status === 401 || response.status === 403) {
              expireAccessToken();
              break;
            }

            throw new Error(
              `Security event stream failed with status ${response.status}`,
            );
          }

          connectedAt = Date.now();
          setStatus("CONNECTED");

          const reader = response.body.getReader();
          const decoder = new TextDecoder();
          let buffer = "";

          try {
            while (!signal.aborted) {
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
          } finally {
            reader.releaseLock();
          }

          if (!signal.aborted) {
            throw new Error("Security event stream ended");
          }
        } catch (error) {
          if (signal.aborted) {
            break;
          }

          console.warn(
            "SentinelX security event stream disconnected; retrying:",
            error,
          );
        }

        if (signal.aborted) {
          break;
        }

        // Reset backoff after a connection remained healthy for 30 seconds.
        if (
          connectedAt !== null &&
          Date.now() - connectedAt >= STABLE_CONNECTION_MS
        ) {
          retryDelay = INITIAL_RETRY_DELAY_MS;
        }

        setStatus("DISCONNECTED");

        await waitForRetry(retryDelay, signal);

        retryDelay = Math.min(
          retryDelay * 2,
          MAX_RETRY_DELAY_MS,
        );
      }
    }

    void connectWithRetry();

    return () => {
      controller.abort();
    };
  }, [token, queryClient]);

   const effectiveStatus: SecurityStreamStatus = token
    ? status
    : "DISCONNECTED";

  return {
    status: effectiveStatus,
    connected: effectiveStatus === "CONNECTED",
  };
}

function handleSecurityEvent(
  event: string,
  queryClient: ReturnType<typeof useQueryClient>,
) {
  switch (event) {
    case "STREAM_RESET":
      for (const queryKey of [
        ["agents"],
        ["agent-api-keys"],
        ["analytics"],
        ["security-events"],
        ["security-alerts"],
        ["incidents"],
        ["tools"],
      ]) {
        queryClient.invalidateQueries({ queryKey });
      }
      break;

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
        queryKey: ["security-alerts"],
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
        queryKey: ["security-alerts"],
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
