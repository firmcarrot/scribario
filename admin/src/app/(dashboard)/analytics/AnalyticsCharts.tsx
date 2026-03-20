"use client";

import { useState, useMemo } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";

interface DailyAnalytics {
  day: string;
  requests: number;
  approvals: number;
  rejections: number;
  regenerations: number;
  distinct_tenants: number;
}

const RANGES = [
  { label: "7d", days: 7 },
  { label: "14d", days: 14 },
  { label: "30d", days: 30 },
] as const;

export function AnalyticsCharts({ data }: { data: DailyAnalytics[] }) {
  const [range, setRange] = useState<number>(30);

  const filtered = useMemo(() => {
    if (!data || data.length === 0) return [];
    return data.slice(-range);
  }, [data, range]);

  if (!data || data.length === 0) {
    return (
      <div
        className="rounded-lg p-8 border text-center"
        style={{
          background: "var(--color-bg-card)",
          borderColor: "var(--color-border)",
          color: "var(--color-text-muted)",
        }}
      >
        <p className="text-sm">No analytics data yet. Charts will appear once content is generated.</p>
      </div>
    );
  }

  return (
    <div
      className="rounded-lg border p-5"
      style={{
        background: "var(--color-bg-card)",
        borderColor: "var(--color-border)",
      }}
    >
      <div className="flex items-center justify-between mb-4">
        <p
          className="text-sm font-medium"
          style={{ color: "var(--color-text)" }}
        >
          Activity Over Time
        </p>
        <div className="flex gap-1">
          {RANGES.map((r) => (
            <button
              key={r.label}
              onClick={() => setRange(r.days)}
              className="px-3 py-1 rounded text-xs font-medium cursor-pointer transition-colors"
              style={{
                background:
                  range === r.days
                    ? "var(--color-accent)"
                    : "transparent",
                color:
                  range === r.days
                    ? "#fff"
                    : "var(--color-text-muted)",
                border:
                  range === r.days
                    ? "none"
                    : "1px solid var(--color-border)",
              }}
            >
              {r.label}
            </button>
          ))}
        </div>
      </div>

      <ResponsiveContainer width="100%" height={280}>
        <LineChart data={filtered}>
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="rgba(255,255,255,0.06)"
          />
          <XAxis
            dataKey="day"
            tickFormatter={(v: string) => {
              const d = new Date(v);
              return d.toLocaleDateString("en-US", {
                month: "short",
                day: "numeric",
              });
            }}
            tick={{ fill: "rgba(255,255,255,0.4)", fontSize: 11 }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            tick={{ fill: "rgba(255,255,255,0.4)", fontSize: 11 }}
            axisLine={false}
            tickLine={false}
            allowDecimals={false}
          />
          <Tooltip
            contentStyle={{
              background: "#1a1a2e",
              border: "1px solid rgba(255,255,255,0.1)",
              borderRadius: 8,
              color: "#fff",
              fontSize: 12,
            }}
            labelFormatter={(label: string) => {
              const d = new Date(label);
              return d.toLocaleDateString("en-US", {
                month: "long",
                day: "numeric",
              });
            }}
          />
          <Legend
            wrapperStyle={{ fontSize: 11, color: "rgba(255,255,255,0.6)" }}
          />
          <Line
            type="monotone"
            dataKey="requests"
            stroke="#ff6b4a"
            strokeWidth={2}
            dot={false}
            name="Requests"
          />
          <Line
            type="monotone"
            dataKey="approvals"
            stroke="#34c759"
            strokeWidth={2}
            dot={false}
            name="Approvals"
          />
          <Line
            type="monotone"
            dataKey="rejections"
            stroke="#ff3b30"
            strokeWidth={1.5}
            dot={false}
            name="Rejections"
          />
          <Line
            type="monotone"
            dataKey="distinct_tenants"
            stroke="#0088cc"
            strokeWidth={1.5}
            dot={false}
            name="Active Tenants"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
