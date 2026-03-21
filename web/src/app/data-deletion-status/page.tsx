import type { Metadata } from "next";
import { Footer } from "@/components/sections/Footer";

export const metadata: Metadata = {
  title: "Data Deletion Status",
  description: "Check the status of your Scribario data deletion request.",
  robots: "noindex, nofollow",
};

export default async function DataDeletionStatusPage({
  searchParams,
}: {
  searchParams: Promise<{ code?: string }>;
}) {
  const { code } = await searchParams;

  return (
    <>
      <article className="max-w-2xl mx-auto px-6 py-24 md:py-32">
        <h1
          className="font-display font-bold mb-4"
          style={{
            fontSize: "clamp(1.75rem, 3vw, 2.5rem)",
            letterSpacing: "-0.03em",
            color: "var(--text)",
          }}
        >
          Data Deletion Status
        </h1>

        {code ? (
          <div style={{ lineHeight: 1.8, fontSize: "0.95rem", color: "var(--text)" }}>
            <p style={{ marginBottom: "1.5rem" }}>
              <strong>Confirmation code:</strong>{" "}
              <code
                style={{
                  background: "var(--bg-alt)",
                  padding: "4px 8px",
                  borderRadius: 4,
                  fontSize: "0.85rem",
                  fontFamily: "var(--font-mono)",
                }}
              >
                {code}
              </code>
            </p>

            <div
              style={{
                background: "var(--bg-alt)",
                borderRadius: 12,
                padding: "1.5rem",
                marginBottom: "2rem",
              }}
            >
              <p style={{ fontWeight: 600, marginBottom: "0.5rem" }}>
                Status: Processing
              </p>
              <p style={{ color: "var(--text-secondary)" }}>
                Your data deletion request has been received. We will delete all
                personal data associated with your account within 30 days, in
                compliance with GDPR and Meta&apos;s data deletion requirements.
              </p>
            </div>

            <p style={{ color: "var(--text-secondary)", fontSize: "0.9rem" }}>
              Certain data may be retained as required by law (e.g., billing
              records for tax compliance — up to 7 years). All other personal
              data, OAuth tokens, generated content, and account information
              will be permanently deleted.
            </p>

            <p
              style={{
                color: "var(--text-secondary)",
                fontSize: "0.9rem",
                marginTop: "1rem",
              }}
            >
              Questions? Contact us at{" "}
              <a href="mailto:privacy@scribario.com" style={{ color: "var(--accent)" }}>
                privacy@scribario.com
              </a>
            </p>
          </div>
        ) : (
          <div style={{ lineHeight: 1.8, fontSize: "0.95rem", color: "var(--text)" }}>
            <p>
              This page shows the status of data deletion requests. If you
              received a confirmation code when removing Scribario from your
              Facebook or Instagram account, visit this page with your code to
              check the status of your request.
            </p>
            <p style={{ marginTop: "1rem", color: "var(--text-secondary)" }}>
              To request data deletion, you can:
            </p>
            <ul style={{ color: "var(--text-secondary)", paddingLeft: "1.5rem" }}>
              <li>
                Remove Scribario from your{" "}
                <a
                  href="https://www.facebook.com/settings?tab=business_tools"
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{ color: "var(--accent)" }}
                >
                  Facebook Business Integrations
                </a>
              </li>
              <li>
                Email us at{" "}
                <a href="mailto:privacy@scribario.com" style={{ color: "var(--accent)" }}>
                  privacy@scribario.com
                </a>
              </li>
            </ul>
          </div>
        )}
      </article>
      <Footer />
    </>
  );
}
