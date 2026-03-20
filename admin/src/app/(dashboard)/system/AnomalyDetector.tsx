"use client";

import { Zap } from "lucide-react";

interface AnomalyData {
  detected: boolean;
  todayCost: number;
  avgCost: number;
  multiplier: number;
}

export function AnomalyDetector({ anomaly }: { anomaly: AnomalyData | null }) {
  if (!anomaly || !anomaly.detected) return null;

  return (
    <div
      className="rounded-lg border p-4 flex items-start gap-3"
      style={{
        background: "rgba(255,59,48,0.08)",
        borderColor: "var(--color-danger)",
      }}
    >
      <Zap
        size={20}
        style={{ color: "var(--color-danger)", flexShrink: 0, marginTop: 2 }}
      />
      <div>
        <p
          className="text-sm font-semibold"
          style={{ color: "var(--color-danger)" }}
        >
          Cost Anomaly Detected
        </p>
        <p
          className="text-xs mt-1"
          style={{ color: "var(--color-text-muted)" }}
        >
          Today&apos;s cost (${anomaly.todayCost.toFixed(2)}) is{" "}
          <strong style={{ color: "var(--color-danger)" }}>
            {anomaly.multiplier.toFixed(1)}x
          </strong>{" "}
          the 14-day average (${anomaly.avgCost.toFixed(2)}). This may indicate
          a runaway process or unusual usage spike.
        </p>
      </div>
    </div>
  );
}
