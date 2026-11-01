import { post } from "@/lib/api-client";
import type { LoginRequest, TokenResponse } from "@/types/auth";

export function loginUser(credentials: LoginRequest) {
  return post<TokenResponse>(
    "/api/auth/login",
    credentials,
  );
}

export function changePassword(
  token: string,
  currentPassword: string,
  newPassword: string,
) {
  return post<{ message: string }>(
    "/api/auth/change-password",
    { current_password: currentPassword, new_password: newPassword },
    token,
  );
}
