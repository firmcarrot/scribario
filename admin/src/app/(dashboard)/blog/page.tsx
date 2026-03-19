import Link from "next/link";
import { createServiceClient } from "@/lib/supabase/server";

type PostStatus = "draft" | "review" | "scheduled" | "published" | "archived";

const STATUS_COLORS: Record<PostStatus, string> = {
  draft: "var(--color-text-muted)",
  review: "var(--color-warning)",
  scheduled: "var(--color-accent)",
  published: "var(--color-success)",
  archived: "var(--color-text-muted)",
};

async function getPosts() {
  const db = createServiceClient();
  const { data, error } = await db
    .from("blog_posts")
    .select("id, slug, title, status, published_at, reading_time, author, created_at")
    .order("created_at", { ascending: false });

  if (error) {
    console.error("Failed to fetch posts:", error);
    return [];
  }
  return data || [];
}

export default async function BlogListPage() {
  const posts = await getPosts();

  const statusCounts = {
    all: posts.length,
    draft: posts.filter((p) => p.status === "draft").length,
    published: posts.filter((p) => p.status === "published").length,
    archived: posts.filter((p) => p.status === "archived").length,
  };

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Blog Posts</h1>
        <Link
          href="/blog/new"
          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          style={{ background: "var(--color-accent)", color: "#fff" }}
        >
          + New Post
        </Link>
      </div>

      {/* Filter tabs */}
      <div className="flex gap-4 text-sm font-medium border-b" style={{ borderColor: "var(--color-border)" }}>
        {(["all", "draft", "published", "archived"] as const).map((tab) => (
          <span
            key={tab}
            className="px-4 py-2 capitalize"
            style={{ color: "var(--color-text)", borderBottom: "2px solid transparent" }}
          >
            {tab} ({statusCounts[tab]})
          </span>
        ))}
      </div>

      {/* Posts table */}
      {posts.length === 0 ? (
        <div
          className="rounded-lg p-8 border text-center"
          style={{ background: "var(--color-bg-card)", borderColor: "var(--color-border)", color: "var(--color-text-muted)" }}
        >
          No blog posts yet. Create your first one!
        </div>
      ) : (
        <div
          className="rounded-lg border overflow-hidden"
          style={{ background: "var(--color-bg-card)", borderColor: "var(--color-border)" }}
        >
          <table className="w-full text-sm">
            <thead>
              <tr style={{ borderBottom: `1px solid var(--color-border)` }}>
                {["Title", "Status", "Published", "Reading Time", ""].map((h) => (
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
              {posts.map((post) => (
                <tr
                  key={post.id}
                  className="hover:opacity-80"
                  style={{ borderBottom: `1px solid var(--color-border)` }}
                >
                  <td className="px-4 py-3 font-medium" style={{ color: "var(--color-text)" }}>
                    {post.title}
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className="inline-block px-2 py-0.5 rounded text-xs font-medium capitalize"
                      style={{
                        color: STATUS_COLORS[post.status as PostStatus] || "var(--color-text-muted)",
                        background: `${STATUS_COLORS[post.status as PostStatus] || "var(--color-text-muted)"}15`,
                      }}
                    >
                      {post.status}
                    </span>
                  </td>
                  <td className="px-4 py-3" style={{ color: "var(--color-text-muted)" }}>
                    {post.published_at
                      ? new Date(post.published_at).toLocaleDateString("en-US", {
                          month: "short",
                          day: "numeric",
                          year: "numeric",
                        })
                      : "—"}
                  </td>
                  <td className="px-4 py-3" style={{ color: "var(--color-text-muted)" }}>
                    {post.reading_time || "—"}
                  </td>
                  <td className="px-4 py-3">
                    <Link
                      href={`/blog/${post.id}`}
                      className="text-xs font-medium hover:underline"
                      style={{ color: "var(--color-accent)" }}
                    >
                      Edit
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
