"use client";

import { useRealtimeRefresh } from "@/hooks/useRealtimeRefresh";

/**
 * Invisible component that subscribes to realtime changes
 * and triggers page refresh on updates to key tables.
 */
export function RealtimeRefresher() {
  // Pass a stable string instead of an array to avoid re-subscription on every render
  useRealtimeRefresh("job_queue,usage_events,tenants", 5000);
  return null;
}
