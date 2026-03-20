"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import {
  changePlanTier,
  changeSubscriptionStatus,
  resetPostLimits,
  adjustVideoCredits,
  setHardCostLimit,
} from "../actions";

interface Tenant {
  id: string;
  plan_tier: string;
  subscription_status: string;
  video_credits_remaining: number | null;
  monthly_cost_hard_limit_usd: number | null;
}

export function TenantActions({ tenant }: { tenant: Tenant }) {
  const router = useRouter();
  const [feedback, setFeedback] = useState<{ type: "success" | "error"; msg: string } | null>(null);

  const showFeedback = (type: "success" | "error", msg: string) => {
    setFeedback({ type, msg });
    setTimeout(() => setFeedback(null), 3000);
    if (type === "success") router.refresh();
  };

  return (
    <div
      className="rounded-lg border p-5 flex flex-col gap-5"
      style={{
        background: "var(--color-bg-card)",
        borderColor: "var(--color-border)",
      }}
    >
      <div className="flex items-center justify-between">
        <p
          className="text-sm font-medium"
          style={{ color: "var(--color-text)" }}
        >
          Admin Actions
        </p>
        {feedback && (
          <span
            className="text-xs px-2 py-1 rounded"
            style={{
              color:
                feedback.type === "success"
                  ? "var(--color-success)"
                  : "var(--color-danger)",
              background:
                feedback.type === "success"
                  ? "rgba(52,199,89,0.15)"
                  : "rgba(255,59,48,0.15)",
            }}
          >
            {feedback.msg}
          </span>
        )}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {/* Change Plan — key forces remount after server refresh */}
        <ActionCard
          key={`plan-${tenant.plan_tier}`}
          label="Change Plan"
          renderInput={(value, setValue) => (
            <select
              value={value}
              onChange={(e) => setValue(e.target.value)}
              className="w-full px-3 py-2 rounded-lg text-sm border outline-none"
              style={{
                background: "var(--color-bg)",
                borderColor: "var(--color-border)",
                color: "var(--color-text)",
              }}
            >
              {["free_trial", "starter", "growth", "pro"].map((t) => (
                <option key={t} value={t}>
                  {t.replace("_", " ")}
                </option>
              ))}
            </select>
          )}
          defaultValue={tenant.plan_tier}
          onApply={async (v) => {
            const res = await changePlanTier(tenant.id, v);
            showFeedback(
              res.error ? "error" : "success",
              res.error || `Plan changed to ${v}`
            );
          }}
        />

        {/* Subscription Status */}
        <ActionCard
          key={`status-${tenant.subscription_status}`}
          label="Subscription Status"
          renderInput={(value, setValue) => (
            <select
              value={value}
              onChange={(e) => setValue(e.target.value)}
              className="w-full px-3 py-2 rounded-lg text-sm border outline-none"
              style={{
                background: "var(--color-bg)",
                borderColor: "var(--color-border)",
                color: "var(--color-text)",
              }}
            >
              {["free_trial", "active", "past_due", "paused", "canceled"].map(
                (s) => (
                  <option key={s} value={s}>
                    {s.replace("_", " ")}
                  </option>
                )
              )}
            </select>
          )}
          defaultValue={tenant.subscription_status}
          onApply={async (v) => {
            const res = await changeSubscriptionStatus(tenant.id, v);
            showFeedback(
              res.error ? "error" : "success",
              res.error || `Status changed to ${v}`
            );
          }}
        />

        {/* Video Credits */}
        <ActionCard
          key={`credits-${tenant.video_credits_remaining}`}
          label="Video Credits"
          renderInput={(value, setValue) => (
            <input
              type="number"
              min={0}
              value={value}
              onChange={(e) => setValue(e.target.value)}
              className="w-full px-3 py-2 rounded-lg text-sm border outline-none"
              style={{
                background: "var(--color-bg)",
                borderColor: "var(--color-border)",
                color: "var(--color-text)",
              }}
            />
          )}
          defaultValue={String(tenant.video_credits_remaining || 0)}
          onApply={async (v) => {
            const parsed = parseInt(v, 10);
            if (isNaN(parsed)) return showFeedback("error", "Enter a valid number");
            const res = await adjustVideoCredits(tenant.id, parsed);
            showFeedback(
              res.error ? "error" : "success",
              res.error || `Credits set to ${v}`
            );
          }}
        />

        {/* Cost Hard Limit */}
        <ActionCard
          key={`limit-${tenant.monthly_cost_hard_limit_usd}`}
          label="Monthly Cost Limit ($)"
          renderInput={(value, setValue) => (
            <input
              type="number"
              min={0}
              step={0.5}
              value={value}
              onChange={(e) => setValue(e.target.value)}
              className="w-full px-3 py-2 rounded-lg text-sm border outline-none"
              style={{
                background: "var(--color-bg)",
                borderColor: "var(--color-border)",
                color: "var(--color-text)",
              }}
            />
          )}
          defaultValue={String(tenant.monthly_cost_hard_limit_usd || 2)}
          onApply={async (v) => {
            const parsed = parseFloat(v);
            if (isNaN(parsed)) return showFeedback("error", "Enter a valid number");
            const res = await setHardCostLimit(tenant.id, parsed);
            showFeedback(
              res.error ? "error" : "success",
              res.error || `Limit set to $${v}`
            );
          }}
        />

        {/* Reset Posts */}
        <div className="flex flex-col gap-2">
          <p
            className="text-xs font-medium uppercase tracking-wider"
            style={{ color: "var(--color-text-muted)" }}
          >
            Reset Post Limits
          </p>
          <button
            onClick={async () => {
              if (!confirm("Reset all post counters to 0?")) return;
              const res = await resetPostLimits(tenant.id);
              showFeedback(
                res.error ? "error" : "success",
                res.error || "Post limits reset"
              );
            }}
            className="px-4 py-2 rounded-lg text-sm font-medium cursor-pointer"
            style={{
              background: "rgba(255,59,48,0.15)",
              color: "var(--color-danger)",
            }}
          >
            Reset Counters
          </button>
        </div>
      </div>
    </div>
  );
}

function ActionCard({
  label,
  renderInput,
  defaultValue,
  onApply,
}: {
  label: string;
  renderInput: (
    value: string,
    setValue: (v: string) => void
  ) => React.ReactNode;
  defaultValue: string;
  onApply: (value: string) => Promise<void>;
}) {
  const [value, setValue] = useState(defaultValue);
  const [applying, setApplying] = useState(false);

  return (
    <div className="flex flex-col gap-2">
      <p
        className="text-xs font-medium uppercase tracking-wider"
        style={{ color: "var(--color-text-muted)" }}
      >
        {label}
      </p>
      {renderInput(value, setValue)}
      <button
        onClick={async () => {
          setApplying(true);
          await onApply(value);
          setApplying(false);
        }}
        disabled={applying || value === defaultValue}
        className="px-4 py-2 rounded-lg text-sm font-medium cursor-pointer disabled:opacity-50"
        style={{ background: "var(--color-accent)", color: "#fff" }}
      >
        {applying ? "Applying..." : "Apply"}
      </button>
    </div>
  );
}
