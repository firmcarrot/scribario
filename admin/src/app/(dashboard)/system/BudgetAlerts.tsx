"use client";

import { AlertTriangle, DollarSign } from "lucide-react";

interface BudgetAlert {
  tenant_id: string;
  tenant_name: string;
  plan_tier: string;
  spend: number;
  hard_limit: number;
  pct_used: number;
}

export function BudgetAlerts({ alerts }: { alerts: BudgetAlert[] }) {
  if (!alerts || alerts.length === 0) return null;

  return (
    <div
      className="rounded-lg border overflow-hidden"
      style={{
        background: "var(--color-bg-card)",
        borderColor: "var(--color-border)",
      }}
    >
      <div
        className="px-5 py-4 border-b flex items-center gap-2"
        style={{ borderColor: "var(--color-border)" }}
      >
        <DollarSign size={16} style={{ color: "var(--color-warning)" }} />
        <h2
          className="text-sm font-semibold"
          style={{ color: "var(--color-text)" }}
        >
          Budget Alerts ({alerts.length})
        </h2>
      </div>
      <div className="divide-y" style={{ borderColor: "var(--color-border)" }}>
        {alerts.map((a) => {
          const isCritical = a.pct_used >= 95;
          const color = isCritical
            ? "var(--color-danger)"
            : "var(--color-warning)";

          return (
            <div
              key={a.tenant_id}
              className="px-5 py-3 flex items-center justify-between"
              style={{
                borderBottom: "1px solid var(--color-border)",
              }}
            >
              <div className="flex items-center gap-3">
                <AlertTriangle size={14} style={{ color }} />
                <div>
                  <p
                    className="text-sm font-medium"
                    style={{ color: "var(--color-text)" }}
                  >
                    {a.tenant_name}
                  </p>
                  <p
                    className="text-xs"
                    style={{ color: "var(--color-text-muted)" }}
                  >
                    {a.plan_tier} &middot; ${Number(a.spend).toFixed(2)} / $
                    {Number(a.hard_limit).toFixed(2)}
                  </p>
                </div>
              </div>
              <span
                className="text-sm font-bold"
                style={{ color }}
              >
                {Number(a.pct_used).toFixed(0)}%
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
