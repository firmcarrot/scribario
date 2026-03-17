import type { Metadata } from "next";
import { Footer } from "@/components/sections/Footer";
import { LegalSection as Section } from "@/components/ui/LegalSection";

export const metadata: Metadata = {
  title: "Privacy Policy",
  description: "Scribario Privacy Policy. Learn how we collect, use, and protect your data.",
  alternates: { canonical: "https://scribario.com/privacy" },
};

const breadcrumbSchema = {
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  itemListElement: [
    { "@type": "ListItem", position: 1, name: "Home", item: "https://scribario.com" },
    { "@type": "ListItem", position: 2, name: "Privacy Policy", item: "https://scribario.com/privacy" },
  ],
};

export default function PrivacyPage() {
  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbSchema) }}
      />
      <article className="max-w-3xl mx-auto px-6 py-24 md:py-32">
        <h1
          className="font-display font-bold mb-4"
          style={{ fontSize: "clamp(2rem, 4vw, 3.5rem)", letterSpacing: "-0.0475em", color: "var(--text)" }}
        >
          Privacy Policy
        </h1>
        <p className="mb-12" style={{ color: "var(--text-secondary)", fontSize: "0.95rem" }}>
          Effective Date: March 12, 2026 &middot; Version 1.0
        </p>

        <div className="legal-content" style={{ color: "var(--text)", lineHeight: 1.8, fontSize: "0.95rem" }}>
          <Section title="1. Controller Identity">
            <p>
              Scribario LLC (&quot;we,&quot; &quot;us,&quot; or &quot;our&quot;), located at 1603 Capitol Ave, Suite 310 #1540, Cheyenne, WY 82001, is the data controller responsible for your personal data. For privacy-related inquiries, contact our Data Protection Officer at privacy@scribario.com.
            </p>
          </Section>

          <Section title="2. Data We Collect">
            <table>
              <thead>
                <tr><th>Category</th><th>Data</th></tr>
              </thead>
              <tbody>
                <tr><td>Account</td><td>Name, email address, password hash</td></tr>
                <tr><td>Billing</td><td>Processed via Stripe (see Stripe&apos;s privacy policy)</td></tr>
                <tr><td>Social connections</td><td>OAuth tokens (encrypted at rest), account IDs, page IDs</td></tr>
                <tr><td>Platform data</td><td>Profile information and account details received via API</td></tr>
                <tr><td>User uploads</td><td>Brand guidelines, reference images, text prompts</td></tr>
                <tr><td>AI interactions</td><td>Prompts sent to AI providers, generated outputs (text, images, videos, audio), approval/rejection signals</td></tr>
                <tr><td>Usage &amp; technical</td><td>IP address, device type, feature usage, Telegram user ID</td></tr>
              </tbody>
            </table>
          </Section>

          <Section title="3. How We Use Your Data">
            <p>We process your data on the following legal bases (GDPR):</p>
            <ul>
              <li><strong>Contract performance:</strong> Content generation, posting, OAuth management — necessary to provide the Service</li>
              <li><strong>Legitimate interests:</strong> Analytics, fraud prevention, service improvement</li>
              <li><strong>Legal obligation:</strong> Tax records, lawful government requests</li>
              <li><strong>Consent:</strong> Marketing emails (opt-in only)</li>
            </ul>
            <p>
              <strong>We do not sell your personal data.</strong> We do not use your content to train AI models. Anthropic&apos;s API terms confirm that API inputs are not used for model training by default.
            </p>
          </Section>

          <Section title="4. Data Sharing & Subprocessors">
            <p>We share data with the following service providers to operate the Service:</p>
            <table>
              <thead>
                <tr><th>Subprocessor</th><th>Data Received</th><th>Purpose</th></tr>
              </thead>
              <tbody>
                <tr><td>Anthropic (Claude)</td><td>Text prompts, brand data</td><td>Caption and script generation</td></tr>
                <tr><td>Kie.ai</td><td>Image prompts</td><td>Image generation</td></tr>
                <tr><td>ElevenLabs</td><td>Text scripts</td><td>Voice synthesis for video</td></tr>
                <tr><td>Supabase</td><td>All stored data</td><td>Database hosting</td></tr>
                <tr><td>Vercel</td><td>Static assets</td><td>Website hosting</td></tr>
                <tr><td>Stripe</td><td>Billing data</td><td>Payment processing</td></tr>
                <tr><td>Meta, TikTok, LinkedIn, Bluesky, YouTube, Pinterest, X</td><td>Post content</td><td>Publishing via API</td></tr>
              </tbody>
            </table>
          </Section>

          <Section title="5. Data Retention">
            <ul>
              <li>Account data: duration of your account plus 90 days</li>
              <li>Billing records: 7 years (tax compliance)</li>
              <li>LinkedIn profile data: maximum 24 hours</li>
              <li>LinkedIn social activity data: maximum 48 hours</li>
              <li>AI-generated content: retained while your account is active</li>
            </ul>
          </Section>

          <Section title="6. Data Deletion">
            <p>
              You may request deletion of your data at any time by emailing privacy@scribario.com or using the in-app deletion feature.
            </p>
            <p>
              We comply with Meta&apos;s Data Deletion Callback requirement — when you remove Scribario from your Meta account, we automatically receive and process the deletion request.
            </p>
            <p>
              Deletion timeline: 30 days (GDPR), 45 days (CCPA). Some data may be retained in anonymized form for aggregate analytics, and billing records are retained for 7 years per tax law.
            </p>
          </Section>

          <Section title="7. Your Rights">
            <h4>GDPR Rights (EU/EEA/UK residents)</h4>
            <p>You have the right to: access, rectify, erase, restrict processing, data portability, and object to processing of your personal data.</p>
            <h4>CCPA Rights (California residents)</h4>
            <p>You have the right to: know what data we collect, request deletion, opt out of sale (we do not sell data), request correction, and non-discrimination for exercising your rights.</p>
            <p>To exercise any of these rights, contact privacy@scribario.com. We will respond within 30 days (GDPR) or 45 days (CCPA).</p>
          </Section>

          <Section title="8. Security">
            <p>
              We protect your data using encryption in transit (TLS) and at rest (particularly OAuth tokens). We implement access controls and follow security best practices. In the event of a data breach, we will notify the relevant supervisory authority within 72 hours as required by GDPR.
            </p>
            <p>
              No method of electronic transmission or storage is 100% secure. We cannot guarantee absolute security.
            </p>
          </Section>

          <Section title="9. International Data Transfers">
            <p>
              Our servers are located in the United States. If you are located outside the US, your data will be transferred to the US for processing. We rely on the EU-U.S. Data Privacy Framework and/or Standard Contractual Clauses to ensure adequate protection for international transfers.
            </p>
          </Section>

          <Section title="10. Cookies">
            <p>
              We use essential cookies for session management and authentication. We may use analytics cookies to understand how the Service is used. EU users will be presented with a cookie consent mechanism for non-essential cookies.
            </p>
          </Section>

          <Section title="11. Children's Privacy">
            <p>
              The Service is not directed to individuals under 18 years of age. We do not knowingly collect personal data from minors. If we discover that we have inadvertently collected data from a minor, we will delete it immediately.
            </p>
          </Section>

          <Section title="12. AI-Specific Disclosures">
            <p>
              Scribario uses Anthropic&apos;s Claude for text and script generation, Kie.ai for image generation, and ElevenLabs for voice synthesis in video content. Your prompts sent via these APIs are not used to train AI models (per each provider&apos;s API terms). AI-generated content may not be copyrightable under current law. We comply with the EU AI Act Article 50 transparency requirements.
            </p>
          </Section>

          <Section title="13. Bluesky / AT Protocol Disclosures">
            <p>
              Content posted to Bluesky is public and may be replicated across servers within the AT Protocol network. Deletion of content on the decentralized network is not guaranteed, as other servers may retain copies.
            </p>
          </Section>

          <Section title="14. Changes to This Policy">
            <p>
              We will provide 30 days notice for material changes to this Privacy Policy via email. We retain historical versions of this policy as required by Meta.
            </p>
          </Section>

          <Section title="15. Contact">
            <p>
              For privacy-related questions or to exercise your rights:<br />
              Scribario LLC<br />
              1603 Capitol Ave, Suite 310 #1540, Cheyenne, WY 82001<br />
              Email: privacy@scribario.com<br />
              <br />
              EU residents have the right to lodge a complaint with their local supervisory authority.
            </p>
          </Section>
        </div>
      </article>
      <Footer />
    </>
  );
}

