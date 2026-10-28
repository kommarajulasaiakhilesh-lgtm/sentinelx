import assert from "node:assert/strict";
import test from "node:test";
import {
  AUTH_SESSION_EXPIRED_EVENT,
  expireAccessToken,
} from "../src/features/auth/auth-storage.ts";
import nextConfig from "../next.config.ts";

test("expiring a session removes the bearer token and notifies the app", () => {
  const removed = [];
  const events = [];
  globalThis.window = {
    localStorage: {
      removeItem: (key) => removed.push(key),
    },
    dispatchEvent: (event) => events.push(event.type),
  };

  try {
    expireAccessToken();

    assert.deepEqual(removed, ["sentinelx_access_token"]);
    assert.deepEqual(events, [AUTH_SESSION_EXPIRED_EVENT]);
  } finally {
    delete globalThis.window;
  }
});

test("all frontend routes return browser security headers", async () => {
  const rules = await nextConfig.headers();
  const rule = rules.find((entry) => entry.source === "/:path*");
  const headers = Object.fromEntries(
    rule.headers.map(({ key, value }) => [key, value]),
  );

  assert.equal(headers["X-Content-Type-Options"], "nosniff");
  assert.equal(headers["X-Frame-Options"], "DENY");
  assert.match(headers["Content-Security-Policy"], /frame-ancestors 'none'/);
  assert.equal(
    headers["Referrer-Policy"],
    "strict-origin-when-cross-origin",
  );
});
