export function LegalSection({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="mb-10">
      <h3
        className="font-display font-bold mb-4"
        style={{ fontSize: "1.25rem", letterSpacing: "-0.0275em", color: "var(--text)" }}
      >
        {title}
      </h3>
      <div className="legal-section-body space-y-3" style={{ color: "rgba(0,0,0,0.72)" }}>
        {children}
      </div>
    </section>
  );
}
