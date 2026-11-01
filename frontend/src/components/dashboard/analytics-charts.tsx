"use client";

import { useMemo } from "react";
import { motion } from "motion/react";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { useSecurityEvents } from "@/features/events/use-security-events";
import { useSecurityAlerts } from "@/features/alerts/use-security-alerts";

const DECISION_COLORS: Record<string, string> = {
  ALLOW: "#059669",
  BLOCK: "#dc2626",
  SUSPICIOUS: "#d97706",
};

const SEVERITY_COLORS: Record<string, string> = {
  CRITICAL: "#dc2626",
  HIGH: "#f87171",
  MEDIUM: "#d97706",
  LOW: "#94a3b8",
};

function ChartCard({
  title,
  subtitle,
  index,
  children,
}: {
  title: string;
  subtitle: string;
  index: number;
  children: React.ReactNode;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: index * 0.08, ease: [0.22, 1, 0.36, 1] }}
      className="security-surface p-5"
    >
      <div className="mb-1 text-sm font-semibold text-slate-900 dark:text-slate-100">{title}</div>
      <div className="mb-4 text-[11px] text-slate-500 dark:text-slate-400">{subtitle}</div>
      {children}
    </motion.div>
  );
}

export function AnalyticsCharts() {
  const { data: eventData } = useSecurityEvents(1, 200);
  const { data: alertData } = useSecurityAlerts(1, 100);

  const events = useMemo(() => eventData?.items ?? [], [eventData]);
  const alerts = useMemo(() => alertData?.items ?? [], [alertData]);

  const decisionData = useMemo(() => {
    const counts: Record<string, number> = {};
    for (const e of events) counts[e.decision] = (counts[e.decision] ?? 0) + 1;
    return Object.entries(counts).map(([name, value]) => ({ name, value }));
  }, [events]);

  const perDay = useMemo(() => {
    const days: { label: string; key: string; count: number }[] = [];
    for (let i = 13; i >= 0; i--) {
      const d = new Date();
      d.setDate(d.getDate() - i);
      const key = d.toISOString().slice(0, 10);
      days.push({
        key,
        label: d.toLocaleDateString(undefined, { month: "short", day: "numeric" }),
        count: 0,
      });
    }
    const idx = new Map(days.map((d, i) => [d.key, i]));
    for (const e of events) {
      const key = (e.created_at ?? "").slice(0, 10);
      const i = idx.get(key);
      if (i !== undefined) days[i].count += 1;
    }
    return days;
  }, [events]);

  const severityData = useMemo(() => {
    const order = ["CRITICAL", "HIGH", "MEDIUM", "LOW"];
    const counts: Record<string, number> = {};
    for (const a of alerts) counts[a.severity] = (counts[a.severity] ?? 0) + 1;
    return order
      .filter((s) => counts[s])
      .map((name) => ({ name, value: counts[name] }));
  }, [alerts]);

  const hasData = events.length > 0 || alerts.length > 0;
  if (!hasData) return null;

  return (
    <section className="grid gap-4 lg:grid-cols-3">
      <ChartCard
        title="Enforcement decisions"
        subtitle={`${events.length} recent events`}
        index={0}
      >
        <ResponsiveContainer width="100%" height={200}>
          <PieChart>
            <Pie
              data={decisionData}
              dataKey="value"
              nameKey="name"
              innerRadius={50}
              outerRadius={80}
              paddingAngle={2}
              strokeWidth={0}
            >
              {decisionData.map((d) => (
                <Cell key={d.name} fill={DECISION_COLORS[d.name] ?? "#94a3b8"} />
              ))}
            </Pie>
            <Tooltip contentStyle={tooltipStyle} />
          </PieChart>
        </ResponsiveContainer>
        <Legend items={decisionData} colors={DECISION_COLORS} />
      </ChartCard>

      <ChartCard
        title="Event volume"
        subtitle="Security events over the last 14 days"
        index={1}
      >
        <ResponsiveContainer width="100%" height={200}>
          <AreaChart data={perDay} margin={{ top: 6, right: 6, left: -22, bottom: 0 }}>
            <defs>
              <linearGradient id="evGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#4f46e5" stopOpacity={0.35} />
                <stop offset="100%" stopColor="#4f46e5" stopOpacity={0} />
              </linearGradient>
            </defs>
            <XAxis
              dataKey="label"
              tick={{ fontSize: 10, fill: "#94a3b8" }}
              axisLine={false}
              tickLine={false}
              interval={2}
            />
            <YAxis
              tick={{ fontSize: 10, fill: "#94a3b8" }}
              axisLine={false}
              tickLine={false}
              allowDecimals={false}
              width={34}
            />
            <Tooltip contentStyle={tooltipStyle} />
            <Area
              type="monotone"
              dataKey="count"
              stroke="#4f46e5"
              strokeWidth={2}
              fill="url(#evGrad)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </ChartCard>

      <ChartCard
        title="Alerts by severity"
        subtitle={`${alerts.length} recent alerts`}
        index={2}
      >
        {severityData.length === 0 ? (
          <div className="flex h-[200px] items-center justify-center text-xs text-slate-400 dark:text-slate-500">
            No alerts to display.
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={severityData} margin={{ top: 6, right: 6, left: -22, bottom: 0 }}>
              <XAxis
                dataKey="name"
                tick={{ fontSize: 10, fill: "#94a3b8" }}
                axisLine={false}
                tickLine={false}
              />
              <YAxis
                tick={{ fontSize: 10, fill: "#94a3b8" }}
                axisLine={false}
                tickLine={false}
                allowDecimals={false}
                width={34}
              />
              <Tooltip contentStyle={tooltipStyle} cursor={{ fill: "#f1f5f9" }} />
              <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                {severityData.map((d) => (
                  <Cell key={d.name} fill={SEVERITY_COLORS[d.name] ?? "#94a3b8"} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        )}
      </ChartCard>
    </section>
  );
}

const tooltipStyle = {
  borderRadius: 10,
  border: "1px solid #e2e8f0",
  boxShadow: "0 10px 30px -12px rgba(15,23,42,0.18)",
  fontSize: 12,
};

function Legend({
  items,
  colors,
}: {
  items: { name: string; value: number }[];
  colors: Record<string, string>;
}) {
  return (
    <div className="mt-3 flex flex-wrap justify-center gap-3">
      {items.map((d) => (
        <div key={d.name} className="flex items-center gap-1.5 text-[11px] text-slate-600 dark:text-slate-300">
          <span
            className="size-2 rounded-full"
            style={{ background: colors[d.name] ?? "#94a3b8" }}
          />
          {d.name} ({d.value})
        </div>
      ))}
    </div>
  );
}
