"use client";

import {
  useEffect,
  useSyncExternalStore,
  type ReactNode,
} from "react";
import { usePathname, useRouter } from "next/navigation";

import { useAuth } from "@/hooks/use-auth";
import { AppShell } from "@/components/layout/app-shell";

const emptySubscribe = () => () => {};

function useHydrated() {
  return useSyncExternalStore(
    emptySubscribe,
    () => true,
    () => false,
  );
}

export function AuthGate({ children }: { children: ReactNode }) {
  const { token } = useAuth();
  const pathname = usePathname();
  const router = useRouter();
  const hydrated = useHydrated();

  useEffect(() => {
    if (!hydrated) {
      return;
    }

    if (!token && pathname !== "/login") {
      router.replace("/login");
    }
  }, [hydrated, token, pathname, router]);

  if (!hydrated) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-[#06090e]">
        <div className="text-center">
          <div className="mx-auto h-8 w-8 animate-spin rounded-full border-2 border-cyan-400/20 border-t-cyan-400" />

          <p className="mt-4 text-xs font-medium uppercase tracking-[0.2em] text-slate-500">
            Initializing SentinelX
          </p>
        </div>
      </main>
    );
  }

  if (!token && pathname !== "/login") {
    return (
      <main className="flex min-h-screen items-center justify-center bg-[#06090e]">
        <div className="text-center">
          <div className="mx-auto h-8 w-8 animate-spin rounded-full border-2 border-cyan-400/20 border-t-cyan-400" />

          <p className="mt-4 text-xs font-medium uppercase tracking-[0.2em] text-slate-500">
            Redirecting to security gateway
          </p>
        </div>
      </main>
    );
  }

  if (pathname === "/login") {
    return <>{children}</>;
  }

  return <AppShell>{children}</AppShell>;
}