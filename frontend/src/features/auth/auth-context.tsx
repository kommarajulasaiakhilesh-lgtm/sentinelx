"use client";

import {
  createContext,
  useCallback,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { loginUser } from "./auth-api";
import {
  clearAccessToken,
  getAccessToken,
  setAccessToken,
  AUTH_SESSION_EXPIRED_EVENT,
} from "./auth-storage";

interface AuthUser {
  id: string | null;
  username: string | null;
  role: string | null;
}

interface AuthContextValue {
  token: string | null;
  user: AuthUser | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

function decodeUser(token: string | null): AuthUser | null {
  if (!token) return null;
  try {
    const payload = token.split(".")[1];
    if (!payload) return null;
    const normalized = payload.replace(/-/g, "+").replace(/_/g, "/");
    const json = JSON.parse(atob(normalized));
    return {
      id: json.sub ?? null,
      username: json.username ?? null,
      role: json.role ?? null,
    };
  } catch {
    return null;
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => getAccessToken());
  const [isLoading] = useState(false);

  useEffect(() => {
    const handleSessionExpired = () => setToken(null);
    window.addEventListener(AUTH_SESSION_EXPIRED_EVENT, handleSessionExpired);
    return () => {
      window.removeEventListener(
        AUTH_SESSION_EXPIRED_EVENT,
        handleSessionExpired,
      );
    };
  }, []);

  const login = useCallback(
    async (username: string, password: string) => {
      const response = await loginUser({
        username,
        password,
      });

      setAccessToken(response.access_token);
      setToken(response.access_token);
    },
    [],
  );

  const logout = useCallback(() => {
    clearAccessToken();
    setToken(null);
  }, []);

  const user = useMemo(() => decodeUser(token), [token]);

  const value = useMemo(
    () => ({
      token,
      user,
      isAuthenticated: Boolean(token),
      isLoading,
      login,
      logout,
    }),
    [token, user, isLoading, login, logout],
  );

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export { AuthContext };
