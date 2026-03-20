"use server";

import { createServiceClient, createServerSupabaseClient } from "@/lib/supabase/server";

async function requireAdmin() {
  const supabase = await createServerSupabaseClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) throw new Error("Unauthorized");
  return user;
}

const TIER_LIMITS: Record<string, { posts: number; videos: number }> = {
  free_trial: { posts: 5, videos: 1 },
  starter: { posts: 30, videos: 5 },
  growth: { posts: 60, videos: 15 },
  pro: { posts: 150, videos: 40 },
};

export async function changePlanTier(tenantId: string, newTier: string) {
  if (!TIER_LIMITS[newTier]) {
    return { error: `Invalid plan tier: ${newTier}` };
  }

  await requireAdmin();
  const db = createServiceClient();
  const limits = TIER_LIMITS[newTier];

  const { error } = await db
    .from("tenants")
    .update({
      plan_tier: newTier,
      monthly_post_limit: limits.posts,
      video_credits_remaining: limits.videos,
      updated_at: new Date().toISOString(),
    })
    .eq("id", tenantId);

  if (error) return { error: error.message };
  return { error: null };
}

export async function changeSubscriptionStatus(
  tenantId: string,
  newStatus: string
) {
  await requireAdmin();
  const validStatuses = [
    "free_trial",
    "active",
    "past_due",
    "paused",
    "canceled",
  ];
  if (!validStatuses.includes(newStatus)) {
    return { error: `Invalid status: ${newStatus}` };
  }

  const db = createServiceClient();
  const updateData: Record<string, unknown> = {
    subscription_status: newStatus,
    updated_at: new Date().toISOString(),
  };

  if (newStatus === "canceled") {
    updateData.canceled_at = new Date().toISOString();
  }

  const { error } = await db
    .from("tenants")
    .update(updateData)
    .eq("id", tenantId);

  if (error) return { error: error.message };
  return { error: null };
}

export async function resetPostLimits(tenantId: string) {
  await requireAdmin();
  const db = createServiceClient();
  const { error } = await db
    .from("tenants")
    .update({
      monthly_posts_used: 0,
      trial_posts_used: 0,
      updated_at: new Date().toISOString(),
    })
    .eq("id", tenantId);

  if (error) return { error: error.message };
  return { error: null };
}

export async function adjustVideoCredits(tenantId: string, credits: number) {
  await requireAdmin();
  if (credits < 0) return { error: "Credits cannot be negative" };

  const db = createServiceClient();
  const { error } = await db
    .from("tenants")
    .update({
      video_credits_remaining: credits,
      updated_at: new Date().toISOString(),
    })
    .eq("id", tenantId);

  if (error) return { error: error.message };
  return { error: null };
}

export async function setHardCostLimit(tenantId: string, limitUsd: number) {
  await requireAdmin();
  if (limitUsd < 0) return { error: "Limit cannot be negative" };

  const db = createServiceClient();
  const { error } = await db
    .from("tenants")
    .update({
      monthly_cost_hard_limit_usd: limitUsd,
      updated_at: new Date().toISOString(),
    })
    .eq("id", tenantId);

  if (error) return { error: error.message };
  return { error: null };
}
