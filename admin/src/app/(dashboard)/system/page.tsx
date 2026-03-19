import { createServiceClient } from "@/lib/supabase/server";
import {
  Activity,
  AlertTriangle,
  CheckCircle,
  Clock,
  Cpu,
  Layers,
  Video,
  Zap,
} from "lucide-react";

interface FailedJob {
  id: string;
  error_message: string | null;
  created_at: string;
  tenant_id: string | null;
  job_type: string | null;
}

async function getSystemHealthData() {
  const db = createServiceClient();

  const now = new Date();
  const twentyFourHoursAgo = new Date(now.getTime() - 24 * 60 * 60 * 1000);
  const sevenDaysAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);

  const [
    queuedResult,
    processingResult,
    failedCountResult,
    failedListResult,
    successPostsResult,
    totalPostsResult,
    autopilotResult,
    videoCreditsResult,
  ] = await Promise.all([
    // Queue depth
    db
      .from("job_queue")
      .select("id", { count: "exact", head: true })
      .eq("status", "queued")
      .then(
        (res) => res,
        () => ({ count: null, data: null, error: null }),
      ),

    // Processing
    db
      .from("job_queue")
      .select("id", { count: "exact", head: true })
      .eq("status", "processing")
      .then(
        (res) => res,
        () => ({ count: null, data: null, error: null }),
      ),

    // Failed jobs count (24h)
    db
      .from("job_queue")
      .select("id", { count: "exact", head: true })
      .eq("status", "failed")
      .gte("created_at", twentyFourHoursAgo.toISOString())
      .then(
        (res) => res,
        () => ({ count: null, data: null, error: null }),
      ),

    // Failed jobs list (24h) — most recent first
    db
      .from("job_queue")
      .select("id, error_message, created_at, tenant_id, job_type")
      .eq("status", "failed")
      .gte("created_at", twentyFourHoursAgo.toISOString())
      .order("created_at", { ascending: false })
      .limit(20)
      .then(
        (res) => res,
        () => ({ data: null, error: null }),
      ),

    // Posting success count (7d)
    db
      .from("posting_results")
      .select("id", { count: "exact", head: true })
      .eq("status", "success")
      .gte("created_at", sevenDaysAgo.toISOString())
      .then(
        (res) => res,
        () => ({ count: null, data: null, error: null }),
      ),

    // Posting total count (7d)
    db
      .from("posting_results")
      .select("id", { count: "exact", head: true })
      .gte("created_at", sevenDaysAgo.toISOString())
      .then(
        (res) => res,
        () => ({ count: null, data: null, error: null }),
      ),

    // Active autopilot configs
    db
      .from("autopilot_configs")
      .select("id", { count: "exact", head: true })
      .eq("enabled", true)
      .then(
        (res) => res,
        () => ({ count: null, data: null, error: null }),
      ),

    // Video credits total
    db
      .from("tenants")
      .select("video_credits_remaining")
      .then(
        (res) => res,
        () => ({ data: null, error: null }),
      ),
  ]);

  const queueDepth = queuedResult.count ?? 0;
  const processing = processingResult.count ?? 0;
  const failedCount = failedCountResult.count ?? 0;
  const failedJobs: FailedJob[] = (failedListResult.data as FailedJob[]) || [];

  const successPosts = successPostsResult.count ?? 0;
  const totalPosts = totalPostsResult.count ?? 0;
  const successRate = totalPosts > 0 ? (successPosts / totalPosts) * 100 : null;

  const autopilotActive = autopilotResult.count ?? 0;

  const videoCreditsTotal = (videoCreditsResult.data || []).reduce(
    (sum: number, t: { video_credits_remaining: number | null }) =>
      sum + Number(t.video_credits_remaining || 0),
    0,
  );

  return {
    queueDepth,
    processing,
    failedCount,
    failedJobs,
    successRate,
    successPosts,
    totalPosts,
    autopilotActive,
    videoCreditsTotal,
  };
}

function formatTimeAgo(dateStr: string): string {
  const now = Date.now();
  const then = new Date(dateStr).getTime();
  const diffMin = Math.round((now - then) / 60000);
  if (diffMin < 1) return "just now";
  if (diffMin < 60) return `${diffMin}m ago`;
  const diffHrs = Math.round(diffMin / 60);
  if (diffHrs < 24) return `${diffHrs}h ago`;
  return `${Math.round(diffHrs / 24)}d ago`;
}

