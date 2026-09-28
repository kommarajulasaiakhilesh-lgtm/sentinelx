"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { AnimatePresence, motion } from "motion/react";
import {
  ArrowRight,
  Eye,
  EyeOff,
  Fingerprint,
  KeyRound,
  LockKeyhole,
  Radar,
  ShieldCheck,
  Terminal,
  UserRound,
  XCircle,
} from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { useAuth } from "@/hooks/use-auth";

const loginSchema = z.object({
  username: z
    .string()
    .min(1, "Operator identity is required")
    .min(3, "Identity must contain at least 3 characters"),
  password: z
    .string()
    .min(1, "Access credential is required")
    .min(6, "Credential must contain at least 6 characters"),
});

type LoginFormValues = z.infer<typeof loginSchema>;

export function LoginForm() {
  const router = useRouter();
  const { login } = useAuth();

  const [showPassword, setShowPassword] = useState(false);
  const [authError, setAuthError] = useState<string | null>(null);
  const [isAuthenticating, setIsAuthenticating] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    mode: "onTouched",
  });

  const onSubmit = async (values: LoginFormValues) => {
    setAuthError(null);
    setIsAuthenticating(true);

    try {
      await login(values.username, values.password);
      router.replace("/");
    } catch (error) {
      setAuthError(
        error instanceof Error
          ? error.message
          : "Authentication failed. Verify your credentials.",
      );
    } finally {
      setIsAuthenticating(false);
    }
  };

  return (
    <div className="relative w-full max-w-5xl">
      <div className="absolute -inset-20 rounded-full bg-cyan-400/[0.035] blur-3xl" />

      <div className="relative grid overflow-hidden rounded-3xl border border-white/10 bg-[#090c12]/90 shadow-2xl shadow-black/60 backdrop-blur-2xl lg:grid-cols-[1.05fr_0.95fr]">
        {/* Left security visualization */}
        <div className="relative hidden min-h-[620px] overflow-hidden border-r border-white/10 lg:block">
          <div className="absolute inset-0 security-grid opacity-50" />
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_45%,rgba(34,211,238,0.12),transparent_30%),linear-gradient(180deg,transparent,rgba(6,8,12,0.85))]" />

          <div className="absolute left-8 right-8 top-8 flex items-center justify-between">
            <div className="flex items-center gap-2 text-[10px] uppercase tracking-[0.2em] text-slate-500">
              <Terminal className="size-3.5 text-cyan-400" />
              Secure access layer
            </div>

            <div className="flex items-center gap-2 rounded-full border border-emerald-400/15 bg-emerald-400/5 px-3 py-1.5 text-[10px] uppercase tracking-[0.14em] text-emerald-300">
              <span className="size-1.5 animate-pulse rounded-full bg-emerald-400" />
              Systems nominal
            </div>
          </div>

          <div className="absolute inset-0 flex items-center justify-center">
            <div className="relative size-72">
              <div className="absolute inset-0 rounded-full border border-cyan-400/10" />
              <div className="absolute inset-7 rounded-full border border-cyan-400/10" />
              <div className="absolute inset-14 rounded-full border border-cyan-400/15" />

              <motion.div
                className="absolute inset-0 rounded-full border border-transparent border-t-cyan-300/70"
                animate={{ rotate: 360 }}
                transition={{
                  duration: 7,
                  repeat: Infinity,
                  ease: "linear",
                }}
              />

              <motion.div
                className="absolute inset-10 rounded-full border border-transparent border-r-cyan-400/50"
                animate={{ rotate: -360 }}
                transition={{
                  duration: 11,
                  repeat: Infinity,
                  ease: "linear",
                }}
              />

              <div className="absolute inset-0 flex items-center justify-center">
                <div className="relative flex size-28 items-center justify-center rounded-full border border-cyan-300/20 bg-cyan-400/[0.04] shadow-[0_0_80px_rgba(34,211,238,0.08)]">
                  <div className="absolute inset-3 rounded-full border border-cyan-400/10" />
                  <ShieldCheck className="size-12 text-cyan-300" strokeWidth={1.3} />
                </div>
              </div>

              <motion.div
                className="absolute left-1/2 top-1/2 h-px w-36 origin-left bg-gradient-to-r from-cyan-300/60 to-transparent"
                animate={{ rotate: [0, 360] }}
                transition={{
                  duration: 5,
                  repeat: Infinity,
                  ease: "linear",
                }}
              />

              <div className="absolute left-1/2 top-1/2 size-2 -translate-x-1/2 -translate-y-1/2 rounded-full bg-cyan-300 shadow-[0_0_20px_rgba(103,232,249,0.9)]" />
            </div>
          </div>

          <div className="absolute bottom-8 left-8 right-8">
            <div className="mb-4 flex items-center gap-3">
              <Radar className="size-4 text-cyan-400" />
              <span className="text-[10px] uppercase tracking-[0.22em] text-cyan-300">
                Sentinel perimeter
              </span>
            </div>

            <h2 className="max-w-md text-3xl font-semibold tracking-tight text-white">
              One gateway.
              <br />
              <span className="text-slate-500">Every agent under control.</span>
            </h2>

            <div className="mt-6 grid grid-cols-3 gap-3">
              <StatusNode label="IDENTITY" value="READY" />
              <StatusNode label="POLICY" value="ARMED" />
              <StatusNode label="RUNTIME" value="ONLINE" />
            </div>
          </div>
        </div>

        {/* Authentication panel */}
        <div className="relative flex min-h-[620px] flex-col justify-center px-6 py-10 sm:px-10 lg:px-12">
          <div className="mx-auto w-full max-w-md">
            <div className="mb-8">
              <div className="mb-6 flex items-center gap-3 lg:hidden">
                <div className="flex size-11 items-center justify-center rounded-xl border border-cyan-400/20 bg-cyan-400/10">
                  <ShieldCheck className="size-5 text-cyan-300" />
                </div>

                <div>
                  <div className="text-sm font-semibold tracking-[0.2em] text-white">
                    SENTINELX
                  </div>
                  <div className="text-[9px] uppercase tracking-[0.16em] text-slate-500">
                    Security Control Plane
                  </div>
                </div>
              </div>

              <div className="mb-3 flex items-center gap-2 text-[10px] font-medium uppercase tracking-[0.2em] text-cyan-400">
                <Fingerprint className="size-3.5" />
                Operator authentication
              </div>

              <h1 className="text-3xl font-semibold tracking-tight text-white">
                Enter the control plane.
              </h1>

              <p className="mt-3 max-w-sm text-sm leading-6 text-slate-500">
                Authenticate your operator identity to access SentinelX security
                operations.
              </p>
            </div>

            <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
              <div>
                <label
                  htmlFor="username"
                  className="mb-2 block text-[10px] font-semibold uppercase tracking-[0.17em] text-slate-500"
                >
                  Operator identity
                </label>

                <div
                  className={`group flex h-13 items-center rounded-xl border bg-white/[0.025] px-4 transition ${
                    errors.username
                      ? "border-red-400/40"
                      : "border-white/10 focus-within:border-cyan-400/40 focus-within:bg-cyan-400/[0.025]"
                  }`}
                >
                  <UserRound className="mr-3 size-4 text-slate-600 transition group-focus-within:text-cyan-400" />

                  <input
                    id="username"
                    type="text"
                    autoComplete="username"
                    placeholder="Enter operator identity"
                    className="h-full w-full bg-transparent text-sm text-slate-100 outline-none placeholder:text-slate-700"
                    {...register("username")}
                  />

                  <span className="ml-3 hidden font-mono text-[9px] text-slate-700 sm:block">
                    ID
                  </span>
                </div>

                {errors.username && (
                  <p className="mt-2 text-xs text-red-400">
                    {errors.username.message}
                  </p>
                )}
              </div>

              <div>
                <label
                  htmlFor="password"
                  className="mb-2 block text-[10px] font-semibold uppercase tracking-[0.17em] text-slate-500"
                >
                  Access credential
                </label>

                <div
                  className={`group flex h-13 items-center rounded-xl border bg-white/[0.025] px-4 transition ${
                    errors.password
                      ? "border-red-400/40"
                      : "border-white/10 focus-within:border-cyan-400/40 focus-within:bg-cyan-400/[0.025]"
                  }`}
                >
                  <LockKeyhole className="mr-3 size-4 text-slate-600 transition group-focus-within:text-cyan-400" />

                  <input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    autoComplete="current-password"
                    placeholder="Enter access credential"
                    className="h-full w-full bg-transparent text-sm text-slate-100 outline-none placeholder:text-slate-700"
                    {...register("password")}
                  />

                  <button
                    type="button"
                    onClick={() => setShowPassword((value) => !value)}
                    className="ml-2 rounded-md p-1.5 text-slate-600 transition hover:text-slate-300"
                    aria-label={
                      showPassword ? "Hide password" : "Show password"
                    }
                  >
                    {showPassword ? (
                      <EyeOff className="size-4" />
                    ) : (
                      <Eye className="size-4" />
                    )}
                  </button>
                </div>

                {errors.password && (
                  <p className="mt-2 text-xs text-red-400">
                    {errors.password.message}
                  </p>
                )}
              </div>

              <AnimatePresence mode="wait">
                {authError && (
                  <motion.div
                    initial={{ opacity: 0, height: 0, y: -6 }}
                    animate={{ opacity: 1, height: "auto", y: 0 }}
                    exit={{ opacity: 0, height: 0, y: -6 }}
                    className="overflow-hidden"
                  >
                    <div className="flex items-start gap-3 rounded-xl border border-red-400/15 bg-red-400/[0.05] p-3.5">
                      <XCircle className="mt-0.5 size-4 shrink-0 text-red-400" />
                      <div>
                        <div className="text-xs font-medium text-red-300">
                          Authentication rejected
                        </div>
                        <div className="mt-1 text-[11px] leading-5 text-red-300/60">
                          {authError}
                        </div>
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

              <button
                type="submit"
                disabled={isAuthenticating}
                className="group relative flex h-13 w-full items-center justify-center overflow-hidden rounded-xl border border-cyan-300/20 bg-cyan-400/10 text-sm font-medium text-cyan-100 transition hover:border-cyan-300/40 hover:bg-cyan-400/15 disabled:cursor-not-allowed disabled:opacity-60"
              >
                <span className="absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-cyan-300/[0.08] to-transparent transition-transform duration-700 group-hover:translate-x-full" />

                {isAuthenticating ? (
                  <span className="relative flex items-center gap-3">
                    <span className="size-4 animate-spin rounded-full border-2 border-cyan-200/20 border-t-cyan-200" />
                    Establishing secure session...
                  </span>
                ) : (
                  <span className="relative flex items-center gap-2">
                    Authenticate operator
                    <ArrowRight className="size-4 transition-transform group-hover:translate-x-1" />
                  </span>
                )}
              </button>
            </form>

            <div className="mt-8 border-t border-white/5 pt-5">
              <div className="flex items-center justify-between text-[9px] uppercase tracking-[0.15em] text-slate-600">
                <span className="flex items-center gap-2">
                  <KeyRound className="size-3" />
                  JWT protected session
                </span>
                <span className="flex items-center gap-1.5">
                  <span className="size-1.5 rounded-full bg-emerald-400" />
                  API online
                </span>
              </div>

              <p className="mt-3 text-[10px] leading-5 text-slate-700">
                Unauthorized access is prohibited. All authenticated activity
                is subject to SentinelX security policies and audit controls.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatusNode({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-lg border border-white/5 bg-white/[0.02] px-3 py-2.5">
      <div className="text-[8px] font-semibold tracking-[0.15em] text-slate-600">
        {label}
      </div>
      <div className="mt-1 flex items-center gap-1.5 text-[9px] font-medium tracking-[0.1em] text-emerald-400">
        <span className="size-1 rounded-full bg-emerald-400" />
        {value}
      </div>
    </div>
  );
}