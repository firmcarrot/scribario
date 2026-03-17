import { Metadata } from "next";
import Link from "next/link";
import { posts } from "@/content/blog/posts";
import { Footer } from "@/components/sections/Footer";

export const metadata: Metadata = {
  title: "Blog — Social Media Tips & AI Automation | Scribario",
  description:
    "Tips, strategies, and insights on AI-powered social media automation for small businesses.",
  alternates: { canonical: "https://scribario.com/blog" },
};

export default function BlogPage() {
  return (
    <main id="main-content">
      <section
        className="px-6 md:px-16"
        style={{ paddingTop: "clamp(10rem, 16vw, 16rem)", paddingBottom: "var(--section-gap)" }}
      >
        <p
          className="font-mono"
          style={{
            fontSize: "0.75rem",
            letterSpacing: "0.1em",
            textTransform: "uppercase",
            color: "var(--text-secondary)",
            marginBottom: "clamp(1.5rem, 2vw, 2rem)",
          }}
        >
          Blog
        </p>

        <h1
          className="font-display font-bold"
          style={{
            fontSize: "clamp(3rem, 6vw, 6rem)",
            lineHeight: 1.04,
            letterSpacing: "-0.03em",
            color: "var(--text)",
            maxWidth: "18ch",
          }}
        >
          Ideas &{" "}
          <span
            style={{
              backgroundImage: "linear-gradient(135deg, #FF6B4A, #FF8C69)",
              backgroundClip: "text",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
            }}
          >
            insights.
          </span>
        </h1>

        <p
          className="font-body"
          style={{
            fontSize: "clamp(1.1rem, 1.5vw, 1.5rem)",
            lineHeight: 1.5,
            color: "var(--text-secondary)",
            maxWidth: "50ch",
            marginTop: "var(--item-gap)",
            letterSpacing: "-0.01em",
          }}
        >
          Social media tips, AI automation strategies, and lessons from building Scribario.
        </p>
      </section>

      {/* Post Grid */}
      <section
        className="px-6 md:px-16"
        style={{ paddingBottom: "var(--section-gap)" }}
      >
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {posts.map((post) => (
            <Link
              key={post.slug}
              href={`/blog/${post.slug}`}
              className="group flex flex-col gap-4 transition-all duration-200 hover:scale-[1.01]"
              style={{
                padding: "clamp(1.5rem, 2.5vw, 2.5rem)",
                borderRadius: 20,
                border: "1px solid rgba(0,0,0,0.06)",
              }}
            >
              <div className="flex items-center gap-3">
                <span
                  className="font-mono"
                  style={{
                    fontSize: "0.7rem",
                    letterSpacing: "0.08em",
                    color: "var(--text-secondary)",
                  }}
                >
                  {new Date(post.date).toLocaleDateString("en-US", {
                    month: "short",
                    day: "numeric",
                    year: "numeric",
                  })}
                </span>
                <span
                  className="font-mono"
                  style={{
                    fontSize: "0.7rem",
                    letterSpacing: "0.08em",
                    color: "var(--accent)",
                  }}
                >
                  {post.readingTime}
                </span>
              </div>

              <h2
                className="font-display font-bold group-hover:text-[var(--accent)] transition-colors duration-200"
                style={{
                  fontSize: "clamp(1.25rem, 1.8vw, 1.8rem)",
                  letterSpacing: "-0.02em",
                  color: "var(--text)",
                  lineHeight: 1.2,
                }}
              >
                {post.title}
              </h2>

              <p
                className="font-body"
                style={{
                  fontSize: "clamp(0.9rem, 1vw, 1rem)",
                  lineHeight: 1.6,
                  color: "var(--text-secondary)",
                  letterSpacing: "-0.01em",
                }}
              >
                {post.description}
              </p>
            </Link>
          ))}
        </div>

        {posts.length === 0 && (
          <p
            className="font-body text-center"
            style={{
              fontSize: "1.1rem",
              color: "var(--text-secondary)",
              padding: "4rem 0",
            }}
          >
            Posts coming soon.
          </p>
        )}
      </section>

      <Footer />
    </main>
  );
}
