"use client";

import { useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { createClient } from "@/lib/supabase/client";

/**
 * Subscribes to Supabase realtime changes on specified tables
 * and throttles router.refresh() calls to avoid excessive re-renders.
 *
 * @param tablesKey - Stable string key for the tables (e.g. "job_queue,usage_events,tenants")
 * @param debounceMs - Minimum interval between refreshes
 */
export function useRealtimeRefresh(
  tablesKey: string,
  debounceMs: number = 5000
) {
  const router = useRouter();
  const lastRefresh = useRef(0);

  useEffect(() => {
    const tables = tablesKey.split(",");
    const supabase = createClient();

    const channel = supabase.channel("admin-dashboard-realtime");

    for (const table of tables) {
      channel.on(
        "postgres_changes",
        { event: "*", schema: "public", table: table.trim() },
        () => maybeRefresh()
      );
    }

    channel.subscribe();

    function maybeRefresh() {
      const now = Date.now();
      if (now - lastRefresh.current > debounceMs) {
        lastRefresh.current = now;
        router.refresh();
      }
    }

    return () => {
      supabase.removeChannel(channel);
    };
  }, [tablesKey, debounceMs, router]);
}
