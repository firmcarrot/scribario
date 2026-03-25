import type { Metadata } from "next";
import { Footer } from "@/components/sections/Footer";
import { LegalSection as Section } from "@/components/ui/LegalSection";

export const metadata: Metadata = {
  title: "Terms of Service",
  description: "Scribario Terms of Service. Read our terms and conditions for using the Scribario social media automation platform.",
  alternates: { canonical: "https://scribario.com/terms" },
};

const breadcrumbSchema = {
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  itemListElement: [
    { "@type": "ListItem", position: 1, name: "Home", item: "https://scribario.com" },
    { "@type": "ListItem", position: 2, name: "Terms of Service", item: "https://scribario.com/terms" },
  ],
};

export default function TermsPage() {
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
          Terms of Service
        </h1>
        <p className="mb-12" style={{ color: "var(--text-secondary)", fontSize: "0.95rem" }}>
          Effective Date: March 21, 2026 &middot; Version 1.1
        </p>

        <div className="legal-content" style={{ color: "var(--text)", lineHeight: 1.8, fontSize: "0.95rem" }}>
          <Section title="1. Introduction & Acceptance">
            <p>
              Welcome to Scribario (&quot;we,&quot; &quot;us,&quot; or &quot;our&quot;), a social media automation platform operated by DarkArc Technologies LLC, a Wyoming limited liability company. These Terms of Service (&quot;Terms&quot;) govern your access to and use of the Scribario platform, including our Telegram bot, web application, and all related services (collectively, the &quot;Service&quot;).
            </p>
            <p>
              By creating an account, accessing, or using the Service, you agree to be bound by these Terms. If you do not agree, do not use the Service. Your continued use of the Service after any modifications to these Terms constitutes acceptance of those changes.
            </p>
            <p>
              You must be at least 18 years old to use the Service.
            </p>
          </Section>

          <Section title="2. Description of Service">
            <p>Scribario provides:</p>
            <ul>
              <li>AI-powered content generation (captions, images, and videos) for social media</li>
              <li>AI-generated short-form video creation with voiceover, sound effects, and music</li>
              <li>OAuth-based connection to your social media accounts (Facebook, Instagram, LinkedIn, TikTok, Bluesky, YouTube, Pinterest, X)</li>
              <li>Automated posting to connected platforms on your behalf</li>
              <li>Scheduled posting and content management</li>
            </ul>
            <p>
              <strong>AI Disclosure:</strong> Scribario uses artificial intelligence for text generation, image generation, and voice synthesis to create content. All content is AI-generated and should be reviewed before publishing.
            </p>
          </Section>

          <Section title="3. Account Registration & Security">
            <p>
              You are responsible for maintaining the confidentiality of your account credentials. You may not share your account with others. You must provide accurate information during registration. You must notify us immediately if you believe your account has been compromised.
            </p>
          </Section>

          <Section title="4. Authorized Use & Prohibited Conduct">
            <p>You agree to:</p>
            <ul>
              <li>Comply with the terms of service of each connected social media platform</li>
              <li>Not use the Service for spam, inauthentic behavior, or coordinated manipulation</li>
              <li>Not create deceptive AI-generated content or impersonate others</li>
              <li>Not infringe on intellectual property rights</li>
              <li>Not use the Service for any illegal purpose</li>
              <li>Not reverse-engineer, decompile, or attempt to extract OAuth tokens or API credentials</li>
              <li>Not use the Service for surveillance, tracking, or monitoring of individuals</li>
            </ul>
            <h4>Platform-Specific Rules</h4>
            <p>When posting via Scribario, you must also comply with each platform&apos;s specific policies:</p>
            <ul>
              <li><strong>X (Twitter):</strong> You must comply with X&apos;s <a href="https://developer.x.com/en/developer-terms/policy" target="_blank" rel="noopener noreferrer">Automation Rules</a>. Automated posts must not be duplicative, must not target users without consent, and must not be used for coordinated inauthentic activity.</li>
              <li><strong>TikTok:</strong> All AI-generated content must be disclosed using TikTok&apos;s labeling tools.</li>
              <li><strong>LinkedIn:</strong> Posts must comply with LinkedIn&apos;s <a href="https://www.linkedin.com/legal/l/marketing-api-terms" target="_blank" rel="noopener noreferrer">Marketing API Terms</a>. Content must be professional and not misleading.</li>
              <li><strong>YouTube:</strong> Uploaded content must comply with YouTube&apos;s <a href="https://www.youtube.com/howyoutubeworks/policies/community-guidelines/" target="_blank" rel="noopener noreferrer">Community Guidelines</a>.</li>
            </ul>
          </Section>

          <Section title="5. Third-Party Platform Connections (OAuth)">
            <p>
              Scribario connects to your social media accounts via OAuth, an industry-standard authorization protocol. When you connect a platform, you grant permission directly to that platform — Scribario never sees or stores your platform passwords. We request only the minimum permissions necessary to provide the Service.
            </p>
            <p>
              You can revoke Scribario&apos;s access at any time via each platform&apos;s settings (see our <a href="/privacy#revoke">Privacy Policy Section 8</a> for detailed instructions per platform). Scribario is not affiliated with or endorsed by Meta, Google, LinkedIn, TikTok, Bluesky, Pinterest, X, or any other connected platform. These platforms may change their APIs at any time, which may affect service availability.
            </p>
            <p>
              By using Scribario&apos;s YouTube integration, you also agree to the <a href="https://www.youtube.com/t/terms" target="_blank" rel="noopener noreferrer">YouTube Terms of Service</a> and acknowledge that your data is subject to <a href="https://policies.google.com/privacy" target="_blank" rel="noopener noreferrer">Google&apos;s Privacy Policy</a>.
            </p>
          </Section>

          <Section title="6. AI-Generated Content">
            <h4>6a. Content Ownership</h4>
            <p>
              AI-generated outputs may not be copyrightable under current U.S. Copyright Office guidance. We grant you a broad license to use all content generated through the Service. Note that other users may receive similar outputs from similar prompts. Third-party IP terms from our AI providers apply to generated content.
            </p>
            <h4>6b. Accuracy & Liability</h4>
            <p>
              AI content may be inaccurate, misleading, or inappropriate. You are solely responsible for reviewing all generated content before posting. We make no warranty that generated content complies with any platform&apos;s advertising standards or legal requirements. We are not liable for any brand damage resulting from AI-generated content.
            </p>
            <h4>6c. AI Disclosure Obligations</h4>
            <p>
              Various platforms and jurisdictions require disclosure of AI-generated content. You are responsible for complying with all applicable AI labeling requirements, including but not limited to:
            </p>
            <ul>
              <li><strong>TikTok:</strong> AI-generated content (AITGC) must be labeled using TikTok&apos;s synthetic media disclosure tools. Failure to label may result in content removal.</li>
              <li><strong>Meta (Facebook/Instagram):</strong> AI-generated content used in ads must be labeled per Meta&apos;s AI content labeling policy.</li>
              <li><strong>YouTube:</strong> Altered or synthetic content that could be mistaken for real must be disclosed per YouTube&apos;s policies.</li>
              <li><strong>EU AI Act Article 50:</strong> Content generated by AI systems must be labeled as such (effective August 2026).</li>
            </ul>
          </Section>

          <Section title="7. User Content License">
            <p>
              By uploading content (brand guidelines, reference images, prompts), you grant Scribario a limited license to process that content solely to provide the Service. You confirm that you own or have rights to all content you upload.
            </p>
            <p>
              If you believe your copyrighted work has been infringed, you may submit a DMCA notice to privacy@scribario.com.
            </p>
          </Section>

          <Section title="8. Subscription, Payment & Cancellation">
            <p>
              Scribario offers subscription plans with varying features and pricing. Subscriptions auto-renew unless cancelled before the renewal date. Refund policies are outlined at the time of purchase. Upon cancellation, your data is retained for 90 days before deletion unless you request earlier deletion.
            </p>
          </Section>

          <Section title="9. Data Retention & Deletion">
            <p>
              We retain your account data for the duration of your account plus 90 days. You may request deletion of your data at any time by emailing privacy@scribario.com.
            </p>
            <p>
              We comply with Meta&apos;s Data Deletion Callback requirements. LinkedIn profile data is retained for a maximum of 24 hours and social activity data for a maximum of 48 hours, per LinkedIn&apos;s API terms. GDPR deletion requests are processed within 30 days; CCPA requests within 45 days.
            </p>
          </Section>

          <Section title="10. Intellectual Property">
            <p>
              The Scribario brand, platform, and all associated intellectual property belong to DarkArc Technologies LLC. Platform API data remains the property of the respective platforms. AI-generated outputs are not guaranteed to be copyrightable.
            </p>
          </Section>

          <Section title="11. Disclaimers & Limitation of Liability">
            <p>
              THE SERVICE IS PROVIDED &quot;AS IS&quot; WITHOUT WARRANTIES OF ANY KIND, EXPRESS OR IMPLIED. WE DO NOT GUARANTEE THAT POSTS WILL PUBLISH SUCCESSFULLY OR THAT AI CONTENT WILL BE ACCURATE OR ORIGINAL.
            </p>
            <p>
              Our total liability is limited to the fees you paid in the prior 12 months. We exclude liability for consequential, incidental, or punitive damages to the maximum extent permitted by law. Nothing in these Terms limits liability that cannot be limited under applicable law, including GDPR.
            </p>
          </Section>

          <Section title="12. Indemnification">
            <p>
              You agree to indemnify and hold Scribario harmless from any claims arising from: content you post through the Service, violations of any platform&apos;s terms of service, violations of applicable law, or infringement of intellectual property rights.
            </p>
          </Section>

          <Section title="13. Termination">
            <p>
              We may terminate or suspend your account for violation of these Terms, non-payment, or revocation of API access by connected platforms. We will provide 30 days notice for without-cause termination. Immediate termination may occur for illegal activity or abuse. You will have a data export window after termination.
            </p>
          </Section>

          <Section title="14. Modifications">
            <p>
              We reserve the right to modify these Terms. We will provide 30 days notice for material changes via email. Your continued use of the Service after changes constitutes acceptance.
            </p>
          </Section>

          <Section title="15. Governing Law & Disputes">
            <p>
              These Terms are governed by the laws of the State of Wyoming, United States. Disputes shall be resolved through binding arbitration, except where prohibited by law. EU and UK users retain all rights under applicable consumer protection laws. CCPA rights cannot be waived.
            </p>
          </Section>

          <Section title="16. Contact">
            <p>
              For questions about these Terms, contact us at:<br />
              DarkArc Technologies LLC<br />
              Email: privacy@scribario.com
            </p>
          </Section>
        </div>
      </article>
      <Footer />
    </>
  );
}

