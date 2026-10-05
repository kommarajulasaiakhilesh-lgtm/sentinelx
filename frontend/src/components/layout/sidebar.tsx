"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Activity,
  AlertTriangle,
  BarChart3,
  Bot,
  CircleDot,
  FileCheck2,
  FlaskConical,
  Gauge,
  LayoutDashboard,
  Shield,
  ShieldCheck,
  Terminal,
  Wrench,
  Siren,
} from "lucide-react";

const primaryNavigation = [
  {
    label: "Command Center",
    href: "/",
    icon: LayoutDashboard,
  },
  {
    label: "Agents",
    href: "/agents",
    icon: Bot,
  },
  {
    label: "Policies",
    href: "/policies",
    icon: Shield,
  },
  {
    label: "Tools & Actions",
    href: "/tools",
    icon: Wrench,
  },
  {
    label: "Runtime Guardrails",
    href: "/guardrails",
    icon: ShieldCheck,
  },
];

const securityNavigation = [
  {
    label: "Security Testing",
    href: "/security-tests",
    icon: FlaskConical,
  },
  {
    label: "Security Events",
    href: "/events",
    icon: Activity,
  },
  {
    label: "Alerts & Incidents",
    href: "/alerts",
    icon: AlertTriangle,
  },
    {
    label: "Incident Response",
    href: "/incidents",
    icon: Siren,
  },
  {
    label: "Analytics",
    href: "/analytics",
    icon: BarChart3,
  },
  {
    label: "Compliance",
    href: "/compliance",
    icon: FileCheck2,
  },
  
];

export function Sidebar() {
  const pathname = usePathname();

  const isActive = (href: string) => {
    if (href === "/") {
      return pathname === "/";
    }

    return pathname === href || pathname.startsWith(`${href}/`);
  };

  return (
    <aside className="fixed inset-y-0 left-0 z-40 hidden w-72 border-r border-white/[0.07] bg-[#070a0f] lg:flex lg:flex-col">
      <div className="relative flex h-[76px] shrink-0 items-center border-b border-white/[0.07] px-5">
        <div className="pointer-events-none absolute inset-x-0 bottom-0 h-px bg-gradient-to-r from-transparent via-cyan-400/20 to-transparent" />

        <Link
          href="/"
          className="group flex items-center gap-3 rounded-lg outline-none"
        >
          <div className="relative flex size-10 items-center justify-center rounded-xl border border-cyan-400/25 bg-cyan-400/[0.07] transition-all duration-200 group-hover:border-cyan-300/40 group-hover:bg-cyan-400/10">
            <div className="absolute inset-1 rounded-lg border border-cyan-300/10" />
            <ShieldCheck className="relative size-[18px] text-cyan-300" />
          </div>

          <div className="min-w-0">
            <div className="text-[13px] font-semibold tracking-[0.24em] text-slate-100">
              SENTINELX
            </div>

            <div className="mt-1 truncate text-[9px] font-medium uppercase tracking-[0.16em] text-slate-500">
              Agent Security Control Plane
            </div>
          </div>
        </Link>
      </div>

      <div className="flex-1 overflow-y-auto px-3 py-5">
        <NavigationSection
          title="Control Plane"
          items={primaryNavigation}
          isActive={isActive}
        />

        <NavigationSection
          title="Security Operations"
          items={securityNavigation}
          isActive={isActive}
        />
      </div>

      <div className="shrink-0 border-t border-white/[0.07] p-3">
        <div className="rounded-xl border border-emerald-400/10 bg-emerald-400/[0.025] p-3">
          <div className="flex items-center gap-2.5">
            <span className="relative flex size-2">
              <span className="absolute inline-flex size-full animate-ping rounded-full bg-emerald-400/30" />
              <CircleDot className="relative size-2 text-emerald-400" />
            </span>

            <span className="text-[11px] font-medium text-emerald-300">
              Control plane operational
            </span>
          </div>

          <div className="mt-2.5 flex items-center gap-2 text-[10px] text-slate-600">
            <Gauge className="size-3.5" />
            <span>Security services online</span>
          </div>
        </div>

        <div className="mt-3 flex items-center gap-2 px-1 text-[9px] uppercase tracking-[0.18em] text-slate-700">
          <Terminal className="size-3" />
          <span>SentinelX v0.1.0</span>
        </div>
      </div>
    </aside>
  );
}

type NavigationItem = {
  label: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
};

function NavigationSection({
  title,
  items,
  isActive,
}: {
  title: string;
  items: NavigationItem[];
  isActive: (href: string) => boolean;
}) {
  return (
    <div className="mb-6">
      <div className="mb-2 px-3 text-[9px] font-semibold uppercase tracking-[0.2em] text-slate-600">
        {title}
      </div>

      <nav className="space-y-0.5">
        {items.map((item) => {
          const Icon = item.icon;
          const active = isActive(item.href);

          return (
            <Link
              key={item.href}
              href={item.href}
              aria-current={active ? "page" : undefined}
              className={`group relative flex items-center gap-3 overflow-hidden rounded-lg border px-3 py-2.5 text-[13px] font-medium transition-all duration-200 ${
                active
                  ? "border-cyan-400/15 bg-cyan-400/[0.075] text-cyan-100"
                  : "border-transparent text-slate-500 hover:border-white/[0.04] hover:bg-white/[0.025] hover:text-slate-200"
              }`}
            >
              {active && (
                <span className="absolute inset-y-1.5 left-0 w-0.5 rounded-r-full bg-cyan-300 shadow-[0_0_10px_rgba(103,232,249,0.7)]" />
              )}

              <Icon
                className={`size-[17px] shrink-0 transition-colors duration-200 ${
                  active
                    ? "text-cyan-300"
                    : "text-slate-600 group-hover:text-slate-300"
                }`}
              />

              <span className="truncate">{item.label}</span>

              {active && (
                <span className="ml-auto flex items-center">
                  <span className="size-1.5 rounded-full bg-cyan-300 shadow-[0_0_8px_rgba(103,232,249,0.8)]" />
                </span>
              )}
            </Link>
          );
        })}
      </nav>
    </div>
  );
}