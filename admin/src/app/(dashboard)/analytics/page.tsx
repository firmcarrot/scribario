import MetricCard from "@/components/charts/MetricCard";
import { createServiceClient } from "@/lib/supabase/server";
import { AnalyticsCharts } from "./AnalyticsCharts";

async function getAnalyticsData() {
  const db = createServiceClient();

  const now = new Date();

  const todayStart = new Date(now);
  todayStart.setHours(0, 0, 0, 0);

  const sevenDaysAgo = new Date(now);
  sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);

  const thirtyDaysAgo = new Date(now);
  thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);

  // Graceful query helper — converts PostgREST builder to Promise and catches errors
  const safe = <T,>(query: PromiseLike<T>): Promise<T> =>
    Promise.resolve(query).then(
      (res) => res,
      () => ({ data: null, count: null }) as T,
    );

  const [
    dauResult,
    wauResult,
    mauResult,
    videoRequestsResult,
    textRequestsResult,
    platformCountsResult,
    approveResult,
    rejectResult,
    regenerateResult,
    totalFeedbackResult,
  ] = await Promise.all([
    // DAU: distinct tenants today
    safe(
      db
        .from("content_requests")
        .select("tenant_id")
        .gte("created_at", todayStart.toISOString()),
    ),
    // WAU: distinct tenants last 7 days
    safe(
      db
        .from("content_requests")
        .select("tenant_id")
        .gte("created_at", sevenDaysAgo.toISOString()),
    ),
    // MAU: distinct tenants last 30 days
    safe(
      db
        .from("content_requests")
        .select("tenant_id")
        .gte("created_at", thirtyDaysAgo.toISOString()),
    ),
    // Video requests
    safe(
      db
        .from("content_requests")
        .select("id", { count: "exact", head: true })
        .ilike("intent", "%video%"),
    ),
    // Text+image requests (not video)
    safe(
      db
        .from("content_requests")
        .select("id", { count: "exact", head: true })
        .not("intent", "ilike", "%video%"),
    ),
    // Platform counts from posting_results
    safe(
      db.from("posting_results").select("platform"),
    ),
    // Approval feedback
    safe(
      db
        .from("feedback_events")
        .select("id", { count: "exact", head: true })
        .eq("action", "approve"),
    ),
    // Reject feedback
    safe(
      db
        .from("feedback_events")
        .select("id", { count: "exact", head: true })
        .eq("action", "reject"),
    ),
    // Regenerate feedback
    safe(
      db
        .from("feedback_events")
        .select("id", { count: "exact", head: true })
        .eq("action", "regenerate"),
    ),
    // Total feedback
    safe(
      db
        .from("feedback_events")
        .select("id", { count: "exact", head: true }),
    ),
  ]);

  // Count distinct tenant_ids
  const distinctCount = (rows: { tenant_id: string }[] | null): number => {
    if (!rows || rows.length === 0) return 0;
    return new Set(rows.map((r) => r.tenant_id)).size;
  };

  const dau = distinctCount(dauResult.data as { tenant_id: string }[] | null);
  const wau = distinctCount(wauResult.data as { tenant_id: string }[] | null);
  const mau = distinctCount(mauResult.data as { tenant_id: string }[] | null);

  // Feature usage
  const videoCount = videoRequestsResult.count ?? 0;
  const textImageCount = textRequestsResult.count ?? 0;

  // Platform breakdown
  const platformRows = (platformCountsResult.data as { platform: string }[] | null) || [];
  const platformMap: Record<string, number> = {};
  for (const row of platformRows) {
    const p = row.platform || "unknown";
    platformMap[p] = (platformMap[p] || 0) + 1;
  }
  const topPlatforms = Object.entries(platformMap)
    .map(([platform, count]) => ({ platform, count }))
    .sort((a, b) => b.count - a.count);

  // Approval rate
  const approveCount = approveResult.count ?? 0;
  const rejectCount = rejectResult.count ?? 0;
  const regenerateCount = regenerateResult.count ?? 0;
  const totalFeedback = totalFeedbackResult.count ?? 0;
  const approvalRate = totalFeedback > 0 ? (approveCount / totalFeedback) * 100 : 0;

  // Daily analytics for charts (RPC may not exist yet)
  const dailyAnalyticsResult = await Promise.resolve(
    db.rpc("get_daily_analytics_30d")
  ).then(
    (res) => res,
    () => ({ data: null }),
  );

  return {
    dau,
    wau,
    mau,
    videoCount,
    textImageCount,
    topPlatforms,
    approveCount,
    rejectCount,
    regenerateCount,
    totalFeedback,
    approvalRate,
    dailyAnalytics: dailyAnalyticsResult?.data || [],
  };
}

