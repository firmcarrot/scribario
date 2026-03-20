"use client";

import { useRouter } from "next/navigation";
import { ChevronLeft, ChevronRight } from "lucide-react";
import Link from "next/link";

interface CalendarPost {
  id: string;
  title: string;
  slug: string;
  status: string;
  date: string;
}

const STATUS_COLORS: Record<string, string> = {
  published: "var(--color-success)",
  draft: "var(--color-text-muted)",
  scheduled: "var(--color-warning)",
  review: "var(--color-accent)",
  archived: "rgba(255,255,255,0.2)",
};

const MONTH_NAMES = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December",
];

const DAY_NAMES = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

export function CalendarGrid({
  posts,
  year,
  month,
}: {
  posts: CalendarPost[];
  year: number;
  month: number;
}) {
  const router = useRouter();

  const firstDayOfMonth = new Date(year, month - 1, 1).getDay();
  const daysInMonth = new Date(year, month, 0).getDate();
  const today = new Date();
  const isCurrentMonth =
    today.getFullYear() === year && today.getMonth() + 1 === month;

  // Build grid: 6 rows x 7 cols
  const cells: (number | null)[] = [];
  for (let i = 0; i < firstDayOfMonth; i++) cells.push(null);
  for (let d = 1; d <= daysInMonth; d++) cells.push(d);
  while (cells.length % 7 !== 0) cells.push(null);

  // Group posts by day
  const postsByDay: Record<number, CalendarPost[]> = {};
  for (const p of posts) {
    const d = new Date(p.date);
    if (d.getFullYear() === year && d.getMonth() + 1 === month) {
      const day = d.getDate();
      if (!postsByDay[day]) postsByDay[day] = [];
      postsByDay[day].push(p);
    }
  }

  const prevMonth = month === 1 ? `${year - 1}-12` : `${year}-${String(month - 1).padStart(2, "0")}`;
  const nextMonth = month === 12 ? `${year + 1}-01` : `${year}-${String(month + 1).padStart(2, "0")}`;

  return (
    <div
      className="rounded-lg border overflow-hidden"
      style={{
        background: "var(--color-bg-card)",
        borderColor: "var(--color-border)",
      }}
    >
      {/* Header with navigation */}
      <div
        className="flex items-center justify-between px-5 py-4 border-b"
        style={{ borderColor: "var(--color-border)" }}
      >
        <button
          onClick={() => router.push(`/blog/calendar?month=${prevMonth}`)}
          className="p-1.5 rounded cursor-pointer hover:opacity-70"
          style={{ color: "var(--color-text-muted)" }}
        >
          <ChevronLeft size={18} />
        </button>
        <p
          className="text-sm font-semibold"
          style={{ color: "var(--color-text)" }}
        >
          {MONTH_NAMES[month - 1]} {year}
        </p>
        <button
          onClick={() => router.push(`/blog/calendar?month=${nextMonth}`)}
          className="p-1.5 rounded cursor-pointer hover:opacity-70"
          style={{ color: "var(--color-text-muted)" }}
        >
          <ChevronRight size={18} />
        </button>
      </div>

      {/* Day headers */}
      <div className="grid grid-cols-7">
        {DAY_NAMES.map((d) => (
          <div
            key={d}
            className="px-2 py-2 text-center text-xs font-medium uppercase tracking-wider"
            style={{
              color: "var(--color-text-muted)",
              borderBottom: "1px solid var(--color-border)",
            }}
          >
            {d}
          </div>
        ))}
      </div>

      {/* Calendar grid */}
      <div className="grid grid-cols-7">
        {cells.map((day, idx) => {
          const isToday = isCurrentMonth && day === today.getDate();
          const dayPosts = day ? postsByDay[day] || [] : [];

          return (
            <div
              key={idx}
              className="min-h-[80px] p-1.5"
              style={{
                borderRight:
                  (idx + 1) % 7 !== 0
                    ? "1px solid var(--color-border)"
                    : undefined,
                borderBottom:
                  idx < cells.length - 7
                    ? "1px solid var(--color-border)"
                    : undefined,
                background: day ? "transparent" : "rgba(255,255,255,0.02)",
              }}
            >
              {day && (
                <>
                  <span
                    className="text-xs font-medium inline-block mb-1"
                    style={{
                      color: isToday
                        ? "var(--color-accent)"
                        : "var(--color-text-muted)",
                      fontWeight: isToday ? 700 : 500,
                    }}
                  >
                    {day}
                  </span>
                  <div className="flex flex-col gap-0.5">
                    {dayPosts.slice(0, 3).map((p) => (
                      <Link
                        key={p.id}
                        href={`/blog/${p.id}`}
                        className="block truncate rounded px-1 py-0.5 text-[10px] font-medium hover:opacity-80"
                        style={{
                          background: `color-mix(in srgb, ${STATUS_COLORS[p.status] || "var(--color-text-muted)"} 20%, transparent)`,
                          color:
                            STATUS_COLORS[p.status] ||
                            "var(--color-text-muted)",
                        }}
                        title={p.title}
                      >
                        {p.title}
                      </Link>
                    ))}
                    {dayPosts.length > 3 && (
                      <span
                        className="text-[10px] px-1"
                        style={{ color: "var(--color-text-muted)" }}
                      >
                        +{dayPosts.length - 3} more
                      </span>
                    )}
                  </div>
                </>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
