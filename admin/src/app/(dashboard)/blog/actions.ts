"use server";

import { createServiceClient } from "@/lib/supabase/server";

interface BlogPostData {
  title: string;
  slug: string;
  description: string;
  body: string;
  author: string;
  reading_time: string | null;
  image_url: string | null;
  image_alt: string | null;
  seo_title: string | null;
  seo_description: string | null;
  status: "draft" | "published";
}

export async function saveBlogPost(data: BlogPostData) {
  const db = createServiceClient();

  const { error } = await db.from("blog_posts").insert({
    ...data,
    published_at: data.status === "published" ? new Date().toISOString() : null,
  });

  if (error) {
    return { error: error.message };
  }
  return { error: null };
}

export async function updateBlogPost(id: string, data: Partial<BlogPostData>) {
  const db = createServiceClient();

  const updateData: Record<string, unknown> = { ...data, updated_at: new Date().toISOString() };
  if (data.status === "published" && !updateData.published_at) {
    updateData.published_at = new Date().toISOString();
  }

  const { error } = await db.from("blog_posts").update(updateData).eq("id", id);

  if (error) {
    return { error: error.message };
  }
  return { error: null };
}
