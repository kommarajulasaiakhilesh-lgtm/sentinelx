"use client";

import {
  createContext,
  useCallback,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { loginUser } from "./auth-api";
import {
  clearAccessToken,
  getAccessToken,
  setAccessToken,
} from "./auth-storage";

interface AuthContextValue {
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => getAccessToken());
  const [isLoading] = useState(false);

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

  const value = useMemo(
    () => ({
      token,
      isAuthenticated: Boolean(token),
      isLoading,
      login,
      logout,
    }),
    [token, isLoading, login, logout],
  );

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export { AuthContext };