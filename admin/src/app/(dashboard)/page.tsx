import MetricCard from "@/components/charts/MetricCard";
import { CostChart } from "@/components/charts/CostChart";
import { TenantEconomicsTable } from "@/components/charts/TenantEconomicsTable";
import { createServiceClient } from "@/lib/supabase/server";
import { RealtimeRefresher } from "./RealtimeRefresher";

// Plan pricing for MRR calculation
const PLAN_PRICES: Record<string, number> = {
  starter: 29,
  growth: 59,
  pro: 99,
};

async function getDashboardData() {
  const db = createServiceClient();

  const monthStart = new Date();
  monthStart.setDate(1);
  monthStart.setHours(0, 0, 0, 0);

  const yesterday = new Date();
  yesterday.setDate(yesterday.getDate() - 1);

  // Run all queries in parallel
  const [
    spendResult,
    tenantsResult,
    failedJobsResult,
    dailyCostResult,
    tenantEconomicsResult,
  ] = await Promise.all([
    // Monthly spend
    db.from("usage_events")
      .select("cost_usd")
      .gte("created_at", monthStart.toISOString()),

    // Tenant counts by status
    db.from("tenants")
      .select("id, plan_tier, subscription_status"),

    // Failed jobs in last 24h (worker uses "dead" for max-retries-exceeded, "failed" for transient)
    db.from("job_queue")
      .select("id", { count: "exact", head: true })
      .in("status", ["failed", "dead"])
      .gte("created_at", yesterday.toISOString()),

    // Daily cost for last 30 days (RPC may not exist yet)
    db.rpc("get_daily_costs_30d").then(
      (res) => res,
      () => ({ data: null }),
    ),

    // Per-tenant economics
    db.from("tenants")
      .select("id, name, plan_tier, subscription_status, monthly_posts_used, monthly_post_limit, video_credits_remaining"),
  ]);

  // Calculate metrics
  const totalSpend = (spendResult.data || []).reduce(
    (sum, e) => sum + Number(e.cost_usd || 0), 0
  );

  const tenants = tenantsResult.data || [];
  const activeTenants = tenants.filter(t => t.subscription_status === "active").length;
  const trialUsers = tenants.filter(t => t.subscription_status === "free_trial").length;

  const mrr = tenants
    .filter(t => t.subscription_status === "active")
    .reduce((sum, t) => sum + (PLAN_PRICES[t.plan_tier] || 0), 0);

  const grossMargin = mrr > 0 ? ((mrr - totalSpend) / mrr * 100) : 0;

  const failedJobs = failedJobsResult.count || 0;

  // Burn rate projection
  const today = new Date();
  const daysElapsed = Math.max(1, today.getDate());
  const daysInMonth = new Date(today.getFullYear(), today.getMonth() + 1, 0).getDate();
  const burnProjection = (totalSpend / daysElapsed) * daysInMonth;

  return {
    totalSpend,
    mrr,
    grossMargin,
    activeTenants,
    trialUsers,
    failedJobs,
    burnProjection,
    dailyCosts: dailyCostResult?.data || [],
    tenantEconomics: tenantEconomicsResult.data || [],
  };
}

export default async function DashboardPage() {
  const data = await getDashboardData();

  const metrics = [
    {
      title: "Monthly Spend",
      value: `$${data.totalSpend.toFixed(2)}`,
      trend: undefined,
      change: undefined,
    },
    {
      title: "Estimated MRR",
      value: `$${data.mrr}`,
      trend: undefined,
      change: undefined,
    },
    {
      title: "Gross Margin",
      value: data.mrr > 0 ? `${data.grossMargin.toFixed(1)}%` : "—",
      trend: (data.grossMargin >= 50 ? "up" : "down") as "up" | "down",
      change: undefined,
    },
    {
      title: "Active Tenants",
      value: String(data.activeTenants),
      trend: undefined,
      change: undefined,
    },
    {
      title: "Trial Users",
      value: String(data.trialUsers),
      trend: undefined,
      change: undefined,
    },
    {
      title: "Failed Jobs (24h)",
      value: String(data.failedJobs),
      trend: (data.failedJobs === 0 ? "down" : "up") as "up" | "down",
      change: undefined,
    },
  ];

  return (
    <div className="flex flex-col gap-8">
      <RealtimeRefresher />
      <h1 className="text-2xl font-bold">Dashboard</h1>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {metrics.map((metric) => (
          <MetricCard key={metric.title} {...metric} />
        ))}
      </div>

      {/* Burn Rate */}
      <div
        className="rounded-lg p-5 border"
        style={{ background: "var(--color-bg-card)", borderColor: "var(--color-border)" }}
      >
        <p className="text-xs font-medium uppercase tracking-wider mb-1" style={{ color: "var(--color-text-muted)" }}>
          Projected Monthly Burn
        </p>
        <p className="text-xl font-bold" style={{ color: "var(--color-warning)" }}>
          ${data.burnProjection.toFixed(2)}
        </p>
        <p className="text-xs mt-1" style={{ color: "var(--color-text-muted)" }}>
          Based on ${data.totalSpend.toFixed(2)} spent in {new Date().getDate()} days
        </p>
      </div>

      {/* Cost Chart */}
      <CostChart data={data.dailyCosts} />

      {/* Per-Tenant Economics */}
      <TenantEconomicsTable tenants={data.tenantEconomics} planPrices={PLAN_PRICES} />
    </div>
  );
}
