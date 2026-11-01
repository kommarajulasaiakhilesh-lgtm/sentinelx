"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { AnimatePresence, motion } from "motion/react";
import {
  Activity,
  AlertTriangle,
  BarChart3,
  Bot,
  CornerDownLeft,
  FileCheck2,
  FlaskConical,
  Gauge,
  LayoutDashboard,
  ListFilter,
  ScrollText,
  Search,
  Settings,
  Shield,
  ShieldCheck,
  Siren,
  SlidersHorizontal,
  Wrench,
} from "lucide-react";

import { useMyAgents } from "@/features/agents/use-agents";

type Command = {
  id: string;
  label: string;
  hint?: string;
  icon: typeof Bot;
  href: string;
  keywords?: string;
};

const PAGES: Command[] = [
  { id: "home", label: "Command Center", icon: LayoutDashboard, href: "/" },
  { id: "agents", label: "Agents", icon: Bot, href: "/agents" },
  { id: "posture", label: "Agent Posture", icon: Gauge, href: "/posture" },
  { id: "policies", label: "Policies", icon: Shield, href: "/policies" },
  { id: "tools", label: "Tools & Actions", icon: Wrench, href: "/tools" },
  { id: "guardrails", label: "Runtime Guardrails", icon: ShieldCheck, href: "/guardrails" },
  { id: "tests", label: "Security Testing", icon: FlaskConical, href: "/security-tests" },
  { id: "events", label: "Security Events", icon: Activity, href: "/events" },
  { id: "rules", label: "Detection Rules", icon: ListFilter, href: "/detection-rules" },
  { id: "alerts", label: "Alerts & Incidents", icon: AlertTriangle, href: "/alerts" },
  { id: "incidents", label: "Incident Response", icon: Siren, href: "/incidents" },
  { id: "analytics", label: "Analytics", icon: BarChart3, href: "/analytics" },
  { id: "compliance", label: "Compliance", icon: FileCheck2, href: "/compliance" },
  { id: "risk", label: "Risk Configurations", icon: SlidersHorizontal, href: "/risk-configurations" },
  { id: "audit", label: "Audit Log", icon: ScrollText, href: "/audit" },
  { id: "settings", label: "Account & Security", icon: Settings, href: "/settings" },
];

export function CommandPalette() {
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [active, setActive] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  const { data: agents = [] } = useMyAgents();

  useEffect(() => {
    const openPalette = () => {
      setQuery("");
      setActive(0);
      setOpen(true);
    };
    const onKey = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setOpen((v) => {
          if (!v) {
            setQuery("");
            setActive(0);
          }
          return !v;
        });
      }
      if (e.key === "Escape") setOpen(false);
    };
    window.addEventListener("keydown", onKey);
    window.addEventListener("sentinelx:open-command", openPalette);
    return () => {
      window.removeEventListener("keydown", onKey);
      window.removeEventListener("sentinelx:open-command", openPalette);
    };
  }, []);

  useEffect(() => {
    if (open) {
      const t = setTimeout(() => inputRef.current?.focus(), 20);
      return () => clearTimeout(t);
    }
  }, [open]);

  const commands = useMemo<Command[]>(() => {
    const agentCommands: Command[] = agents.map((a) => ({
      id: `agent-${a.id}`,
      label: a.name,
      hint: "Agent",
      icon: Bot,
      href: `/agents/${a.id}`,
      keywords: a.status,
    }));
    return [...PAGES, ...agentCommands];
  }, [agents]);

  const results = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return commands;
    return commands.filter(
      (c) =>
        c.label.toLowerCase().includes(q) ||
        c.hint?.toLowerCase().includes(q) ||
        c.keywords?.toLowerCase().includes(q),
    );
  }, [query, commands]);

  const go = (href: string) => {
    setOpen(false);
    router.push(href);
  };

  const onKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setActive((i) => Math.min(i + 1, results.length - 1));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setActive((i) => Math.max(i - 1, 0));
    } else if (e.key === "Enter" && results[active]) {
      e.preventDefault();
      go(results[active].href);
    }
  };

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          className="fixed inset-0 z-[90] flex items-start justify-center px-4 pt-[12vh]"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.15 }}
        >
          <div
            className="absolute inset-0 bg-slate-900/30 backdrop-blur-sm"
            onClick={() => setOpen(false)}
            aria-hidden
          />
          <motion.div
            initial={{ opacity: 0, y: -12, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -12, scale: 0.98 }}
            transition={{ duration: 0.18, ease: [0.22, 1, 0.36, 1] }}
            className="relative w-full max-w-xl overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-2xl shadow-slate-900/20"
          >
            <div className="flex items-center gap-3 border-b border-slate-100 px-4">
              <Search className="size-4 text-slate-400" />
              <input
                ref={inputRef}
                value={query}
                onChange={(e) => {
                  setQuery(e.target.value);
                  setActive(0);
                }}
                onKeyDown={onKeyDown}
                placeholder="Search pages and agents…"
                className="h-12 w-full bg-transparent text-sm text-slate-900 outline-none placeholder:text-slate-400"
              />
              <kbd className="hidden rounded border border-slate-200 bg-slate-50 px-1.5 py-0.5 text-[10px] font-medium text-slate-400 sm:block">
                ESC
              </kbd>
            </div>

            <div className="max-h-80 overflow-y-auto p-2">
              {results.length === 0 ? (
                <div className="px-3 py-8 text-center text-sm text-slate-400">
                  No matches.
                </div>
              ) : (
                results.map((c, i) => {
                  const Icon = c.icon;
                  return (
                    <button
                      key={c.id}
                      type="button"
                      onMouseEnter={() => setActive(i)}
                      onClick={() => go(c.href)}
                      className={`flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-left text-sm transition-colors ${
                        i === active
                          ? "bg-indigo-50 text-indigo-700"
                          : "text-slate-700 hover:bg-slate-50"
                      }`}
                    >
                      <Icon
                        className={`size-4 shrink-0 ${
                          i === active ? "text-indigo-600" : "text-slate-400"
                        }`}
                      />
                      <span className="flex-1 truncate">{c.label}</span>
                      {c.hint && (
                        <span className="rounded border border-slate-200 bg-slate-50 px-1.5 py-0.5 text-[10px] text-slate-400">
                          {c.hint}
                        </span>
                      )}
                      {i === active && (
                        <CornerDownLeft className="size-3.5 text-indigo-400" />
                      )}
                    </button>
                  );
                })
              )}
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
