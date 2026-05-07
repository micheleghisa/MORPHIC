"use client";

import { useState } from "react";
import Link from "next/link";

export default function PricingPage() {
  const [billing, setBilling] = useState<"one-time" | "annual">("one-time");

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

      <div className="container-narrow py-20 text-center">
        <h1 className="text-[clamp(1.8rem,4vw,2.8rem)] font-bold tracking-[-0.02em] text-[#1a1b1c] mb-4">
          Start Your Glow Up Today
        </h1>
        <p className="text-[#5f6468] text-[16px] mb-4">
          One price. Full analysis. No surgery. 14-day money-back guarantee.
        </p>

        {/* Toggle */}
        <div className="inline-flex bg-[#f0f1f2] rounded-full p-1 mb-12">
          <button
            onClick={() => setBilling("one-time")}
            className={`px-6 py-2 rounded-full text-[13px] font-medium transition-all ${
              billing === "one-time" ? "bg-white text-[#1a1b1c] shadow-sm" : "text-[#8b9094]"
            }`}
          >
            One Analysis
          </button>
          <button
            onClick={() => setBilling("annual")}
            className={`px-6 py-2 rounded-full text-[13px] font-medium transition-all ${
              billing === "annual" ? "bg-white text-[#1a1b1c] shadow-sm" : "text-[#8b9094]"
            }`}
          >
            Unlimited Annual
          </button>
        </div>

        {/* Price Card */}
        <div className="max-w-[380px] mx-auto">
          <div className="card-elevated p-8">
            <h3 className="text-[18px] font-semibold text-[#1a1b1c] mb-1">
              {billing === "one-time" ? "Single Analysis" : "Unlimited Plan"}
            </h3>
            <div className="mb-6">
              <span className="text-[40px] font-bold text-[#1a1b1c] tracking-[-0.02em]">
                {billing === "one-time" ? "$9.99" : "$49.99"}
              </span>
              <span className="text-[#8b9094] text-[14px] ml-2">
                {billing === "one-time" ? "one-time" : "/year"}
              </span>
            </div>
            <ul className="space-y-3 mb-8 text-left">
              {billing === "one-time" ? (
                <>
                  <Benefit text="Full facial analysis (478 landmarks)" />
                  <Benefit text="Skin health assessment" />
                  <Benefit text="Before/after visualizations" />
                  <Benefit text="Personalized glow-up protocol" />
                  <Benefit text="Access results forever" />
                </>
              ) : (
                <>
                  <Benefit text="Everything in Single Analysis" />
                  <Benefit text="Unlimited analyses all year" />
                  <Benefit text="Quarterly progress tracking" />
                  <Benefit text="24/7 AI aesthetic assistant" />
                  <Benefit text="Early access to new features" />
                </>
              )}
            </ul>

            {/* Stripe Checkout */}
            <form action="/api/stripe/checkout" method="POST">
              <input type="hidden" name="plan" value={billing} />
              <button type="submit" className="btn-dark w-full !py-3.5 text-[15px]">
                Pay {billing === "one-time" ? "$9.99" : "$49.99"} →
              </button>
            </form>
            <p className="text-[12px] text-[#b0b1b2] mt-3 text-center">
              Secure payment via Stripe. 14-day refund.
            </p>
          </div>
        </div>
      </div>
    </main>
  );
}

function Benefit({ text }: { text: string }) {
  return (
    <li className="flex items-start gap-2 text-[14px] text-[#5f6468]">
      <svg className="w-4 h-4 text-[#1a1b1c] mt-0.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
      </svg>
      {text}
    </li>
  );
}
