import { API_BASE_URL } from "./api-config";

type ApiRequestOptions = RequestInit & {
  token?: string;
};

export async function apiRequest<T>(
  path: string,
  options: ApiRequestOptions = {},
): Promise<T> {
  const { token, headers, ...requestOptions } = options;

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...requestOptions,
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
      ...(token
        ? {
            Authorization: `Bearer ${token}`,
          }
        : {}),
      ...headers,
    },
  });

  if (!response.ok) {
    let message = `API request failed with status ${response.status}`;

    try {
      const errorBody = await response.json();

      if (typeof errorBody?.detail === "string") {
        message = errorBody.detail;
      }
    } catch {
      // Keep the default error message when the response is not JSON.
    }

    throw new Error(message);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export function get<T>(path: string, token?: string) {
  return apiRequest<T>(path, {
    method: "GET",
    token,
  });
}

export function post<T>(
  path: string,
  body: unknown,
  token?: string,
) {
  return apiRequest<T>(path, {
    method: "POST",
    body: JSON.stringify(body),
    token,
  });
}

export function put<T>(
  path: string,
  body: unknown,
  token?: string,
) {
  return apiRequest<T>(path, {
    method: "PUT",
    body: JSON.stringify(body),
    token,
  });
}

export function del<T>(path: string, token?: string) {
  return apiRequest<T>(path, {
    method: "DELETE",
    token,
  });
}