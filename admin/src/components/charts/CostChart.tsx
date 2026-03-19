"use client";

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

interface DailyCost {
  day: string;
  total_cost: number;
  event_count: number;
}

export function CostChart({ data }: { data?: DailyCost[] }) {
  const hasData = data && data.length > 0;

  return (
    <div
      className="rounded-lg p-5 border"
      style={{
        background: "var(--color-bg-card)",
        borderColor: "var(--color-border)",
      }}
    >
      <p
        className="text-sm font-medium mb-4"
        style={{ color: "var(--color-text)" }}
      >
        Daily Cost (30 days)
      </p>
      {hasData ? (
        <ResponsiveContainer width="100%" height={240}>
          <AreaChart data={data}>
            <defs>
              <linearGradient id="costGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#ff6b4a" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#ff6b4a" stopOpacity={0} />
              </linearGradient>
            </defs>
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
              tickFormatter={(v: number) => `$${v.toFixed(2)}`}
              tick={{ fill: "rgba(255,255,255,0.4)", fontSize: 11 }}
              axisLine={false}
              tickLine={false}
              width={60}
            />
            <Tooltip
              contentStyle={{
                background: "#1a1a2e",
                border: "1px solid rgba(255,255,255,0.1)",
                borderRadius: 8,
                color: "#fff",
                fontSize: 12,
              }}
              formatter={(value: number) => [
                `$${value.toFixed(4)}`,
                "Cost",
              ]}
              labelFormatter={(label: string) => {
                const d = new Date(label);
                return d.toLocaleDateString("en-US", {
                  month: "long",
                  day: "numeric",
                  year: "numeric",
                });
              }}
            />
            <Area
              type="monotone"
              dataKey="total_cost"
              stroke="#ff6b4a"
              strokeWidth={2}
              fill="url(#costGradient)"
            />
          </AreaChart>
        </ResponsiveContainer>
      ) : (
        <div
          className="flex items-center justify-center"
          style={{ height: 240, color: "var(--color-text-muted)" }}
        >
          <p className="text-sm">
            Cost chart will render here once usage data accumulates.
          </p>
        </div>
      )}
    </div>
  );
}
