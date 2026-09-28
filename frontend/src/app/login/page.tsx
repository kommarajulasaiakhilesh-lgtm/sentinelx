import { LoginForm } from "@/features/auth/login-form";

export default function LoginPage() {
  return (
    <main className="relative flex min-h-screen items-center justify-center overflow-hidden bg-[#06080c] px-4 py-8 sm:px-6">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute left-[10%] top-[15%] size-72 rounded-full bg-cyan-400/[0.025] blur-3xl" />
        <div className="absolute bottom-[5%] right-[10%] size-96 rounded-full bg-blue-500/[0.02] blur-3xl" />

        <div className="absolute left-0 right-0 top-1/2 h-px bg-gradient-to-r from-transparent via-white/[0.025] to-transparent" />
        <div className="absolute bottom-0 left-1/2 top-0 w-px bg-gradient-to-b from-transparent via-white/[0.025] to-transparent" />
      </div>

      <div className="absolute left-5 top-5 hidden items-center gap-2 text-[9px] uppercase tracking-[0.18em] text-slate-700 sm:flex">
        <span className="size-1.5 rounded-full bg-cyan-400/70" />
        SX // AUTH GATEWAY
      </div>

      <div className="absolute right-5 top-5 hidden font-mono text-[9px] uppercase tracking-[0.15em] text-slate-700 sm:block">
        NODE: CONTROL-01
      </div>

      <LoginForm />

      <div className="absolute bottom-5 left-0 right-0 hidden justify-center text-[9px] uppercase tracking-[0.16em] text-slate-700 sm:flex">
        SENTINELX // AI AGENT SECURITY CONTROL PLANE
      </div>
    </main>
  );
}