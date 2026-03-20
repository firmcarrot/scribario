import { ImageResponse } from "next/og";
import { supabase } from "@/lib/supabase";

export const alt = "Scribario Blog";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default async function Image({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const { data: post } = await supabase
    .from("blog_posts")
    .select("title, reading_time")
    .eq("slug", slug)
    .eq("status", "published")
    .single();
  const title = post?.title ?? "Scribario Blog";
  const readTime = post?.reading_time ?? "";

  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          backgroundColor: "#0A0A0F",
          padding: "70px 80px",
          position: "relative",
          overflow: "hidden",
        }}
      >
        {/* Ambient gradient blob */}
        <div
          style={{
            position: "absolute",
            top: "-120px",
            right: "-80px",
            width: "600px",
            height: "600px",
            borderRadius: "50%",
            background: "radial-gradient(circle, rgba(255,107,74,0.15) 0%, transparent 70%)",
          }}
        />
        <div
          style={{
            position: "absolute",
            bottom: "-100px",
            left: "-60px",
            width: "400px",
            height: "400px",
            borderRadius: "50%",
            background: "radial-gradient(circle, rgba(0,136,204,0.08) 0%, transparent 70%)",
          }}
        />

        {/* Top: Logo + Blog label */}
        <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
          <div
            style={{
              width: "44px",
              height: "44px",
              borderRadius: "50%",
              background: "linear-gradient(135deg, #FF6B4A, #E5553A)",
            }}
          />
          <span
            style={{
              fontSize: "26px",
              fontWeight: 700,
              color: "rgba(255,255,255,0.6)",
              letterSpacing: "-0.02em",
            }}
          >
            Scribario
          </span>
          <span
            style={{
              fontSize: "14px",
              fontWeight: 400,
              color: "rgba(255,255,255,0.25)",
              letterSpacing: "0.1em",
              textTransform: "uppercase",
              marginLeft: "8px",
            }}
          >
            Blog
          </span>
        </div>

        {/* Middle: Title */}
        <div style={{ display: "flex", flexDirection: "column", gap: "20px", maxWidth: "900px" }}>
          <h1
            style={{
              fontSize: title.length > 50 ? "52px" : "60px",
              fontWeight: 700,
              lineHeight: 1.1,
              letterSpacing: "-0.03em",
              color: "#fff",
              margin: 0,
            }}
          >
            {title}
          </h1>
        </div>

        {/* Bottom: Reading time + domain */}
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "20px" }}>
            {readTime && (
              <span
                style={{
                  fontSize: "16px",
                  color: "#FF6B4A",
                  letterSpacing: "0.04em",
                }}
              >
                {readTime}
              </span>
            )}
          </div>
          <span
            style={{
              fontSize: "16px",
              color: "rgba(255,255,255,0.2)",
              letterSpacing: "0.02em",
            }}
          >
            scribario.com
          </span>
        </div>
      </div>
    ),
    { ...size }
  );
}
