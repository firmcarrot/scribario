"use server";

import { createServiceClient, createServerSupabaseClient } from "@/lib/supabase/server";

async function requireAdmin() {
  const supabase = await createServerSupabaseClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) throw new Error("Unauthorized");
  return user;
}

interface KeywordData {
  keyword: string;
  cluster?: string | null;
  search_volume?: number | null;
  difficulty?: number | null;
  trend?: string | null;
  priority?: string | null;
}

export async function createKeyword(data: KeywordData) {
  await requireAdmin();
  const db = createServiceClient();
  const { error } = await db.from("seo_keywords").insert({
    keyword: data.keyword,
    cluster: data.cluster || null,
    search_volume: data.search_volume ?? null,
    difficulty: data.difficulty ?? null,
    trend: data.trend || "stable",
    priority: data.priority || "medium",
    rotation_status: "available",
    times_used: 0,
  });
  if (error) return { error: error.message };
  return { error: null };
}

export async function updateKeyword(id: string, data: Partial<KeywordData>) {
  await requireAdmin();
  const db = createServiceClient();
  const { error } = await db
    .from("seo_keywords")
    .update({ ...data, updated_at: new Date().toISOString() })
    .eq("id", id);
  if (error) return { error: error.message };
  return { error: null };
}

export async function deleteKeyword(id: string) {
  await requireAdmin();
  const db = createServiceClient();
  // Delete junction rows first
  await db.from("blog_post_keywords").delete().eq("keyword_id", id);
  const { error } = await db.from("seo_keywords").delete().eq("id", id);
  if (error) return { error: error.message };
  return { error: null };
}

export async function rotateKeyword(keywordId: string) {
  await requireAdmin();
  const db = createServiceClient();

  const { error } = await db.rpc("increment_keyword_usage", {
    keyword_id: keywordId,
  });

  if (error) return { error: error.message };
  return { error: null };
}

export async function releaseKeyword(
  keywordId: string,
  cooldownDays: number = 14
) {
  await requireAdmin();
  const db = createServiceClient();
  const cooldownUntil = new Date();
  cooldownUntil.setDate(cooldownUntil.getDate() + cooldownDays);

  const { error } = await db
    .from("seo_keywords")
    .update({
      rotation_status: "cooldown",
      cooldown_until: cooldownUntil.toISOString(),
    })
    .eq("id", keywordId);

  if (error) return { error: error.message };
  return { error: null };
}

export async function getNextAvailableKeyword(cluster?: string) {
  await requireAdmin();
  const db = createServiceClient();

  // First, expire any stale cooldowns
  await db
    .from("seo_keywords")
    .update({ rotation_status: "available", cooldown_until: null })
    .eq("rotation_status", "cooldown")
    .lte("cooldown_until", new Date().toISOString());

  // Select next available keyword, prioritize by priority then least-used
  let query = db
    .from("seo_keywords")
    .select("*")
    .eq("rotation_status", "available")
    .order("priority", { ascending: true }) // high first (alphabetically)
    .order("times_used", { ascending: true })
    .limit(1);

  if (cluster) {
    query = query.eq("cluster", cluster);
  }

  const { data, error } = await query.single();
  if (error || !data) return { data: null, error: error?.message || "No available keywords" };
  return { data, error: null };
}

export async function getAvailableKeywords() {
  await requireAdmin();
  const db = createServiceClient();

  // Expire stale cooldowns
  await db
    .from("seo_keywords")
    .update({ rotation_status: "available", cooldown_until: null })
    .eq("rotation_status", "cooldown")
    .lte("cooldown_until", new Date().toISOString());

  const { data } = await db
    .from("seo_keywords")
    .select("id, keyword, cluster, priority, rotation_status, times_used")
    .eq("rotation_status", "available")
    .order("priority", { ascending: true })
    .order("times_used", { ascending: true });

  return data || [];
}

interface CSVImportResult {
  imported: number;
  skipped: number;
  errors: string[];
}

