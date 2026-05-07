import Link from "next/link";

export default function PrivacyPage() {
  return (
    <main className="min-h-screen bg-white">
      <header className="border-b border-[#e8e9ea]">
        <div className="container-page flex items-center justify-between h-[64px]">
          <Link href="/" className="flex items-center gap-2">
            <span className="text-[20px] font-bold tracking-[-0.02em] text-[#1a1b1c]">MORPHIC</span>
            <span className="hidden sm:inline text-[11px] uppercase tracking-[0.2em] text-[#8b9094] font-medium mt-0.5">Lab</span>
          </Link>
          <Link href="/" className="btn-ghost text-[13px]">← Back</Link>
        </div>
      </header>
      <div className="container-narrow py-12">
        <h1 className="text-[28px] font-bold tracking-[-0.02em] text-[#1a1b1c] mb-2">Privacy Policy</h1>
        <p className="text-[#8b9094] text-[14px] mb-10">Last updated: May 2026</p>

        <div className="prose prose-gray max-w-none text-[14px] text-[#5f6468] space-y-6">
          <section>
            <h2 className="text-[18px] font-semibold text-[#1a1b1c] mb-3">1. Data We Collect</h2>
            <p>When you use MORPHIC, we collect:</p>
            <ul className="list-disc pl-5 space-y-1">
              <li><strong>Photos:</strong> The 6 facial photos you upload for analysis. Stored encrypted on EU servers (Cloudflare R2, GDPR-compliant).</li>
              <li><strong>Demographic data:</strong> Age, gender, ethnicity, skin type, and aesthetic goals you provide.</li>
              <li><strong>Biometric measurements:</strong> 478 facial landmarks, symmetry scores, proportions, skin analysis results extracted by our AI. These are numerical data — not identifiable.</li>
              <li><strong>Account data:</strong> Email address and payment information (processed securely via Stripe; we never see your full card details).</li>
              <li><strong>Usage data:</strong> Anonymous analytics about how you interact with our site (pages visited, time on site).</li>
            </ul>
          </section>

          <section>
            <h2 className="text-[18px] font-semibold text-[#1a1b1c] mb-3">2. How We Use Your Data</h2>
            <ul className="list-disc pl-5 space-y-1">
              <li><strong>Facial analysis:</strong> Photos are processed locally on our servers to extract numerical biometric data. Photos are NEVER sent to third-party AI providers.</li>
              <li><strong>Report generation:</strong> Only anonymized numerical data (never photos or names) is sent to our LLM provider (DeepSeek API) to generate your aesthetic report.</li>
              <li><strong>Service improvement:</strong> Aggregated, anonymized data may be used to improve our AI models.</li>
              <li><strong>Communication:</strong> Your email is used to send your report results and occasional product updates (opt-out anytime).</li>
            </ul>
          </section>

          <section>
            <h2 className="text-[18px] font-semibold text-[#1a1b1c] mb-3">3. Data Storage & Security</h2>
            <ul className="list-disc pl-5 space-y-1">
              <li>Photos are encrypted at rest (AES-256) and in transit (TLS 1.3).</li>
              <li>All data is stored on EU-based servers (Hetzner, Germany).</li>
              <li>We retain your photos for 30 days after your last analysis, then they are permanently deleted.</li>
              <li>Biometric numerical data is retained for the lifetime of your account for progress tracking.</li>
              <li>Payment data is processed by Stripe and never stored on our servers.</li>
            </ul>
          </section>

          <section>
            <h2 className="text-[18px] font-semibold text-[#1a1b1c] mb-3">4. Your Rights (GDPR)</h2>
            <ul className="list-disc pl-5 space-y-1">
              <li><strong>Access:</strong> Export all your data anytime from your dashboard.</li>
              <li><strong>Deletion:</strong> Delete your account and all associated data permanently (GDPR Art. 17, Right to Erasure).</li>
              <li><strong>Rectification:</strong> Update your demographic data anytime.</li>
              <li><strong>Portability:</strong> Receive your data in a machine-readable format.</li>
              <li>To exercise any right, email <a href="mailto:privacy@morphic.ai" className="text-[#1a1b1c] underline">privacy@morphic.ai</a>.</li>
            </ul>
          </section>

          <section>
            <h2 className="text-[18px] font-semibold text-[#1a1b1c] mb-3">5. Cookies</h2>
            <p>We use essential cookies for authentication and security. Optional analytics cookies help us understand site usage. You can manage preferences via the cookie banner.</p>
          </section>

          <section>
            <h2 className="text-[18px] font-semibold text-[#1a1b1c] mb-3">6. Third-Party Services</h2>
            <ul className="list-disc pl-5 space-y-1">
              <li><strong>Stripe:</strong> Payment processing. Stripe's privacy policy applies to payment data.</li>
              <li><strong>DeepSeek API:</strong> Receives ONLY anonymized numerical facial data for report generation. No photos, no names, no emails.</li>
              <li><strong>Cloudflare R2:</strong> Encrypted photo storage on EU infrastructure.</li>
            </ul>
          </section>

          <section>
            <h2 className="text-[18px] font-semibold text-[#1a1b1c] mb-3">7. Contact</h2>
            <p>Data Protection Officer: <a href="mailto:privacy@morphic.ai" className="text-[#1a1b1c] underline">privacy@morphic.ai</a></p>
          </section>
        </div>
      </div>
    </main>
  );
}
