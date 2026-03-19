import { createServiceClient } from "@/lib/supabase/server";
import { notFound } from "next/navigation";
import Link from "next/link";

async function getTenant(id: string) {
  const db = createServiceClient();

  const [tenantResult, usageResult, requestsResult] = await Promise.all([
    db.from("tenants")
      .select("*")
      .eq("id", id)
      .single(),
    db.from("usage_events")
      .select("event_type, provider, cost_usd, created_at")
      .eq("tenant_id", id)
      .order("created_at", { ascending: false })
      .limit(50),
    db.from("content_requests")
      .select("id, intent, status, created_at")
      .eq("tenant_id", id)
      .order("created_at", { ascending: false })
      .limit(20),
  ]);

  if (tenantResult.error || !tenantResult.data) return null;

  return {
    tenant: tenantResult.data,
    usage: usageResult.data || [],
    requests: requestsResult.data || [],
  };
}

export default async function TenantDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const data = await getTenant(id);
  if (!data) notFound();

  const { tenant, usage, requests } = data;
  const totalCost = usage.reduce((sum, e) => sum + Number(e.cost_usd || 0), 0);

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center gap-3">
        <Link href="/tenants" className="text-sm hover:underline" style={{ color: "var(--color-accent)" }}>
          ← Tenants
        </Link>
      </div>

      <h1 className="text-2xl font-bold">{tenant.name}</h1>

      {/* Info cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: "Plan", value: tenant.plan_tier },
          { label: "Status", value: tenant.subscription_status },
          { label: "Posts Used", value: tenant.plan_tier === "free_trial" ? `${tenant.trial_posts_used || 0}/${tenant.trial_posts_limit || 5}` : `${tenant.monthly_posts_used || 0}/${tenant.monthly_post_limit || 5}` },
          { label: "Total Cost", value: `$${totalCost.toFixed(2)}` },
        ].map((card) => (
          <div
            key={card.label}
            className="rounded-lg p-4 border"
            style={{ background: "var(--color-bg-card)", borderColor: "var(--color-border)" }}
          >
            <p className="text-xs font-medium uppercase tracking-wider mb-1" style={{ color: "var(--color-text-muted)" }}>{card.label}</p>
            <p className="text-lg font-bold" style={{ color: "var(--color-text)" }}>{card.value}</p>
          </div>
        ))}
      </div>

      {/* Recent content requests */}
      <div className="rounded-lg border overflow-hidden" style={{ background: "var(--color-bg-card)", borderColor: "var(--color-border)" }}>
        <div className="p-4 border-b" style={{ borderColor: "var(--color-border)" }}>
          <p className="text-sm font-medium" style={{ color: "var(--color-text)" }}>Recent Content Requests</p>
        </div>
        {requests.length === 0 ? (
          <div className="p-4 text-center text-sm" style={{ color: "var(--color-text-muted)" }}>No requests yet.</div>
        ) : (
          <table className="w-full text-sm">
            <tbody>
              {requests.map((r) => (
                <tr key={r.id} style={{ borderBottom: `1px solid var(--color-border)` }}>
                  <td className="px-4 py-3" style={{ color: "var(--color-text)" }}>
                    {(r.intent || "").slice(0, 60)}{(r.intent || "").length > 60 ? "..." : ""}
                  </td>
                  <td className="px-4 py-3" style={{ color: "var(--color-text-muted)" }}>{r.status}</td>
                  <td className="px-4 py-3" style={{ color: "var(--color-text-muted)" }}>
                    {new Date(r.created_at).toLocaleDateString("en-US", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" })}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Recent usage events */}
      <div className="rounded-lg border overflow-hidden" style={{ background: "var(--color-bg-card)", borderColor: "var(--color-border)" }}>
        <div className="p-4 border-b" style={{ borderColor: "var(--color-border)" }}>
          <p className="text-sm font-medium" style={{ color: "var(--color-text)" }}>Usage Events (recent 50)</p>
        </div>
        {usage.length === 0 ? (
          <div className="p-4 text-center text-sm" style={{ color: "var(--color-text-muted)" }}>No usage events yet.</div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr style={{ borderBottom: `1px solid var(--color-border)` }}>
                {["Type", "Provider", "Cost", "Date"].map((h) => (
                  <th key={h} className="text-left px-4 py-2 text-xs font-medium uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {usage.map((e, i) => (
                <tr key={i} style={{ borderBottom: `1px solid var(--color-border)` }}>
                  <td className="px-4 py-2" style={{ color: "var(--color-text)" }}>{e.event_type}</td>
                  <td className="px-4 py-2" style={{ color: "var(--color-text-muted)" }}>{e.provider}</td>
                  <td className="px-4 py-2" style={{ color: "var(--color-text)" }}>${Number(e.cost_usd).toFixed(4)}</td>
                  <td className="px-4 py-2" style={{ color: "var(--color-text-muted)" }}>
                    {new Date(e.created_at).toLocaleDateString("en-US", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" })}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
