import Link from "next/link";

export default function TermsPage() {
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
        <h1 className="text-[28px] font-bold tracking-[-0.02em] text-[#1a1b1c] mb-2">Terms of Service</h1>
        <p className="text-[#8b9094] text-[14px] mb-10">Last updated: May 2026</p>

        <div className="prose prose-gray max-w-none text-[14px] text-[#5f6468] space-y-6">
          <section>
            <h2 className="text-[18px] font-semibold text-[#1a1b1c] mb-3">1. Acceptance of Terms</h2>
            <p>By using MORPHIC, you agree to these Terms of Service. If you do not agree, do not use the service.</p>
          </section>

          <section>
            <h2 className="text-[18px] font-semibold text-[#1a1b1c] mb-3">2. Service Description</h2>
            <p>MORPHIC provides AI-powered facial aesthetic analysis. Our analysis is based on scientific literature and AI models. Results are for informational and educational purposes only. MORPHIC does not provide medical advice, diagnosis, or treatment. Always consult a qualified healthcare professional before starting any new skincare, supplement, or treatment regimen.</p>
          </section>

          <section>
            <h2 className="text-[18px] font-semibold text-[#1a1b1c] mb-3">3. User Responsibilities</h2>
            <ul className="list-disc pl-5 space-y-1">
              <li>You must be at least 13 years old to use MORPHIC.</li>
              <li>You are responsible for the accuracy of information you provide.</li>
              <li>You agree not to upload photos of people without their explicit consent.</li>
              <li>You agree not to misuse, reverse-engineer, or resell our service.</li>
            </ul>
          </section>

          <section>
            <h2 className="text-[18px] font-semibold text-[#1a1b1c] mb-3">4. Payments & Refunds</h2>
            <p>Payments are processed securely via Stripe. We offer a 14-day money-back guarantee from the date you receive your analysis. To request a refund, contact <a href="mailto:support@morphic.ai" className="text-[#1a1b1c] underline">support@morphic.ai</a>. Annual subscriptions auto-renew unless cancelled. You can cancel anytime from your account settings.</p>
          </section>

          <section>
            <h2 className="text-[18px] font-semibold text-[#1a1b1c] mb-3">5. Intellectual Property</h2>
            <p>The MORPHIC brand, website, AI models, and analysis methodology are proprietary. You may not copy, modify, or redistribute our reports or technology without permission.</p>
          </section>

          <section>
            <h2 className="text-[18px] font-semibold text-[#1a1b1c] mb-3">6. Limitation of Liability</h2>
            <p>MORPHIC is provided "as is." We make no warranties about the accuracy of AI-generated reports. We are not liable for any damages arising from the use of our service. Our maximum liability is limited to the amount you paid us in the last 12 months.</p>
          </section>

          <section>
            <h2 className="text-[18px] font-semibold text-[#1a1b1c] mb-3">7. Contact</h2>
            <p><a href="mailto:support@morphic.ai" className="text-[#1a1b1c] underline">support@morphic.ai</a></p>
          </section>
        </div>
      </div>
    </main>
  );
}
