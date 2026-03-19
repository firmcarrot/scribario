"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { saveBlogPost } from "../actions";

function slugify(text: string) {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/(^-|-$)/g, "");
}

export default function NewPostPage() {
  const router = useRouter();
  const [saving, setSaving] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState("");
  const [keyword, setKeyword] = useState("");

  const [title, setTitle] = useState("");
  const [slug, setSlug] = useState("");
  const [description, setDescription] = useState("");
  const [body, setBody] = useState("");
  const [author, setAuthor] = useState("Scribario Team");
  const [readingTime, setReadingTime] = useState("");
  const [imageUrl, setImageUrl] = useState("");
  const [imageAlt, setImageAlt] = useState("");
  const [seoTitle, setSeoTitle] = useState("");
  const [seoDescription, setSeoDescription] = useState("");
  const [status, setStatus] = useState<"draft" | "published">("draft");

  const handleTitleChange = (val: string) => {
    setTitle(val);
    if (!slug || slug === slugify(title)) {
      setSlug(slugify(val));
    }
  };

  const handleGenerate = async () => {
    if (!keyword.trim()) {
      setError("Enter a target keyword to generate a post.");
      return;
    }
    setGenerating(true);
    setError("");

    try {
      const res = await fetch("/api/generate-blog", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ keyword: keyword.trim() }),
      });
      const data = await res.json();
      if (!res.ok) {
        setError(data.error || "Generation failed");
        setGenerating(false);
        return;
      }
      setTitle(data.title || "");
      setSlug(data.slug || slugify(data.title || ""));
      setDescription(data.description || "");
      setBody(data.body || "");
      setReadingTime(data.readingTime ? `${data.readingTime} min read` : "");
      setSeoDescription(data.description || "");
    } catch (err) {
      setError("Failed to connect to generation API");
    }
    setGenerating(false);
  };

  const handleSave = async () => {
    if (!title.trim() || !slug.trim()) {
      setError("Title and slug are required.");
      return;
    }

    setSaving(true);
    setError("");

    const result = await saveBlogPost({
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
      status,
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
    <div className="flex flex-col gap-6 max-w-4xl">
      <h1 className="text-2xl font-bold">New Post</h1>

      {error && (
        <div className="p-3 rounded-lg text-sm" style={{ background: "var(--color-danger)", color: "#fff" }}>
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main editor */}
        <div className="lg:col-span-2 flex flex-col gap-4">
          {/* AI Generation */}
          <div
            className="rounded-lg p-4 border flex gap-3 items-end"
            style={{ background: "var(--color-bg-card)", borderColor: "var(--color-border)" }}
          >
            <div className="flex-1">
              <label className="text-xs font-medium uppercase tracking-wider mb-1 block" style={{ color: "var(--color-text-muted)" }}>
                Generate with AI
              </label>
              <input
                type="text"
                placeholder="Target keyword (e.g. 'social media automation')"
                value={keyword}
                onChange={(e) => setKeyword(e.target.value)}
                className="w-full px-3 py-2 rounded-lg text-sm border outline-none"
                style={{ background: "var(--color-bg)", borderColor: "var(--color-border)", color: "var(--color-text)" }}
              />
            </div>
            <button
              onClick={handleGenerate}
              disabled={generating}
              className="px-4 py-2 rounded-lg text-sm font-medium cursor-pointer transition-opacity disabled:opacity-50 whitespace-nowrap"
              style={{ background: "var(--color-accent)", color: "#fff" }}
            >
              {generating ? "Generating..." : "Generate"}
            </button>
          </div>

          <input
            type="text"
            placeholder="Post title"
            value={title}
            onChange={(e) => handleTitleChange(e.target.value)}
            className="w-full px-4 py-3 rounded-lg text-lg font-bold border outline-none"
            style={{ background: "var(--color-bg-card)", borderColor: "var(--color-border)", color: "var(--color-text)" }}
          />

          <input
            type="text"
            placeholder="slug-goes-here"
            value={slug}
            onChange={(e) => setSlug(e.target.value)}
            className="w-full px-4 py-2 rounded-lg text-sm font-mono border outline-none"
            style={{ background: "var(--color-bg-card)", borderColor: "var(--color-border)", color: "var(--color-text-muted)" }}
          />

          <textarea
            placeholder="Short description..."
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={2}
            className="w-full px-4 py-2 rounded-lg text-sm border outline-none resize-y"
            style={{ background: "var(--color-bg-card)", borderColor: "var(--color-border)", color: "var(--color-text)" }}
          />

          <textarea
            placeholder="Write your post in Markdown..."
            value={body}
            onChange={(e) => setBody(e.target.value)}
            rows={20}
            className="w-full px-4 py-3 rounded-lg text-sm font-mono border outline-none resize-y"
            style={{ background: "var(--color-bg-card)", borderColor: "var(--color-border)", color: "var(--color-text)", minHeight: 400 }}
          />
        </div>

        {/* Side panel */}
        <div className="flex flex-col gap-4">
          <div
            className="rounded-lg p-4 border flex flex-col gap-3"
            style={{ background: "var(--color-bg-card)", borderColor: "var(--color-border)" }}
          >
            <p className="text-xs font-medium uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>
              Publish Settings
            </p>

            <select
              value={status}
              onChange={(e) => setStatus(e.target.value as "draft" | "published")}
              className="w-full px-3 py-2 rounded-lg text-sm border outline-none"
              style={{ background: "var(--color-bg)", borderColor: "var(--color-border)", color: "var(--color-text)" }}
            >
              <option value="draft">Draft</option>
              <option value="published">Published</option>
            </select>

            <input
              type="text"
              placeholder="Author"
              value={author}
              onChange={(e) => setAuthor(e.target.value)}
              className="w-full px-3 py-2 rounded-lg text-sm border outline-none"
              style={{ background: "var(--color-bg)", borderColor: "var(--color-border)", color: "var(--color-text)" }}
            />

            <input
              type="text"
              placeholder="Reading time (e.g. 5 min read)"
              value={readingTime}
              onChange={(e) => setReadingTime(e.target.value)}
              className="w-full px-3 py-2 rounded-lg text-sm border outline-none"
              style={{ background: "var(--color-bg)", borderColor: "var(--color-border)", color: "var(--color-text)" }}
            />
          </div>

          <div
            className="rounded-lg p-4 border flex flex-col gap-3"
            style={{ background: "var(--color-bg-card)", borderColor: "var(--color-border)" }}
          >
            <p className="text-xs font-medium uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>
              Image
            </p>
            <input
              type="text"
              placeholder="Image URL"
              value={imageUrl}
              onChange={(e) => setImageUrl(e.target.value)}
              className="w-full px-3 py-2 rounded-lg text-sm border outline-none"
              style={{ background: "var(--color-bg)", borderColor: "var(--color-border)", color: "var(--color-text)" }}
            />
            <input
              type="text"
              placeholder="Image alt text"
              value={imageAlt}
              onChange={(e) => setImageAlt(e.target.value)}
              className="w-full px-3 py-2 rounded-lg text-sm border outline-none"
              style={{ background: "var(--color-bg)", borderColor: "var(--color-border)", color: "var(--color-text)" }}
            />
          </div>

          <div
            className="rounded-lg p-4 border flex flex-col gap-3"
            style={{ background: "var(--color-bg-card)", borderColor: "var(--color-border)" }}
          >
            <p className="text-xs font-medium uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>
              SEO
            </p>
            <input
              type="text"
              placeholder="SEO title (optional)"
              value={seoTitle}
              onChange={(e) => setSeoTitle(e.target.value)}
              className="w-full px-3 py-2 rounded-lg text-sm border outline-none"
              style={{ background: "var(--color-bg)", borderColor: "var(--color-border)", color: "var(--color-text)" }}
            />
            <textarea
              placeholder="SEO description (optional)"
              value={seoDescription}
              onChange={(e) => setSeoDescription(e.target.value)}
              rows={2}
              className="w-full px-3 py-2 rounded-lg text-sm border outline-none resize-y"
              style={{ background: "var(--color-bg)", borderColor: "var(--color-border)", color: "var(--color-text)" }}
            />
          </div>

          <button
            onClick={handleSave}
            disabled={saving}
            className="w-full py-3 rounded-lg text-sm font-medium cursor-pointer transition-opacity disabled:opacity-50"
            style={{ background: "var(--color-accent)", color: "#fff" }}
          >
            {saving ? "Saving..." : status === "published" ? "Publish" : "Save Draft"}
          </button>
        </div>
      </div>
    </div>
  );
}
