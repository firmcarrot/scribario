import { ImageResponse } from "next/og";

export const runtime = "edge";
export const alt = "Scribario — Your social media team in a text";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default async function Image() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "flex-start",
          backgroundColor: "#1A1A2E",
          padding: "80px",
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "16px",
            marginBottom: "40px",
          }}
        >
          <div
            style={{
              width: "48px",
              height: "48px",
              borderRadius: "50%",
              background: "linear-gradient(135deg, #FF6B4A, #E5553A)",
            }}
          />
          <span
            style={{
              fontSize: "28px",
              fontWeight: 700,
              color: "rgba(255,255,255,0.7)",
              letterSpacing: "-0.02em",
            }}
          >
            Scribario
          </span>
        </div>

        <h1
          style={{
            fontSize: "72px",
            fontWeight: 700,
            lineHeight: 1.05,
            letterSpacing: "-0.04em",
            color: "#fff",
            margin: 0,
            maxWidth: "800px",
          }}
        >
          Your social media team in{" "}
          <span style={{ color: "#FF6B4A" }}>a text.</span>
        </h1>

        <p
          style={{
            fontSize: "24px",
            color: "rgba(255,255,255,0.5)",
            marginTop: "32px",
            letterSpacing: "-0.02em",
            maxWidth: "600px",
            lineHeight: 1.5,
          }}
        >
          Text what you want. AI creates 3 options. One tap publishes to Facebook.
        </p>

        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "12px",
            marginTop: "48px",
            padding: "14px 28px",
            borderRadius: "52px",
            background: "#FF6B4A",
          }}
        >
          <span
            style={{
              fontSize: "18px",
              fontWeight: 500,
              color: "#fff",
              letterSpacing: "-0.01em",
            }}
          >
            Try it free on Telegram
          </span>
        </div>
      </div>
    ),
    { ...size }
  );
}
