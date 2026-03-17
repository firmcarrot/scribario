import { Metadata } from "next";
import { notFound } from "next/navigation";
import Link from "next/link";
import { posts } from "@/content/blog/posts";
import { Footer } from "@/components/sections/Footer";

export function generateStaticParams() {
  return posts.map((post) => ({ slug: post.slug }));
}

export function generateMetadata({ params }: { params: { slug: string } }): Metadata {
  const post = posts.find((p) => p.slug === params.slug);
  if (!post) return { title: "Post Not Found" };

  return {
    title: `${post.title} | Scribario Blog`,
    description: post.description,
    alternates: { canonical: `https://scribario.com/blog/${post.slug}` },
    openGraph: {
      title: post.title,
      description: post.description,
      type: "article",
      publishedTime: post.date,
      authors: [post.author],
    },
  };
}

export default function BlogPostPage({ params }: { params: { slug: string } }) {
  const post = posts.find((p) => p.slug === params.slug);
  if (!post) notFound();

  const breadcrumbSchema = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: [
      { "@type": "ListItem", position: 1, name: "Home", item: "https://scribario.com" },
      { "@type": "ListItem", position: 2, name: "Blog", item: "https://scribario.com/blog" },
      { "@type": "ListItem", position: 3, name: post.title, item: `https://scribario.com/blog/${post.slug}` },
    ],
  };

  const articleSchema = {
    "@context": "https://schema.org",
    "@type": "Article",
    headline: post.title,
    description: post.description,
    datePublished: post.date,
    author: { "@type": "Organization", name: "Scribario", url: "https://scribario.com" },
    publisher: { "@type": "Organization", name: "Scribario", url: "https://scribario.com", logo: { "@type": "ImageObject", url: "https://scribario.com/icon-512" } },
    mainEntityOfPage: `https://scribario.com/blog/${post.slug}`,
  };

  return (
    <main id="main-content">
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbSchema) }} />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(articleSchema) }} />
      <article
        className="px-6 md:px-16"
        style={{
          paddingTop: "clamp(10rem, 16vw, 16rem)",
          paddingBottom: "var(--section-gap)",
          maxWidth: "var(--max-content)",
          margin: "0 auto",
        }}
      >
        {/* Breadcrumb */}
        <nav className="mb-8" aria-label="Breadcrumb">
          <ol className="flex items-center gap-2 font-mono" style={{ fontSize: "0.75rem", color: "var(--text-secondary)" }}>
            <li><Link href="/blog" className="hover:text-[var(--accent)] transition-colors">Blog</Link></li>
            <li aria-hidden="true">/</li>
            <li style={{ color: "var(--text)" }}>{post.title}</li>
          </ol>
        </nav>

        {/* Meta */}
        <div className="flex items-center gap-4 mb-6">
          <span
            className="font-mono"
            style={{
              fontSize: "0.75rem",
              letterSpacing: "0.08em",
              color: "var(--text-secondary)",
            }}
          >
            {new Date(post.date).toLocaleDateString("en-US", {
              month: "long",
              day: "numeric",
              year: "numeric",
            })}
          </span>
          <span
            className="font-mono"
            style={{
              fontSize: "0.75rem",
              letterSpacing: "0.08em",
              color: "var(--accent)",
            }}
          >
            {post.readingTime}
          </span>
        </div>

        {/* Title */}
        <h1
          className="font-display font-bold"
          style={{
            fontSize: "clamp(2.5rem, 5vw, 5rem)",
            lineHeight: 1.1,
            letterSpacing: "-0.03em",
            color: "var(--text)",
            marginBottom: "var(--item-gap)",
          }}
        >
          {post.title}
        </h1>

        <p
          className="font-body"
          style={{
            fontSize: "clamp(1.1rem, 1.4vw, 1.4rem)",
            lineHeight: 1.6,
            color: "var(--text-secondary)",
            marginBottom: "var(--content-gap)",
            letterSpacing: "-0.01em",
          }}
        >
          {post.description}
        </p>

        <hr style={{ border: "none", borderTop: "1px solid var(--separator)", marginBottom: "var(--content-gap)" }} />

        {/* Body — rendered as paragraphs with markdown-like h2 support */}
        <div className="blog-body flex flex-col gap-6">
          {post.body.split("\n\n").map((block, i) => {
            const trimmed = block.trim();
            if (!trimmed) return null;

            if (trimmed.startsWith("## ")) {
              return (
                <h2
                  key={i}
                  className="font-display font-bold"
                  style={{
                    fontSize: "clamp(1.5rem, 2.5vw, 2.5rem)",
                    letterSpacing: "-0.02em",
                    color: "var(--text)",
                    marginTop: "var(--item-gap)",
                  }}
                >
                  {trimmed.replace("## ", "")}
                </h2>
              );
            }

            if (trimmed.startsWith("- **")) {
              const items = trimmed.split("\n").filter(Boolean);
              return (
                <ul key={i} className="flex flex-col gap-3" style={{ paddingLeft: "1.5rem" }}>
                  {items.map((item, j) => {
                    const clean = item.replace(/^- /, "");
                    const parts = clean.split("**");
                    return (
                      <li
                        key={j}
                        className="font-body"
                        style={{
                          fontSize: "clamp(1rem, 1.15vw, 1.15rem)",
                          lineHeight: 1.7,
                          color: "var(--text-secondary)",
                          letterSpacing: "-0.01em",
                          listStyleType: "disc",
                        }}
                      >
                        {parts.map((part, k) =>
                          k % 2 === 1 ? (
                            <strong key={k} style={{ color: "var(--text)", fontWeight: 600 }}>
                              {part}
                            </strong>
                          ) : (
                            <span key={k}>{part}</span>
                          )
                        )}
                      </li>
                    );
                  })}
                </ul>
              );
            }

            if (trimmed.startsWith("1. ")) {
              const items = trimmed.split("\n").filter(Boolean);
              return (
                <ol key={i} className="flex flex-col gap-3" style={{ paddingLeft: "1.5rem" }}>
                  {items.map((item, j) => {
                    const clean = item.replace(/^\d+\.\s/, "");
                    const parts = clean.split("**");
                    return (
                      <li
                        key={j}
                        className="font-body"
                        style={{
                          fontSize: "clamp(1rem, 1.15vw, 1.15rem)",
                          lineHeight: 1.7,
                          color: "var(--text-secondary)",
                          letterSpacing: "-0.01em",
                          listStyleType: "decimal",
                        }}
                      >
                        {parts.map((part, k) =>
                          k % 2 === 1 ? (
                            <strong key={k} style={{ color: "var(--text)", fontWeight: 600 }}>
                              {part}
                            </strong>
                          ) : (
                            <span key={k}>{part}</span>
                          )
                        )}
                      </li>
                    );
                  })}
                </ol>
              );
            }

            // Regular paragraph — handle inline **bold**
            const parts = trimmed.split("**");
            return (
              <p
                key={i}
                className="font-body"
                style={{
                  fontSize: "clamp(1rem, 1.15vw, 1.15rem)",
                  lineHeight: 1.8,
                  color: "var(--text-secondary)",
                  letterSpacing: "-0.01em",
                }}
              >
                {parts.map((part, k) =>
                  k % 2 === 1 ? (
                    <strong key={k} style={{ color: "var(--text)", fontWeight: 600 }}>
                      {part}
                    </strong>
                  ) : (
                    <span key={k}>{part}</span>
                  )
                )}
              </p>
            );
          })}
        </div>

        {/* Post CTA */}
        <div
          className="flex flex-col gap-4 mt-16 p-8 rounded-2xl"
          style={{
            backgroundColor: "var(--bg-alt)",
            border: "1px solid rgba(0,0,0,0.06)",
          }}
        >
          <p
            className="font-display font-bold"
            style={{
              fontSize: "clamp(1.25rem, 1.8vw, 1.8rem)",
              letterSpacing: "-0.02em",
              color: "var(--text)",
            }}
          >
            Ready to automate your social media?
          </p>
          <p
            className="font-body"
            style={{
              fontSize: "clamp(0.9rem, 1.05vw, 1.05rem)",
              color: "var(--text-secondary)",
              lineHeight: 1.6,
            }}
          >
            Try Scribario free — text what you want to post, get three options, publish everywhere.
          </p>
          <a
            href="https://t.me/ScribarioBot"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 font-body font-medium transition-all duration-200 hover:scale-[1.02] self-start"
            style={{
              backgroundColor: "var(--accent)",
              color: "#fff",
              borderRadius: 52,
              padding: "14px 28px",
              fontSize: "0.95rem",
              minHeight: 44,
            }}
          >
            Try it free on Telegram
          </a>
        </div>

        {/* Back to blog */}
        <div className="mt-12">
          <Link
            href="/blog"
            className="font-mono transition-colors hover:text-[var(--accent)]"
            style={{
              fontSize: "0.8rem",
              letterSpacing: "0.08em",
              color: "var(--text-secondary)",
            }}
          >
            ← All posts
          </Link>
        </div>
      </article>

      <Footer />
    </main>
  );
}