export async function importKeywordsFromCSV(
  csvText: string
): Promise<CSVImportResult> {
  await requireAdmin();
  const lines = csvText.trim().split("\n");
  if (lines.length < 2) {
    return { imported: 0, skipped: 0, errors: ["CSV must have a header row and at least one data row"] };
  }

  // Parse header
  const header = lines[0].toLowerCase().split(",").map((h) => h.trim().replace(/^"/, "").replace(/"$/, ""));
  const keywordIdx = header.indexOf("keyword");
  if (keywordIdx === -1) {
    return { imported: 0, skipped: 0, errors: ["CSV must have a 'keyword' column"] };
  }

  const clusterIdx = header.indexOf("cluster");
  const volumeIdx = header.indexOf("search_volume");
  const difficultyIdx = header.indexOf("difficulty");
  const trendIdx = header.indexOf("trend");
  const priorityIdx = header.indexOf("priority");

  const rows: KeywordData[] = [];
  const errors: string[] = [];
  let skipped = 0;

  for (let i = 1; i < Math.min(lines.length, 1001); i++) {
    const cols = parseCSVLine(lines[i]);
    const keyword = cols[keywordIdx]?.trim();

    if (!keyword) {
      skipped++;
      continue;
    }

    const volume = volumeIdx >= 0 ? parseInt(cols[volumeIdx], 10) : null;
    const difficulty = difficultyIdx >= 0 ? parseInt(cols[difficultyIdx], 10) : null;

    if (volumeIdx >= 0 && cols[volumeIdx] && isNaN(volume!)) {
      errors.push(`Row ${i + 1}: invalid search_volume "${cols[volumeIdx]}"`);
      skipped++;
      continue;
    }

    if (difficultyIdx >= 0 && cols[difficultyIdx] && (isNaN(difficulty!) || difficulty! < 0 || difficulty! > 100)) {
      errors.push(`Row ${i + 1}: difficulty must be 0-100, got "${cols[difficultyIdx]}"`);
      skipped++;
      continue;
    }

    const trend = trendIdx >= 0 ? cols[trendIdx]?.trim().toLowerCase() : null;
    if (trend && !["rising", "stable", "declining"].includes(trend)) {
      errors.push(`Row ${i + 1}: invalid trend "${trend}" (must be rising/stable/declining)`);
      skipped++;
      continue;
    }

    const priority = priorityIdx >= 0 ? cols[priorityIdx]?.trim().toLowerCase() : null;
    if (priority && !["high", "medium", "low"].includes(priority)) {
      errors.push(`Row ${i + 1}: invalid priority "${priority}" (must be high/medium/low)`);
      skipped++;
      continue;
    }

    rows.push({
      keyword,
      cluster: clusterIdx >= 0 ? cols[clusterIdx]?.trim() || null : null,
      search_volume: volume,
      difficulty,
      trend: trend || "stable",
      priority: priority || "medium",
    });
  }

  if (rows.length === 0) {
    return { imported: 0, skipped, errors };
  }

  // Upsert (on conflict by keyword)
  const db = createServiceClient();
  const { error } = await db.from("seo_keywords").upsert(
    rows.map((r) => ({
      ...r,
      rotation_status: "available",
      times_used: 0,
    })),
    { onConflict: "keyword" }
  );

  if (error) {
    return { imported: 0, skipped, errors: [...errors, error.message] };
  }

  return { imported: rows.length, skipped, errors };
}

/** Simple CSV line parser that handles quoted fields with commas. */
function parseCSVLine(line: string): string[] {
  const result: string[] = [];
  let current = "";
  let inQuotes = false;

  for (let i = 0; i < line.length; i++) {
    const ch = line[i];
    if (ch === '"') {
      if (inQuotes && line[i + 1] === '"') {
        current += '"';
        i++;
      } else {
        inQuotes = !inQuotes;
      }
    } else if (ch === "," && !inQuotes) {
      result.push(current.trim());
      current = "";
    } else {
      current += ch;
    }
  }
  result.push(current.trim());
  return result;
}
