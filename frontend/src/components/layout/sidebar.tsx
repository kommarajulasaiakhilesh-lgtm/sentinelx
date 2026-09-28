"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Activity,
  AlertTriangle,
  BarChart3,
  Bot,
  CircleDot,
  Gauge,
  LayoutDashboard,
  Shield,
  ShieldCheck,
  Terminal,
  Wrench,
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
    label: "Analytics",
    href: "/analytics",
    icon: BarChart3,
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
    <aside className="fixed inset-y-0 left-0 z-40 hidden w-72 border-r border-white/10 bg-[#090b10] lg:flex lg:flex-col">
      <div className="flex h-20 items-center border-b border-white/10 px-6">
        <Link href="/" className="flex items-center gap-3">
          <div className="flex size-10 items-center justify-center rounded-xl border border-cyan-400/30 bg-cyan-400/10">
            <ShieldCheck className="size-5 text-cyan-300" />
          </div>

          <div>
            <div className="text-sm font-semibold tracking-[0.22em] text-white">
              SENTINELX
            </div>
            <div className="mt-0.5 text-[10px] uppercase tracking-[0.18em] text-slate-500">
              Agent Security Control Plane
            </div>
          </div>
        </Link>
      </div>

      <div className="flex-1 overflow-y-auto px-4 py-6">
        <NavigationSection
          title="Control Plane"
          items={primaryNavigation}
          isActive={isActive}
        />

        <NavigationSection
          title="Security"
          items={securityNavigation}
          isActive={isActive}
        />
      </div>

      <div className="border-t border-white/10 p-4">
        <div className="rounded-xl border border-emerald-400/15 bg-emerald-400/5 p-3">
          <div className="flex items-center gap-2">
            <CircleDot className="size-3 fill-emerald-400 text-emerald-400" />
            <span className="text-xs font-medium text-emerald-300">
              Control plane operational
            </span>
          </div>

          <div className="mt-2 flex items-center gap-2 text-[11px] text-slate-500">
            <Gauge className="size-3.5" />
            <span>Security services online</span>
          </div>
        </div>

        <div className="mt-3 flex items-center gap-2 px-1 text-[10px] uppercase tracking-[0.16em] text-slate-600">
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
    <div className="mb-7">
      <div className="mb-2 px-3 text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-600">
        {title}
      </div>

      <nav className="space-y-1">
        {items.map((item) => {
          const Icon = item.icon;
          const active = isActive(item.href);

          return (
            <Link
              key={item.href}
              href={item.href}
              className={`group flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition ${
                active
                  ? "border border-cyan-400/15 bg-cyan-400/10 text-cyan-200"
                  : "border border-transparent text-slate-400 hover:bg-white/[0.04] hover:text-slate-200"
              }`}
            >
              <Icon
                className={`size-4 ${
                  active
                    ? "text-cyan-300"
                    : "text-slate-500 group-hover:text-slate-300"
                }`}
              />

              <span>{item.label}</span>

              {active && (
                <span className="ml-auto size-1.5 rounded-full bg-cyan-300 shadow-[0_0_8px_rgba(103,232,249,0.8)]" />
              )}
            </Link>
          );
        })}
      </nav>
    </div>
  );
}