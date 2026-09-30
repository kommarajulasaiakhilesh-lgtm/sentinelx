import type { ReactNode } from "react";

import { SecurityPulse } from "@/components/security/security-pulse";

import { Sidebar } from "./sidebar";
import { Topbar } from "./topbar";

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-[#06090e] text-slate-100">
      <a
        href="#main-content"
        className="fixed left-4 top-4 z-[100] -translate-y-20 rounded-lg border border-cyan-400/30 bg-[#0a0f16] px-4 py-2 text-xs font-semibold text-cyan-300 shadow-xl transition-transform focus:translate-y-0 focus:outline-none focus:ring-2 focus:ring-cyan-400/60"
      >
        Skip to main content
      </a>

      <Sidebar />

      <div className="min-h-screen lg:pl-72">
        <Topbar />

        <main
          id="main-content"
          tabIndex={-1}
          aria-label="SentinelX security operations workspace"
          className="relative min-h-[calc(100vh-4rem)] overflow-hidden outline-none"
        >
          <div
            aria-hidden="true"
            className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_70%_0%,rgba(34,211,238,0.035),transparent_32%),radial-gradient(circle_at_15%_30%,rgba(99,102,241,0.025),transparent_28%)]"
          />

          <div className="relative px-4 py-5 sm:px-6 sm:py-6 lg:px-8 lg:py-7">
            <SecurityPulse />

            <div className="mt-6 [content-visibility:auto]">
              {children}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}