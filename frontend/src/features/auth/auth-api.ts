import { post } from "@/lib/api-client";
import type { LoginRequest, TokenResponse } from "@/types/auth";

export function loginUser(credentials: LoginRequest) {
  return post<TokenResponse>(
    "/api/auth/login",
    credentials,
  );
}