export default async function SystemPage() {
  const data = await getSystemHealthData();

  const overallHealthy =
    data.failedCount === 0 && data.queueDepth < 50 && data.processing < 20;

  return (
    <div className="flex flex-col gap-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">System Health</h1>
        <div
          className="flex items-center gap-2 rounded-full px-3 py-1 text-xs font-medium"
          style={{
            background: overallHealthy
              ? "color-mix(in srgb, var(--color-success) 15%, transparent)"
              : "color-mix(in srgb, var(--color-warning) 15%, transparent)",
            color: overallHealthy
              ? "var(--color-success)"
              : "var(--color-warning)",
          }}
        >
          {overallHealthy ? (
            <CheckCircle size={14} />
          ) : (
            <AlertTriangle size={14} />
          )}
          {overallHealthy ? "All Systems Operational" : "Attention Needed"}
        </div>
      </div>

      {/* Metric Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {/* Queue Depth */}
        <div
          className="rounded-lg p-5 border"
          style={{
            background: "var(--color-bg-card)",
            borderColor: "var(--color-border)",
          }}
        >
          <div className="flex items-center justify-between mb-3">
            <p
              className="text-xs font-medium uppercase tracking-wider"
              style={{ color: "var(--color-text-muted)" }}
            >
              Queue Depth
            </p>
            <Layers
              size={16}
              style={{
                color:
                  data.queueDepth > 50
                    ? "var(--color-warning)"
                    : "var(--color-text-muted)",
              }}
            />
          </div>
          <p className="text-2xl font-bold" style={{ color: "var(--color-text)" }}>
            {data.queueDepth}
          </p>
          <p className="text-xs mt-1" style={{ color: "var(--color-text-muted)" }}>
            jobs waiting
          </p>
        </div>

        {/* Processing */}
        <div
          className="rounded-lg p-5 border"
          style={{
            background: "var(--color-bg-card)",
            borderColor: "var(--color-border)",
          }}
        >
          <div className="flex items-center justify-between mb-3">
            <p
              className="text-xs font-medium uppercase tracking-wider"
              style={{ color: "var(--color-text-muted)" }}
            >
              Processing
            </p>
            <Cpu
              size={16}
              style={{
                color:
                  data.processing > 0
                    ? "var(--color-accent)"
                    : "var(--color-text-muted)",
              }}
            />
          </div>
          <p className="text-2xl font-bold" style={{ color: "var(--color-text)" }}>
            {data.processing}
          </p>
          <p className="text-xs mt-1" style={{ color: "var(--color-text-muted)" }}>
            jobs in progress
          </p>
        </div>

        {/* Failed Jobs (24h) */}
        <div
          className="rounded-lg p-5 border"
          style={{
            background: "var(--color-bg-card)",
            borderColor:
              data.failedCount > 0
                ? "var(--color-danger)"
                : "var(--color-border)",
          }}
        >
          <div className="flex items-center justify-between mb-3">
            <p
              className="text-xs font-medium uppercase tracking-wider"
              style={{ color: "var(--color-text-muted)" }}
            >
              Failed Jobs (24h)
            </p>
            <AlertTriangle
              size={16}
              style={{
                color:
                  data.failedCount > 0
                    ? "var(--color-danger)"
                    : "var(--color-text-muted)",
              }}
            />
          </div>
          <p
            className="text-2xl font-bold"
            style={{
              color:
                data.failedCount > 0
                  ? "var(--color-danger)"
                  : "var(--color-text)",
            }}
          >
            {data.failedCount}
          </p>
          <p className="text-xs mt-1" style={{ color: "var(--color-text-muted)" }}>
            errors in last 24 hours
          </p>
        </div>

        {/* Posting Success Rate (7d) */}
        <div
          className="rounded-lg p-5 border"
          style={{
            background: "var(--color-bg-card)",
            borderColor: "var(--color-border)",
          }}
        >
          <div className="flex items-center justify-between mb-3">
            <p
              className="text-xs font-medium uppercase tracking-wider"
              style={{ color: "var(--color-text-muted)" }}
            >
              Success Rate (7d)
            </p>
            <Activity
              size={16}
              style={{
                color:
                  data.successRate !== null && data.successRate >= 95
                    ? "var(--color-success)"
                    : data.successRate !== null && data.successRate >= 80
                      ? "var(--color-warning)"
                      : "var(--color-text-muted)",
              }}
            />
          </div>
          <p
            className="text-2xl font-bold"
            style={{
              color:
                data.successRate !== null && data.successRate >= 95
                  ? "var(--color-success)"
                  : data.successRate !== null
                    ? "var(--color-warning)"
                    : "var(--color-text)",
            }}
          >
            {data.successRate !== null
              ? `${data.successRate.toFixed(1)}%`
              : "\u2014"}
          </p>
          <p className="text-xs mt-1" style={{ color: "var(--color-text-muted)" }}>
            {data.totalPosts > 0
              ? `${data.successPosts} / ${data.totalPosts} posts`
              : "no posting data"}
          </p>
        </div>

        {/* Autopilot Configs */}
        <div
          className="rounded-lg p-5 border"
          style={{
            background: "var(--color-bg-card)",
            borderColor: "var(--color-border)",
          }}
        >
          <div className="flex items-center justify-between mb-3">
            <p
              className="text-xs font-medium uppercase tracking-wider"
              style={{ color: "var(--color-text-muted)" }}
            >
              Active Autopilots
            </p>
            <Zap
              size={16}
              style={{
                color:
                  data.autopilotActive > 0
                    ? "var(--color-accent)"
                    : "var(--color-text-muted)",
              }}
            />
          </div>
          <p className="text-2xl font-bold" style={{ color: "var(--color-text)" }}>
            {data.autopilotActive}
          </p>
          <p className="text-xs mt-1" style={{ color: "var(--color-text-muted)" }}>
            enabled configurations
          </p>
        </div>

        {/* Video Credits */}
        <div
          className="rounded-lg p-5 border"
          style={{
            background: "var(--color-bg-card)",
            borderColor: "var(--color-border)",
          }}
        >
          <div className="flex items-center justify-between mb-3">
            <p
              className="text-xs font-medium uppercase tracking-wider"
              style={{ color: "var(--color-text-muted)" }}
            >
              Video Credits
            </p>
            <Video
              size={16}
              style={{
                color:
                  data.videoCreditsTotal > 0
                    ? "var(--color-accent)"
                    : "var(--color-text-muted)",
              }}
            />
          </div>
          <p className="text-2xl font-bold" style={{ color: "var(--color-text)" }}>
            {data.videoCreditsTotal}
          </p>
          <p className="text-xs mt-1" style={{ color: "var(--color-text-muted)" }}>
            remaining across all tenants
          </p>
        </div>
      </div>

      {/* Failed Jobs Table */}
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
          <Clock size={16} style={{ color: "var(--color-text-muted)" }} />
          <h2 className="text-sm font-semibold" style={{ color: "var(--color-text)" }}>
            Recent Failed Jobs (24h)
          </h2>
        </div>

        {data.failedJobs.length === 0 ? (
          <div className="px-5 py-12 text-center">
            <CheckCircle
              size={32}
              style={{ color: "var(--color-success)", margin: "0 auto 8px" }}
            />
            <p className="text-sm" style={{ color: "var(--color-text-muted)" }}>
              No failed jobs in the last 24 hours.
            </p>
          </div>
        ) : (
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr
                  style={{
                    borderBottom: "1px solid var(--color-border)",
                  }}
                >
                  <th
                    className="text-xs font-medium uppercase tracking-wider text-left px-5 py-3"
                    style={{ color: "var(--color-text-muted)" }}
                  >
                    Time
                  </th>
                  <th
                    className="text-xs font-medium uppercase tracking-wider text-left px-5 py-3"
                    style={{ color: "var(--color-text-muted)" }}
                  >
                    Job Type
                  </th>
                  <th
                    className="text-xs font-medium uppercase tracking-wider text-left px-5 py-3"
                    style={{ color: "var(--color-text-muted)" }}
                  >
                    Error Message
                  </th>
                  <th
                    className="text-xs font-medium uppercase tracking-wider text-left px-5 py-3"
                    style={{ color: "var(--color-text-muted)" }}
                  >
                    Tenant
                  </th>
                </tr>
              </thead>
              <tbody>
                {data.failedJobs.map((job) => (
                  <tr
                    key={job.id}
                    style={{
                      borderBottom: "1px solid var(--color-border)",
                    }}
                  >
                    <td
                      className="px-5 py-3 text-xs whitespace-nowrap"
                      style={{ color: "var(--color-text-muted)" }}
                    >
                      {formatTimeAgo(job.created_at)}
                    </td>
                    <td
                      className="px-5 py-3 text-xs whitespace-nowrap"
                      style={{ color: "var(--color-text)" }}
                    >
                      {job.job_type || "\u2014"}
                    </td>
                    <td
                      className="px-5 py-3 text-xs"
                      style={{
                        color: "var(--color-danger)",
                        maxWidth: "400px",
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                        whiteSpace: "nowrap",
                      }}
                      title={job.error_message || undefined}
                    >
                      {job.error_message || "No error message"}
                    </td>
                    <td
                      className="px-5 py-3 text-xs font-mono whitespace-nowrap"
                      style={{ color: "var(--color-text-muted)" }}
                    >
                      {job.tenant_id
                        ? job.tenant_id.substring(0, 8) + "\u2026"
                        : "\u2014"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
