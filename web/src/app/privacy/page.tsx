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
          Effective Date: March 21, 2026 &middot; Version 1.1
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
                <tr><td>Google (YouTube API Services)</td><td>Video content, channel metadata</td><td>Video publishing via YouTube API</td></tr>
                <tr><td>Supabase</td><td>All stored data</td><td>Database hosting</td></tr>
                <tr><td>Vercel</td><td>Static assets</td><td>Website hosting</td></tr>
                <tr><td>Stripe</td><td>Billing data</td><td>Payment processing</td></tr>
                <tr><td>Meta (Facebook, Instagram)</td><td>Post content, page data</td><td>Publishing via Meta Graph API</td></tr>
                <tr><td>TikTok</td><td>Video and post content</td><td>Publishing via TikTok Content Posting API</td></tr>
                <tr><td>LinkedIn</td><td>Post content, profile data</td><td>Publishing via LinkedIn Marketing API</td></tr>
                <tr><td>X (formerly Twitter)</td><td>Post content</td><td>Publishing via X API</td></tr>
                <tr><td>Pinterest</td><td>Pin content, images</td><td>Publishing via Pinterest API</td></tr>
                <tr><td>Bluesky</td><td>Post content</td><td>Publishing via AT Protocol</td></tr>
              </tbody>
            </table>
            <p>
              Scribario&apos;s use and transfer to any other app of information received from Google APIs will adhere to the <a href="https://developers.google.com/terms/api-services-user-data-policy" target="_blank" rel="noopener noreferrer">Google API Services User Data Policy</a>, including the Limited Use requirements. Your use of YouTube features is also subject to <a href="https://policies.google.com/privacy" target="_blank" rel="noopener noreferrer">Google&apos;s Privacy Policy</a>.
            </p>
          </Section>

          <Section title="5. Data Retention">
            <ul>
              <li>Account data: duration of your account plus 90 days</li>
              <li>Billing records: 7 years (tax compliance)</li>
              <li>LinkedIn profile data: maximum 24 hours</li>
              <li>LinkedIn social activity data: maximum 48 hours</li>
              <li>YouTube/Google API data: retained only as long as necessary to provide the Service; deleted within 30 days of account deletion or access revocation</li>
              <li>AI-generated content: retained while your account is active</li>
              <li>OAuth tokens: deleted immediately upon disconnection or account deletion</li>
            </ul>
          </Section>

          <Section title="6. Data Deletion">
            <p>
              You may request deletion of your data at any time by emailing privacy@scribario.com or using the in-app deletion feature.
            </p>
            <h4>Meta (Facebook/Instagram) Data Deletion</h4>
            <p>
              We comply with Meta&apos;s Data Deletion Callback requirement. When you remove Scribario from your Meta account settings, Meta sends us an automated deletion request. We process the request, delete all associated data, and provide you with a confirmation code and a status URL at <code>https://scribario.com/data-deletion-status</code> where you can verify deletion progress.
            </p>
            <h4>YouTube/Google Data Deletion</h4>
            <p>
              You may revoke Scribario&apos;s access to your YouTube data at any time via <a href="https://myaccount.google.com/permissions" target="_blank" rel="noopener noreferrer">Google&apos;s security settings</a>. Upon revocation, we delete all YouTube API data within 30 days.
            </p>
            <h4>Deletion Timeline</h4>
            <p>
              GDPR: 30 days. CCPA: 45 days. Some data may be retained in anonymized form for aggregate analytics, and billing records are retained for 7 years per tax law.
            </p>
          </Section>

          <Section title="7. Your Rights">
            <h4>GDPR Rights (EU/EEA/UK residents)</h4>
            <p>You have the right to: access, rectify, erase, restrict processing, data portability, and object to processing of your personal data.</p>
            <h4>CCPA Rights (California residents)</h4>
            <p>You have the right to: know what data we collect, request deletion, opt out of sale (we do not sell data), request correction, and non-discrimination for exercising your rights.</p>
            <p>To exercise any of these rights, contact privacy@scribario.com. We will respond within 30 days (GDPR) or 45 days (CCPA).</p>
          </Section>

          <Section title="8. How to Revoke Platform Access">
            <p>You can disconnect Scribario from any connected platform at any time. Upon disconnection, we delete the associated OAuth tokens immediately.</p>
            <ul>
              <li><strong>Facebook/Instagram:</strong> Go to <a href="https://www.facebook.com/settings?tab=business_tools" target="_blank" rel="noopener noreferrer">Facebook Settings → Business Integrations</a> → find Scribario → Remove</li>
              <li><strong>YouTube/Google:</strong> Go to <a href="https://myaccount.google.com/permissions" target="_blank" rel="noopener noreferrer">Google Account → Security → Third-party apps</a> → find Scribario → Remove Access</li>
              <li><strong>TikTok:</strong> Go to TikTok → Settings → Security → Manage App Permissions → find Scribario → Revoke</li>
              <li><strong>LinkedIn:</strong> Go to <a href="https://www.linkedin.com/psettings/permitted-services" target="_blank" rel="noopener noreferrer">LinkedIn Settings → Data Privacy → Permitted Services</a> → find Scribario → Remove</li>
              <li><strong>X (Twitter):</strong> Go to <a href="https://twitter.com/settings/connected_apps" target="_blank" rel="noopener noreferrer">X Settings → Security → Connected Apps</a> → find Scribario → Revoke Access</li>
              <li><strong>Pinterest:</strong> Go to Pinterest → Settings → Security → Apps → find Scribario → Remove</li>
              <li><strong>Bluesky:</strong> Go to Bluesky → Settings → App Passwords → revoke the password used for Scribario</li>
            </ul>
          </Section>

          <Section title="9. Security">
            <p>
              We protect your data using encryption in transit (TLS) and at rest (particularly OAuth tokens). We implement access controls and follow security best practices. In the event of a data breach, we will notify the relevant supervisory authority within 72 hours as required by GDPR.
            </p>
            <p>
              No method of electronic transmission or storage is 100% secure. We cannot guarantee absolute security.
            </p>
          </Section>

          <Section title="10. International Data Transfers">
            <p>
              Our servers are located in the United States. If you are located outside the US, your data will be transferred to the US for processing. We rely on the EU-U.S. Data Privacy Framework and/or Standard Contractual Clauses to ensure adequate protection for international transfers.
            </p>
          </Section>

          <Section title="11. Cookies">
            <p>
              We use only essential cookies required for the Service to function (session management, authentication). We do not use tracking cookies, advertising cookies, or third-party analytics cookies. Because we use only strictly necessary cookies, no consent banner is required under GDPR.
            </p>
          </Section>

          <Section title="12. Children&apos;s Privacy">
            <p>
              The Service is not directed to individuals under 18 years of age. We do not knowingly collect personal data from minors. If we discover that we have inadvertently collected data from a minor, we will delete it immediately.
            </p>
          </Section>

          <Section title="13. AI-Specific Disclosures">
            <p>
              Scribario uses Anthropic&apos;s Claude for text and script generation, Kie.ai for image generation, and ElevenLabs for voice synthesis in video content. Your prompts sent via these APIs are not used to train AI models (per each provider&apos;s API terms). AI-generated content may not be copyrightable under current law. We comply with the EU AI Act Article 50 transparency requirements.
            </p>
          </Section>

          <Section title="14. Bluesky / AT Protocol Disclosures">
            <p>
              Content posted to Bluesky is public and may be replicated across servers within the AT Protocol network. Deletion of content on the decentralized network is not guaranteed, as other servers may retain copies.
            </p>
          </Section>

          <Section title="15. YouTube API Services Disclosures">
            <p>
              Scribario uses <a href="https://developers.google.com/youtube/terms/api-services-terms-of-service" target="_blank" rel="noopener noreferrer">YouTube API Services</a> to publish video content to YouTube on your behalf. By using Scribario&apos;s YouTube integration, you agree to be bound by the <a href="https://www.youtube.com/t/terms" target="_blank" rel="noopener noreferrer">YouTube Terms of Service</a>. Your data obtained through YouTube API Services is subject to <a href="https://policies.google.com/privacy" target="_blank" rel="noopener noreferrer">Google&apos;s Privacy Policy</a>.
            </p>
            <p>
              We access only the YouTube API scopes necessary to upload videos and manage your channel content. We do not access your viewing history, subscriptions, or personal YouTube data beyond what is required for publishing. You may revoke access at any time via <a href="https://myaccount.google.com/permissions" target="_blank" rel="noopener noreferrer">Google&apos;s security settings</a>, and we will delete all associated data within 30 days.
            </p>
          </Section>

          <Section title="16. Changes to This Policy">
            <p>
              We will provide 30 days notice for material changes to this Privacy Policy via email. We retain historical versions of this policy as required by Meta.
            </p>
          </Section>

          <Section title="17. Contact">
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

