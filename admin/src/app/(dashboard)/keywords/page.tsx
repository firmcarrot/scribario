import { createServiceClient } from "@/lib/supabase/server";
import { KeywordsClient } from "./KeywordsClient";

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
  return <KeywordsClient keywords={keywords} />;
}
