const TOKEN_KEY = "sentinelx_access_token";
export const AUTH_SESSION_EXPIRED_EVENT = "sentinelx:auth-session-expired";

export function getAccessToken(): string | null {
  if (typeof window === "undefined") {
    return null;
  }

  return window.localStorage.getItem(TOKEN_KEY);
}

export function setAccessToken(token: string): void {
  window.localStorage.setItem(TOKEN_KEY, token);
}

export function clearAccessToken(): void {
  window.localStorage.removeItem(TOKEN_KEY);
}

export function expireAccessToken(): void {
  if (typeof window === "undefined") {
    return;
  }

  clearAccessToken();
  window.dispatchEvent(new Event(AUTH_SESSION_EXPIRED_EVENT));
}
