"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { updateBlogPost } from "../actions";

interface Post {
  id: string;
  slug: string;
  title: string;
  description: string;
  body: string;
  author: string;
  reading_time: string | null;
  image_url: string | null;
  image_alt: string | null;
  seo_title: string | null;
  seo_description: string | null;
  status: string;
}

export function BlogEditor({ post }: { post: Post }) {
  const router = useRouter();
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const [title, setTitle] = useState(post.title);
  const [slug, setSlug] = useState(post.slug);
  const [description, setDescription] = useState(post.description);
  const [body, setBody] = useState(post.body);
  const [author, setAuthor] = useState(post.author);
  const [readingTime, setReadingTime] = useState(post.reading_time || "");
  const [imageUrl, setImageUrl] = useState(post.image_url || "");
  const [imageAlt, setImageAlt] = useState(post.image_alt || "");
  const [seoTitle, setSeoTitle] = useState(post.seo_title || "");
  const [seoDescription, setSeoDescription] = useState(post.seo_description || "");
  const [status, setStatus] = useState(post.status);

  const handleSave = async () => {
    setSaving(true);
    setError("");

    const result = await updateBlogPost(post.id, {
      title,
      slug,
      description,
      body,
      author,
      reading_time: readingTime || null,
      image_url: imageUrl || null,
      image_alt: imageAlt || null,
      seo_title: seoTitle || null,
      seo_description: seoDescription || null,
      status: status as "draft" | "published",
    });

    setSaving(false);

    if (result.error) {
      setError(result.error);
      return;
    }

    router.push("/blog");
    router.refresh();
  };

  return (
    <>
      {error && (
        <div className="p-3 rounded-lg text-sm" style={{ background: "var(--color-danger)", color: "#fff" }}>
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 flex flex-col gap-4">
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full px-4 py-3 rounded-lg text-lg font-bold border outline-none"
            style={{ background: "var(--color-bg-card)", borderColor: "var(--color-border)", color: "var(--color-text)" }}
          />
          <input
            type="text"
            value={slug}
            onChange={(e) => setSlug(e.target.value)}
            className="w-full px-4 py-2 rounded-lg text-sm font-mono border outline-none"
            style={{ background: "var(--color-bg-card)", borderColor: "var(--color-border)", color: "var(--color-text-muted)" }}
          />
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={2}
            className="w-full px-4 py-2 rounded-lg text-sm border outline-none resize-y"
            style={{ background: "var(--color-bg-card)", borderColor: "var(--color-border)", color: "var(--color-text)" }}
          />
          <textarea
            value={body}
            onChange={(e) => setBody(e.target.value)}
            rows={20}
            className="w-full px-4 py-3 rounded-lg text-sm font-mono border outline-none resize-y"
            style={{ background: "var(--color-bg-card)", borderColor: "var(--color-border)", color: "var(--color-text)", minHeight: 400 }}
          />
        </div>

        <div className="flex flex-col gap-4">
          <div className="rounded-lg p-4 border flex flex-col gap-3" style={{ background: "var(--color-bg-card)", borderColor: "var(--color-border)" }}>
            <p className="text-xs font-medium uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>Settings</p>
            <select
              value={status}
              onChange={(e) => setStatus(e.target.value)}
              className="w-full px-3 py-2 rounded-lg text-sm border outline-none"
              style={{ background: "var(--color-bg)", borderColor: "var(--color-border)", color: "var(--color-text)" }}
            >
              <option value="draft">Draft</option>
              <option value="published">Published</option>
              <option value="archived">Archived</option>
            </select>
            <input type="text" value={author} onChange={(e) => setAuthor(e.target.value)} placeholder="Author" className="w-full px-3 py-2 rounded-lg text-sm border outline-none" style={{ background: "var(--color-bg)", borderColor: "var(--color-border)", color: "var(--color-text)" }} />
            <input type="text" value={readingTime} onChange={(e) => setReadingTime(e.target.value)} placeholder="Reading time" className="w-full px-3 py-2 rounded-lg text-sm border outline-none" style={{ background: "var(--color-bg)", borderColor: "var(--color-border)", color: "var(--color-text)" }} />
          </div>
          <div className="rounded-lg p-4 border flex flex-col gap-3" style={{ background: "var(--color-bg-card)", borderColor: "var(--color-border)" }}>
            <p className="text-xs font-medium uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>Image</p>
            <input type="text" value={imageUrl} onChange={(e) => setImageUrl(e.target.value)} placeholder="Image URL" className="w-full px-3 py-2 rounded-lg text-sm border outline-none" style={{ background: "var(--color-bg)", borderColor: "var(--color-border)", color: "var(--color-text)" }} />
            <input type="text" value={imageAlt} onChange={(e) => setImageAlt(e.target.value)} placeholder="Alt text" className="w-full px-3 py-2 rounded-lg text-sm border outline-none" style={{ background: "var(--color-bg)", borderColor: "var(--color-border)", color: "var(--color-text)" }} />
          </div>
          <div className="rounded-lg p-4 border flex flex-col gap-3" style={{ background: "var(--color-bg-card)", borderColor: "var(--color-border)" }}>
            <p className="text-xs font-medium uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>SEO</p>
            <input type="text" value={seoTitle} onChange={(e) => setSeoTitle(e.target.value)} placeholder="SEO title" className="w-full px-3 py-2 rounded-lg text-sm border outline-none" style={{ background: "var(--color-bg)", borderColor: "var(--color-border)", color: "var(--color-text)" }} />
            <textarea value={seoDescription} onChange={(e) => setSeoDescription(e.target.value)} placeholder="SEO description" rows={2} className="w-full px-3 py-2 rounded-lg text-sm border outline-none resize-y" style={{ background: "var(--color-bg)", borderColor: "var(--color-border)", color: "var(--color-text)" }} />
          </div>
          <button onClick={handleSave} disabled={saving} className="w-full py-3 rounded-lg text-sm font-medium cursor-pointer transition-opacity disabled:opacity-50" style={{ background: "var(--color-accent)", color: "#fff" }}>
            {saving ? "Saving..." : "Save Changes"}
          </button>
        </div>
      </div>
    </>
  );
}
