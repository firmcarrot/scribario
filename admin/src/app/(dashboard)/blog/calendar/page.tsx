import { createServiceClient } from "@/lib/supabase/server";
import { CalendarGrid } from "./CalendarGrid";

async function getCalendarPosts(year: number, month: number) {
  const db = createServiceClient();

  // Fetch all posts — filter client-side by resolved date
  // This is simpler and correct vs. complex OR queries in PostgREST
  const { data } = await db
    .from("blog_posts")
    .select("id, title, slug, status, published_at, scheduled_for, created_at")
    .order("created_at", { ascending: true });

  // Resolve each post's display date and filter to the target month
  return (data || [])
    .map((p) => ({
      ...p,
      date: p.published_at || p.scheduled_for || p.created_at,
    }))
    .filter((p) => {
      const d = new Date(p.date);
      return d.getFullYear() === year && d.getMonth() + 1 === month;
    });
}

export default async function CalendarPage({
  searchParams,
}: {
  searchParams: Promise<{ month?: string }>;
}) {
  const params = await searchParams;
  const now = new Date();
  let year = now.getFullYear();
  let month = now.getMonth() + 1;

  if (params.month) {
    const parts = params.month.split("-");
    if (parts.length === 2) {
      year = parseInt(parts[0], 10);
      month = parseInt(parts[1], 10);
    }
  }

  const posts = await getCalendarPosts(year, month);

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Content Calendar</h1>
      </div>
      <CalendarGrid posts={posts} year={year} month={month} />
    </div>
  );
}
