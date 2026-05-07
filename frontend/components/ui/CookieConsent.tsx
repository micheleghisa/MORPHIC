"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";

export default function CookieConsent() {
  const [show, setShow] = useState(false);

  useEffect(() => {
    const consented = localStorage.getItem("eidos_cookie_consent");
    if (!consented) {
      setTimeout(() => setShow(true), 800);
    }
  }, []);

  const acceptAll = () => {
    localStorage.setItem("eidos_cookie_consent", "all");
    setShow(false);
  };

  const acceptEssential = () => {
    localStorage.setItem("eidos_cookie_consent", "essential");
    setShow(false);
  };

  return (
    <AnimatePresence>
      {show && (
        <motion.div
          initial={{ y: 100, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: 100, opacity: 0 }}
          transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
          className="fixed bottom-4 left-4 right-4 md:left-auto md:right-4 md:max-w-sm z-50"
        >
          <div className="bg-white rounded-2xl border border-[#e8e9ea] shadow-[0_8px_32px_rgba(0,0,0,0.1)] p-5">
            <p className="text-[13px] text-[#5f6468] leading-relaxed mb-4">
              We use cookies to analyze traffic and improve your experience.{" "}
              <a href="/privacy" className="text-[#1a1b1c] underline underline-offset-2">
                Learn more
              </a>
            </p>
            <div className="flex gap-2">
              <button onClick={acceptEssential} className="flex-1 btn-ghost !text-[12px] !py-2">
                Essential Only
              </button>
              <button onClick={acceptAll} className="flex-1 btn-dark !text-[12px] !py-2">
                Accept All
              </button>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
