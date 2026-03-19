"use client";

export function CostChart() {
  return (
    <div
      className="rounded-lg p-5 border"
      style={{ background: "var(--color-bg-card)", borderColor: "var(--color-border)" }}
    >
      <p className="text-sm font-medium mb-4" style={{ color: "var(--color-text)" }}>
        Daily Cost (30 days)
      </p>
      <div
        className="flex items-center justify-center"
        style={{ height: 200, color: "var(--color-text-muted)" }}
      >
        <p className="text-sm">Cost chart will render here once usage data accumulates.</p>
      </div>
    </div>
  );
}
