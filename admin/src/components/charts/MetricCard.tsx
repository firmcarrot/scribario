import { TrendingUp, TrendingDown } from "lucide-react";

interface MetricCardProps {
  title: string;
  value: string;
  change?: number;
  trend?: "up" | "down";
}

export default function MetricCard({
  title,
  value,
  change,
  trend,
}: MetricCardProps) {
  return (
    <div
      className="rounded-lg p-5 border"
      style={{
        background: "var(--color-bg-card)",
        borderColor: "var(--color-border)",
      }}
    >
      <p
        className="text-xs font-medium uppercase tracking-wider mb-2"
        style={{ color: "var(--color-text-muted)" }}
      >
        {title}
      </p>
      <p className="text-2xl font-bold" style={{ color: "var(--color-text)" }}>
        {value}
      </p>
      {change !== undefined && trend && (
        <div className="flex items-center gap-1 mt-2 text-xs font-medium">
          {trend === "up" ? (
            <TrendingUp
              size={14}
              style={{ color: "var(--color-success)" }}
            />
          ) : (
            <TrendingDown
              size={14}
              style={{ color: "var(--color-danger)" }}
            />
          )}
          <span
            style={{
              color:
                trend === "up"
                  ? "var(--color-success)"
                  : "var(--color-danger)",
            }}
          >
            {change > 0 ? "+" : ""}
            {change}%
          </span>
        </div>
      )}
    </div>
  );
}
