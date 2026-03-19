"use client";

interface Tenant {
  id: string;
  name: string;
  plan_tier: string;
  subscription_status: string;
  monthly_posts_used: number | null;
  monthly_post_limit: number | null;
  video_credits_remaining: number | null;
}

interface Props {
  tenants: Tenant[];
  planPrices: Record<string, number>;
}

export function TenantEconomicsTable({ tenants, planPrices }: Props) {
  if (tenants.length === 0) {
    return (
      <div
        className="rounded-lg p-5 border text-center"
        style={{ background: "var(--color-bg-card)", borderColor: "var(--color-border)", color: "var(--color-text-muted)" }}
      >
        No tenants yet.
      </div>
    );
  }

  return (
    <div
      className="rounded-lg border overflow-hidden"
      style={{ background: "var(--color-bg-card)", borderColor: "var(--color-border)" }}
    >
      <div className="p-4 border-b" style={{ borderColor: "var(--color-border)" }}>
        <p className="text-sm font-medium" style={{ color: "var(--color-text)" }}>
          Per-Tenant Economics
        </p>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr style={{ borderBottom: `1px solid var(--color-border)` }}>
              {["Tenant", "Plan", "Status", "Posts Used", "Videos", "Revenue"].map((h) => (
                <th
                  key={h}
                  className="text-left px-4 py-3 text-xs font-medium uppercase tracking-wider"
                  style={{ color: "var(--color-text-muted)" }}
                >
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {tenants.map((t) => {
              const revenue = planPrices[t.plan_tier] || 0;
              const statusColor =
                t.subscription_status === "active"
                  ? "var(--color-success)"
                  : t.subscription_status === "free_trial"
                  ? "var(--color-warning)"
                  : "var(--color-danger)";

              return (
                <tr
                  key={t.id}
                  className="hover:opacity-80"
                  style={{ borderBottom: `1px solid var(--color-border)` }}
                >
                  <td className="px-4 py-3 font-medium" style={{ color: "var(--color-text)" }}>
                    {t.name}
                  </td>
                  <td className="px-4 py-3" style={{ color: "var(--color-text-muted)" }}>
                    {t.plan_tier}
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className="inline-block px-2 py-0.5 rounded text-xs font-medium"
                      style={{ color: statusColor, background: `${statusColor}15` }}
                    >
                      {t.subscription_status}
                    </span>
                  </td>
                  <td className="px-4 py-3" style={{ color: "var(--color-text-muted)" }}>
                    {t.monthly_posts_used ?? 0}/{t.monthly_post_limit ?? 5}
                  </td>
                  <td className="px-4 py-3" style={{ color: "var(--color-text-muted)" }}>
                    {t.video_credits_remaining ?? 0}
                  </td>
                  <td className="px-4 py-3" style={{ color: "var(--color-text)" }}>
                    {revenue > 0 ? `$${revenue}/mo` : "Free"}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
