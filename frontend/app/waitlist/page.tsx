"use client";

import { useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";

export default function WaitlistPage() {
  const [email, setEmail] = useState("");
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    // Using a simple free form backend
    try {
      await fetch("https://formsubmit.co/ajax/micheleghisa88@gmail.com", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, _subject: "MORPHIC Waitlist" }),
      });
    } catch {}
    setSubmitted(true);
  };

  return (
    <main className="min-h-screen bg-white flex items-center justify-center">
      <div className="container-narrow py-20 text-center">
        {!submitted ? (
          <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
            <Link href="/" className="text-[13px] text-[#8b9094] hover:text-[#1a1b1c] transition-colors mb-8 inline-block">
              ← MORPHIC
            </Link>
            <h1 className="text-[clamp(1.8rem,4vw,2.8rem)] font-bold tracking-[-0.02em] text-[#1a1b1c] mb-4">
              Get early access
            </h1>
            <p className="text-[#5f6468] text-[16px] max-w-[400px] mx-auto mb-10">
              Be the first to get a science-backed facial analysis.
              No surgery. Just AI and science.
            </p>
            <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-3 max-w-[400px] mx-auto">
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Your email address"
                required
                className="flex-1 rounded-full border border-[#e0e1e2] px-5 py-3.5 text-[15px] focus:outline-none focus:ring-2 focus:ring-[#1a1b1c]/10 focus:border-[#c0c1c2] transition-all"
              />
              <button type="submit" className="btn-dark whitespace-nowrap text-[15px] px-8 py-3.5">
                Notify Me →
              </button>
            </form>
            <p className="text-[#b0b1b2] text-[12px] mt-4">No spam. Launch updates only.</p>
          </motion.div>
        ) : (
          <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}>
            <div className="w-16 h-16 bg-[#f0f1f2] rounded-full flex items-center justify-center mx-auto mb-6">
              <svg className="w-8 h-8 text-[#5f6468]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h2 className="text-[24px] font-bold text-[#1a1b1c] mb-2">You're on the list!</h2>
            <p className="text-[#5f6468] text-[15px] mb-8">
              We'll let you know as soon as MORPHIC launches.
            </p>
            <Link href="/" className="btn-dark">Back to Home</Link>
          </motion.div>
        )}
      </div>
    </main>
  );
}
