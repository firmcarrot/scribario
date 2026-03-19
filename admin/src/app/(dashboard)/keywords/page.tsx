import { createServiceClient } from "@/lib/supabase/server";

const ROTATION_COLORS: Record<string, string> = {
  available: "var(--color-success)",
  in_use: "var(--color-warning)",
  cooldown: "var(--color-danger)",
};

async function getKeywords() {
  const db = createServiceClient();
  const { data, error } = await db
    .from("seo_keywords")
    .select("*")
    .order("priority", { ascending: true })
    .order("created_at", { ascending: false });

  if (error) {
    console.error("Failed to fetch keywords:", error);
    return [];
  }
  return data || [];
}

export default async function KeywordsPage() {
  const keywords = await getKeywords();

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-2xl font-bold">Keyword Library</h1>

      {keywords.length === 0 ? (
        <div className="rounded-lg p-8 border text-center" style={{ background: "var(--color-bg-card)", borderColor: "var(--color-border)", color: "var(--color-text-muted)" }}>
          No keywords tracked yet. Add keywords to start building your SEO strategy.
        </div>
      ) : (
        <div className="rounded-lg border overflow-hidden" style={{ background: "var(--color-bg-card)", borderColor: "var(--color-border)" }}>
          <table className="w-full text-sm">
            <thead>
              <tr style={{ borderBottom: `1px solid var(--color-border)` }}>
                {["Keyword", "Cluster", "Volume", "Difficulty", "Trend", "Priority", "Status", "Used"].map((h) => (
                  <th key={h} className="text-left px-4 py-3 text-xs font-medium uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {keywords.map((kw) => (
                <tr key={kw.id} className="hover:opacity-80" style={{ borderBottom: `1px solid var(--color-border)` }}>
                  <td className="px-4 py-3 font-medium" style={{ color: "var(--color-text)" }}>{kw.keyword}</td>
                  <td className="px-4 py-3" style={{ color: "var(--color-text-muted)" }}>{kw.cluster || "—"}</td>
                  <td className="px-4 py-3" style={{ color: "var(--color-text-muted)" }}>{kw.search_volume ?? "—"}</td>
                  <td className="px-4 py-3" style={{ color: "var(--color-text-muted)" }}>{kw.difficulty ?? "—"}</td>
                  <td className="px-4 py-3" style={{ color: "var(--color-text-muted)" }}>{kw.trend || "—"}</td>
                  <td className="px-4 py-3">
                    <span className="capitalize" style={{ color: kw.priority === "high" ? "var(--color-danger)" : kw.priority === "medium" ? "var(--color-warning)" : "var(--color-text-muted)" }}>
                      {kw.priority}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className="inline-block px-2 py-0.5 rounded text-xs font-medium" style={{ color: ROTATION_COLORS[kw.rotation_status] || "var(--color-text-muted)", background: `${ROTATION_COLORS[kw.rotation_status] || "var(--color-text-muted)"}15` }}>
                      {kw.rotation_status}
                    </span>
                  </td>
                  <td className="px-4 py-3" style={{ color: "var(--color-text-muted)" }}>{kw.times_used}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
