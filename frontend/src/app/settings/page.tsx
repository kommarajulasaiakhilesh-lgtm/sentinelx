"use client";

import { useState } from "react";
import { motion } from "motion/react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import {
  CheckCircle2,
  Eye,
  EyeOff,
  LockKeyhole,
  ShieldCheck,
  UserRound,
  XCircle,
} from "lucide-react";

import { useAuth } from "@/hooks/use-auth";
import { changePassword } from "@/features/auth/auth-api";
import { useToast } from "@/components/ui/toast";

const schema = z
  .object({
    currentPassword: z.string().min(1, "Enter your current password"),
    newPassword: z
      .string()
      .min(6, "New password must be at least 6 characters")
      .max(1024),
    confirmPassword: z.string().min(1, "Confirm your new password"),
  })
  .refine((v) => v.newPassword === v.confirmPassword, {
    message: "Passwords do not match",
    path: ["confirmPassword"],
  })
  .refine((v) => v.newPassword !== v.currentPassword, {
    message: "New password must differ from the current one",
    path: ["newPassword"],
  });

type FormValues = z.infer<typeof schema>;

export default function SettingsPage() {
  const { token, user } = useAuth();
  const toast = useToast();
  const [showCurrent, setShowCurrent] = useState(false);
  const [showNew, setShowNew] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<FormValues>({ resolver: zodResolver(schema), mode: "onTouched" });

  const onSubmit = async (values: FormValues) => {
    setError(null);
    setSuccess(false);
    setSubmitting(true);
    try {
      await changePassword(
        token as string,
        values.currentPassword,
        values.newPassword,
      );
      setSuccess(true);
      reset();
      toast({
        variant: "success",
        title: "Password changed",
        description: "Your access credential was updated.",
      });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not change password.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      <section className="security-surface relative overflow-hidden">
        <div className="absolute inset-0 security-grid opacity-40" />
        <div className="relative px-6 py-6">
          <div className="mb-2 flex items-center gap-2 text-[10px] font-semibold uppercase tracking-[0.2em] text-indigo-600 dark:text-indigo-400">
            <ShieldCheck className="size-3.5" />
            Account
          </div>
          <h1 className="text-3xl font-semibold tracking-tight text-slate-900 dark:text-slate-100">
            Account &amp; Security
          </h1>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500 dark:text-slate-400">
            Manage the credentials for your operator identity.
          </p>
        </div>
      </section>

      <div className="grid gap-6 lg:grid-cols-[minmax(0,0.7fr)_minmax(0,1.3fr)]">
        {/* Identity card */}
        <motion.div
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
          className="security-surface p-6"
        >
          <div className="flex items-center gap-3">
            <div className="flex size-12 items-center justify-center rounded-full border border-indigo-200 dark:border-indigo-500/30 bg-indigo-50 dark:bg-indigo-500/10 text-sm font-semibold text-indigo-600 dark:text-indigo-400">
              {(user?.username ?? "OP").slice(0, 2).toUpperCase()}
            </div>
            <div>
              <div className="text-sm font-semibold text-slate-900 dark:text-slate-100">
                {user?.username ?? "Operator"}
              </div>
              <div className="text-[11px] text-slate-500 dark:text-slate-400">
                {user?.role === "ADMIN" ? "Administrator" : "Operator"}
              </div>
            </div>
          </div>
          <div className="mt-5 space-y-3 border-t border-slate-200 dark:border-slate-800 pt-5 text-[11px] text-slate-500 dark:text-slate-400">
            <div className="flex items-center gap-2">
              <UserRound className="size-3.5 text-slate-400 dark:text-slate-500" />
              Operator ID: {user?.id ?? "—"}
            </div>
            <div className="flex items-center gap-2">
              <LockKeyhole className="size-3.5 text-slate-400 dark:text-slate-500" />
              JWT-protected session
            </div>
          </div>
        </motion.div>

        {/* Change password */}
        <motion.div
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.08, ease: [0.22, 1, 0.36, 1] }}
          className="security-surface p-6"
        >
          <h2 className="text-sm font-semibold text-slate-900 dark:text-slate-100">
            Change password
          </h2>
          <p className="mt-1 text-[11px] text-slate-500 dark:text-slate-400">
            Choose a strong, unique password. You&apos;ll stay signed in on this
            device.
          </p>

          {success && (
            <motion.div
              initial={{ opacity: 0, y: -6 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-4 flex items-center gap-2 rounded-xl border border-emerald-200 dark:border-emerald-500/30 bg-emerald-50 dark:bg-emerald-500/10 px-3.5 py-3 text-xs text-emerald-700 dark:text-emerald-400"
            >
              <CheckCircle2 className="size-4" />
              Password changed successfully.
            </motion.div>
          )}

          {error && (
            <motion.div
              initial={{ opacity: 0, y: -6 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-4 flex items-center gap-2 rounded-xl border border-red-200 dark:border-red-500/30 bg-red-50 dark:bg-red-500/10 px-3.5 py-3 text-xs text-red-700 dark:text-red-400"
            >
              <XCircle className="size-4" />
              {error}
            </motion.div>
          )}

          <form onSubmit={handleSubmit(onSubmit)} className="mt-5 space-y-4">
            <PasswordInput
              label="Current password"
              visible={showCurrent}
              onToggle={() => setShowCurrent((v) => !v)}
              error={errors.currentPassword?.message}
              {...register("currentPassword")}
            />
            <PasswordInput
              label="New password"
              visible={showNew}
              onToggle={() => setShowNew((v) => !v)}
              error={errors.newPassword?.message}
              {...register("newPassword")}
            />
            <PasswordInput
              label="Confirm new password"
              visible={showNew}
              onToggle={() => setShowNew((v) => !v)}
              error={errors.confirmPassword?.message}
              {...register("confirmPassword")}
            />

            <button
              type="submit"
              disabled={submitting}
              className="inline-flex h-10 items-center justify-center gap-2 rounded-lg bg-indigo-600 px-5 text-sm font-medium text-white transition-colors hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {submitting ? "Updating…" : "Update password"}
            </button>
          </form>
        </motion.div>
      </div>
    </div>
  );
}

const PasswordInput = ({
  label,
  visible,
  onToggle,
  error,
  ...props
}: {
  label: string;
  visible: boolean;
  onToggle: () => void;
  error?: string;
} & React.InputHTMLAttributes<HTMLInputElement>) => {
  return (
    <div>
      <label className="mb-1.5 block text-[10px] font-semibold uppercase tracking-[0.14em] text-slate-500 dark:text-slate-400">
        {label}
      </label>
      <div
        className={`flex h-11 items-center rounded-xl border bg-white dark:bg-slate-900 px-3.5 transition ${
          error
            ? "border-red-300"
            : "border-slate-200 dark:border-slate-800 focus-within:border-indigo-400"
        }`}
      >
        <LockKeyhole className="mr-2.5 size-4 text-slate-400 dark:text-slate-500" />
        <input
          type={visible ? "text" : "password"}
          autoComplete="off"
          className="h-full w-full bg-transparent text-sm text-slate-900 dark:text-slate-100 outline-none placeholder:text-slate-400 dark:placeholder:text-slate-500"
          {...props}
        />
        <button
          type="button"
          onClick={onToggle}
          className="ml-2 rounded-md p-1 text-slate-400 dark:text-slate-500 transition hover:text-slate-600 dark:hover:text-slate-300"
          aria-label={visible ? "Hide password" : "Show password"}
        >
          {visible ? <EyeOff className="size-4" /> : <Eye className="size-4" />}
        </button>
      </div>
      {error && <p className="mt-1.5 text-xs text-red-600 dark:text-red-400">{error}</p>}
    </div>
  );
};
