import { createServiceClient } from "@/lib/supabase/server";
import { notFound } from "next/navigation";
import { BlogEditor } from "./BlogEditor";

async function getPost(id: string) {
  const db = createServiceClient();
  const { data, error } = await db
    .from("blog_posts")
    .select("*")
    .eq("id", id)
    .single();

  if (error || !data) return null;
  return data;
}

export default async function EditPostPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const post = await getPost(id);
  if (!post) notFound();

  return (
    <div className="flex flex-col gap-6 max-w-4xl">
      <h1 className="text-2xl font-bold">Edit Post</h1>
      <BlogEditor post={post} />
    </div>
  );
}
