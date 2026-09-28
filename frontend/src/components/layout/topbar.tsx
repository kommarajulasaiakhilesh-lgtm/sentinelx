"use client";

import { Bell, LogOut, Menu, Search, ShieldCheck } from "lucide-react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/use-auth";

export function Topbar() {
  const router = useRouter();
  const { logout } = useAuth();

  const handleLogout = () => {
    logout();
    router.replace("/login");
  };

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-white/10 bg-[#090b10]/90 px-4 backdrop-blur-xl sm:px-6 lg:px-8">
      <div className="flex items-center gap-3">
        <button
          type="button"
          className="flex size-9 items-center justify-center rounded-lg border border-white/10 text-slate-400 transition hover:bg-white/[0.05] hover:text-white lg:hidden"
          aria-label="Open navigation"
        >
          <Menu className="size-4" />
        </button>

        <div className="hidden items-center gap-2 text-xs text-slate-500 sm:flex">
          <ShieldCheck className="size-4 text-cyan-400" />
          <span>Security Operations</span>
          <span className="text-slate-700">/</span>
          <span className="text-slate-300">Command Center</span>
        </div>
      </div>

      <div className="flex items-center gap-2 sm:gap-3">
        <button
          type="button"
          className="flex size-9 items-center justify-center rounded-lg border border-white/10 text-slate-400 transition hover:bg-white/[0.05] hover:text-white"
          aria-label="Search"
        >
          <Search className="size-4" />
        </button>

        <button
          type="button"
          className="relative flex size-9 items-center justify-center rounded-lg border border-white/10 text-slate-400 transition hover:bg-white/[0.05] hover:text-white"
          aria-label="Notifications"
        >
          <Bell className="size-4" />
          <span className="absolute right-2 top-2 size-1.5 rounded-full bg-red-400" />
        </button>

        <div className="hidden h-8 w-px bg-white/10 sm:block" />

        <div className="hidden items-center gap-2 sm:flex">
          <div className="flex size-8 items-center justify-center rounded-full border border-cyan-400/20 bg-cyan-400/10 text-xs font-semibold text-cyan-300">
            SX
          </div>

          <div className="hidden text-left md:block">
            <div className="text-xs font-medium text-slate-200">
              Security Admin
            </div>
            <div className="text-[10px] text-slate-500">
              Control Plane
            </div>
          </div>
        </div>

        <button
          type="button"
          onClick={handleLogout}
          className="group flex size-9 items-center justify-center rounded-lg border border-white/10 text-slate-500 transition hover:border-red-400/20 hover:bg-red-400/[0.05] hover:text-red-300"
          aria-label="Sign out"
          title="Sign out"
        >
          <LogOut className="size-4 transition-transform group-hover:-translate-x-0.5" />
        </button>
      </div>
    </header>
  );
}