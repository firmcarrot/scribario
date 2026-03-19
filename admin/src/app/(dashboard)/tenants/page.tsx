import Link from "next/link";
import { createServiceClient } from "@/lib/supabase/server";

async function getTenants() {
  const db = createServiceClient();
  const { data, error } = await db
    .from("tenants")
    .select("id, name, plan_tier, subscription_status, monthly_posts_used, monthly_post_limit, video_credits_remaining, trial_posts_used, trial_posts_limit, created_at")
    .order("created_at", { ascending: false });

  if (error) {
    console.error("Failed to fetch tenants:", error);
    return [];
  }
  return data || [];
}

const STATUS_COLORS: Record<string, string> = {
  active: "var(--color-success)",
  free_trial: "var(--color-warning)",
  past_due: "var(--color-danger)",
  canceled: "var(--color-text-muted)",
  paused: "var(--color-text-muted)",
};

export default async function TenantsPage() {
  const tenants = await getTenants();

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-2xl font-bold">Tenants</h1>

      {tenants.length === 0 ? (
        <div className="rounded-lg p-8 border text-center" style={{ background: "var(--color-bg-card)", borderColor: "var(--color-border)", color: "var(--color-text-muted)" }}>
          No tenants registered yet.
        </div>
      ) : (
        <div className="rounded-lg border overflow-hidden" style={{ background: "var(--color-bg-card)", borderColor: "var(--color-border)" }}>
          <table className="w-full text-sm">
            <thead>
              <tr style={{ borderBottom: `1px solid var(--color-border)` }}>
                {["Name", "Plan", "Status", "Posts", "Videos", "Created", ""].map((h) => (
                  <th key={h} className="text-left px-4 py-3 text-xs font-medium uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {tenants.map((t) => {
                const postsUsed = t.plan_tier === "free_trial"
                  ? `${t.trial_posts_used || 0}/${t.trial_posts_limit || 5}`
                  : `${t.monthly_posts_used || 0}/${t.monthly_post_limit || 5}`;

                return (
                  <tr key={t.id} className="hover:opacity-80" style={{ borderBottom: `1px solid var(--color-border)` }}>
                    <td className="px-4 py-3 font-medium" style={{ color: "var(--color-text)" }}>{t.name}</td>
                    <td className="px-4 py-3" style={{ color: "var(--color-text-muted)" }}>{t.plan_tier}</td>
                    <td className="px-4 py-3">
                      <span className="inline-block px-2 py-0.5 rounded text-xs font-medium" style={{ color: STATUS_COLORS[t.subscription_status] || "var(--color-text-muted)", background: `${STATUS_COLORS[t.subscription_status] || "var(--color-text-muted)"}15` }}>
                        {t.subscription_status}
                      </span>
                    </td>
                    <td className="px-4 py-3" style={{ color: "var(--color-text-muted)" }}>{postsUsed}</td>
                    <td className="px-4 py-3" style={{ color: "var(--color-text-muted)" }}>{t.video_credits_remaining ?? 0}</td>
                    <td className="px-4 py-3" style={{ color: "var(--color-text-muted)" }}>
                      {new Date(t.created_at).toLocaleDateString("en-US", { month: "short", day: "numeric" })}
                    </td>
                    <td className="px-4 py-3">
                      <Link href={`/tenants/${t.id}`} className="text-xs font-medium hover:underline" style={{ color: "var(--color-accent)" }}>
                        View
                      </Link>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