export default async function AnalyticsPage() {
  const data = await getAnalyticsData();

  const userMetrics = [
    { title: "DAU (Today)", value: String(data.dau) },
    { title: "WAU (7 Days)", value: String(data.wau) },
    { title: "MAU (30 Days)", value: String(data.mau) },
  ];

  const hasFeatureData = data.videoCount > 0 || data.textImageCount > 0;
  const hasPlatformData = data.topPlatforms.length > 0;
  const hasFeedbackData = data.totalFeedback > 0;

  return (
    <div className="flex flex-col gap-8">
      <h1 className="text-2xl font-bold">Analytics</h1>

      {/* Active Users */}
      <section>
        <h2
          className="text-sm font-medium uppercase tracking-wider mb-3"
          style={{ color: "var(--color-text-muted)" }}
        >
          Active Users
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {userMetrics.map((m) => (
            <MetricCard key={m.title} title={m.title} value={m.value} />
          ))}
        </div>
      </section>

      {/* Activity Charts */}
      <AnalyticsCharts data={data.dailyAnalytics} />

      {/* Feature Usage */}
      <section>
        <h2
          className="text-sm font-medium uppercase tracking-wider mb-3"
          style={{ color: "var(--color-text-muted)" }}
        >
          Feature Usage
        </h2>
        <div
          className="rounded-lg border overflow-hidden"
          style={{
            background: "var(--color-bg-card)",
            borderColor: "var(--color-border)",
          }}
        >
          {hasFeatureData ? (
            <table className="w-full text-sm">
              <thead>
                <tr
                  style={{
                    borderBottom: "1px solid var(--color-border)",
                  }}
                >
                  <th
                    className="text-left px-5 py-3 text-xs font-medium uppercase tracking-wider"
                    style={{ color: "var(--color-text-muted)" }}
                  >
                    Type
                  </th>
                  <th
                    className="text-right px-5 py-3 text-xs font-medium uppercase tracking-wider"
                    style={{ color: "var(--color-text-muted)" }}
                  >
                    Requests
                  </th>
                  <th
                    className="text-right px-5 py-3 text-xs font-medium uppercase tracking-wider"
                    style={{ color: "var(--color-text-muted)" }}
                  >
                    Share
                  </th>
                </tr>
              </thead>
              <tbody style={{ color: "var(--color-text)" }}>
                {[
                  {
                    label: "Video",
                    count: data.videoCount,
                    color: "var(--color-accent)",
                  },
                  {
                    label: "Text + Image",
                    count: data.textImageCount,
                    color: "var(--color-success)",
                  },
                ].map((row) => {
                  const total = data.videoCount + data.textImageCount;
                  const share = total > 0 ? ((row.count / total) * 100).toFixed(1) : "0";
                  return (
                    <tr
                      key={row.label}
                      style={{ borderBottom: "1px solid var(--color-border)" }}
                    >
                      <td className="px-5 py-3 flex items-center gap-2">
                        <span
                          className="inline-block w-2 h-2 rounded-full"
                          style={{ background: row.color }}
                        />
                        {row.label}
                      </td>
                      <td className="text-right px-5 py-3 font-medium">
                        {row.count.toLocaleString()}
                      </td>
                      <td
                        className="text-right px-5 py-3"
                        style={{ color: "var(--color-text-muted)" }}
                      >
                        {share}%
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          ) : (
            <p
              className="px-5 py-10 text-center text-sm"
              style={{ color: "var(--color-text-muted)" }}
            >
              No data yet
            </p>
          )}
        </div>
      </section>

      {/* Approval Rate */}
      <section>
        <h2
          className="text-sm font-medium uppercase tracking-wider mb-3"
          style={{ color: "var(--color-text-muted)" }}
        >
          Approval Rate
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {/* Rate card */}
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
              Overall Approval Rate
            </p>
            <p
              className="text-3xl font-bold"
              style={{
                color: hasFeedbackData
                  ? data.approvalRate >= 70
                    ? "var(--color-success)"
                    : data.approvalRate >= 40
                      ? "var(--color-warning)"
                      : "var(--color-danger)"
                  : "var(--color-text-muted)",
              }}
            >
              {hasFeedbackData ? `${data.approvalRate.toFixed(1)}%` : "---"}
            </p>
            <p
              className="text-xs mt-1"
              style={{ color: "var(--color-text-muted)" }}
            >
              {hasFeedbackData
                ? `${data.totalFeedback.toLocaleString()} total feedback events`
                : "No feedback data yet"}
            </p>
          </div>

          {/* Breakdown card */}
          <div
            className="rounded-lg p-5 border"
            style={{
              background: "var(--color-bg-card)",
              borderColor: "var(--color-border)",
            }}
          >
            <p
              className="text-xs font-medium uppercase tracking-wider mb-3"
              style={{ color: "var(--color-text-muted)" }}
            >
              Feedback Breakdown
            </p>
            {hasFeedbackData ? (
              <div className="flex flex-col gap-2">
                {[
                  {
                    label: "Approved",
                    count: data.approveCount,
                    color: "var(--color-success)",
                  },
                  {
                    label: "Rejected",
                    count: data.rejectCount,
                    color: "var(--color-danger)",
                  },
                  {
                    label: "Regenerated",
                    count: data.regenerateCount,
                    color: "var(--color-warning)",
                  },
                ].map((item) => (
                  <div key={item.label} className="flex items-center justify-between">
                    <div className="flex items-center gap-2 text-sm">
                      <span
                        className="inline-block w-2 h-2 rounded-full"
                        style={{ background: item.color }}
                      />
                      <span style={{ color: "var(--color-text)" }}>{item.label}</span>
                    </div>
                    <span
                      className="text-sm font-medium"
                      style={{ color: "var(--color-text)" }}
                    >
                      {item.count.toLocaleString()}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <p
                className="text-sm text-center py-4"
                style={{ color: "var(--color-text-muted)" }}
              >
                No data yet
              </p>
            )}
          </div>
        </div>
      </section>

      {/* Top Platforms */}
      <section>
        <h2
          className="text-sm font-medium uppercase tracking-wider mb-3"
          style={{ color: "var(--color-text-muted)" }}
        >
          Top Platforms
        </h2>
        <div
          className="rounded-lg border overflow-hidden"
          style={{
            background: "var(--color-bg-card)",
            borderColor: "var(--color-border)",
          }}
        >
          {hasPlatformData ? (
            <table className="w-full text-sm">
              <thead>
                <tr style={{ borderBottom: "1px solid var(--color-border)" }}>
                  <th
                    className="text-left px-5 py-3 text-xs font-medium uppercase tracking-wider"
                    style={{ color: "var(--color-text-muted)" }}
                  >
                    Platform
                  </th>
                  <th
                    className="text-right px-5 py-3 text-xs font-medium uppercase tracking-wider"
                    style={{ color: "var(--color-text-muted)" }}
                  >
                    Posts
                  </th>
                  <th
                    className="text-right px-5 py-3 text-xs font-medium uppercase tracking-wider"
                    style={{ color: "var(--color-text-muted)" }}
                  >
                    Share
                  </th>
                </tr>
              </thead>
              <tbody style={{ color: "var(--color-text)" }}>
                {data.topPlatforms.map((p, i) => {
                  const totalPosts = data.topPlatforms.reduce(
                    (sum, x) => sum + x.count,
                    0,
                  );
                  const share =
                    totalPosts > 0
                      ? ((p.count / totalPosts) * 100).toFixed(1)
                      : "0";
                  return (
                    <tr
                      key={p.platform}
                      style={{
                        borderBottom:
                          i < data.topPlatforms.length - 1
                            ? "1px solid var(--color-border)"
                            : undefined,
                      }}
                    >
                      <td className="px-5 py-3 capitalize">{p.platform}</td>
                      <td className="text-right px-5 py-3 font-medium">
                        {p.count.toLocaleString()}
                      </td>
                      <td
                        className="text-right px-5 py-3"
                        style={{ color: "var(--color-text-muted)" }}
                      >
                        {share}%
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          ) : (
            <p
              className="px-5 py-10 text-center text-sm"
              style={{ color: "var(--color-text-muted)" }}
            >
              No data yet
            </p>
          )}
        </div>
      </section>
    </div>
  );
}
