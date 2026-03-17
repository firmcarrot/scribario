import Link from "next/link";

export default function NotFound() {
  return (
    <main
      id="main-content"
      data-dark
      className="flex flex-col items-center justify-center px-6 text-center"
      style={{
        backgroundColor: "var(--bg-dark)",
        minHeight: "100vh",
      }}
    >
      <p
        className="font-display font-bold"
        style={{
          fontSize: "clamp(6rem, 15vw, 15rem)",
          lineHeight: 1,
          letterSpacing: "-0.04em",
          backgroundImage: "linear-gradient(135deg, #FF6B4A, #FF8C69)",
          backgroundClip: "text",
          WebkitBackgroundClip: "text",
          WebkitTextFillColor: "transparent",
        }}
      >
        404
      </p>

      <h1
        className="font-display font-bold mt-4"
        style={{
          fontSize: "clamp(1.5rem, 3vw, 3rem)",
          letterSpacing: "-0.02em",
          color: "#fff",
        }}
      >
        This page doesn&apos;t exist.
      </h1>

      <p
        className="font-body mt-4"
        style={{
          fontSize: "clamp(1rem, 1.2vw, 1.2rem)",
          color: "rgba(255,255,255,0.5)",
          maxWidth: "40ch",
          lineHeight: 1.6,
          letterSpacing: "-0.01em",
        }}
      >
        Maybe it moved, maybe it never did. Either way, let&apos;s get you back.
      </p>

      <div className="flex flex-wrap gap-4 mt-8 justify-center">
        <Link
          href="/"
          className="inline-flex items-center font-body font-medium transition-all duration-200 hover:scale-[1.02]"
          style={{
            backgroundColor: "var(--accent)",
            color: "#fff",
            borderRadius: 52,
            padding: "16px 32px",
            fontSize: "1rem",
            letterSpacing: "-0.01em",
            minHeight: 48,
            boxShadow: "0 8px 30px rgba(255, 107, 74, 0.3)",
          }}
        >
          Go home
        </Link>
        <a
          href="https://t.me/ScribarioBot"
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center font-body font-medium transition-all duration-200 hover:scale-[1.02]"
          style={{
            backgroundColor: "rgba(255,255,255,0.06)",
            color: "#fff",
            borderRadius: 52,
            padding: "16px 32px",
            fontSize: "1rem",
            letterSpacing: "-0.01em",
            minHeight: 48,
            border: "1px solid rgba(255,255,255,0.1)",
          }}
        >
          Try Scribario
        </a>
      </div>
    </main>
  );
}
