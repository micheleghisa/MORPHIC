"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import Link from "next/link";
import {
  motion,
  useScroll,
  useTransform,
  useMotionValue,
  AnimatePresence,
  useInView,
} from "framer-motion";

// ═══════════════════════════════════════════
// DATA
// ═══════════════════════════════════════════

const RESEARCH = [
  {
    category: "Finances",
    items: [
      { stat: "10-15%", label: "Higher salary for attractive people", ref: "Hamermesh & Biddle, 1994, The American Economic Review" },
      { stat: "$1,261", label: "More in tips annually for attractive servers", ref: "Parrett, 2015, Journal of Economic Psychology" },
      { stat: "55%", label: "More likely to buy from attractive sales people", ref: "Reingen & Kernan, 1993, Journal of Consumer Psychology" },
    ],
  },
  {
    category: "Dating",
    items: [
      { stat: "9x", label: "Looks matter more than biographies on dating apps", ref: "Witmer, Rosenbusch & Meral, 2025" },
      { stat: "Consistent", label: "Looks predict speed-dating success across studies", ref: "Eastwick & Finkel, 2008" },
      { stat: "Understated", label: "People underestimate how much looks affect romantic choices", ref: "Eastwick et al., 2024" },
    ],
  },
  {
    category: "Social",
    items: [
      { stat: "Healthier", label: "Attractive people are perceived as healthier", ref: "Zebrowitz & Franklin, 2014" },
      { stat: "Smarter", label: "Attractive people thought to be more intelligent", ref: "Moore, Filippou & Perrett, 2011" },
      { stat: "3.67x", label: "More missed diagnoses for unattractive patients", ref: "Tsiga et al., 2016" },
    ],
  },
  {
    category: "Legal & Career",
    items: [
      { stat: "Fewer", label: "Arrests for attractive individuals", ref: "Beaver et al., 2019" },
      { stat: "Lighter", label: "Sentences for attractive defendants", ref: "Mazzella & Feingold, 1994" },
      { stat: "Higher", label: "Grades for attractive students in-person", ref: "Hernández-Julián & Peters, 2017" },
    ],
  },
];

const FAQS = [
  {
    q: "What is MORPHIC?",
    a: "MORPHIC is the world's best platform to improve your looks and achieve a real facial transformation without surgery. We provide you, from the comfort of your home, with a personalized facial analysis and transformation plan based on over 2,000 academic studies.",
  },
  {
    q: "How does it work?",
    a: "1. Tell us about yourself: Demographics, lifestyle, and goals. 2. Upload your photos: Six specific angles of your face and head. 3. Get your results: Within minutes, you'll receive your full protocol and visuals of your best-looking self.",
  },
  {
    q: "Is this actually science-backed, or just AI hype?",
    a: "Our analysis is grounded in over 2,000 peer-reviewed studies in facial morphology, dermatology, and aesthetic science. AI helps us deliver that expertise faster and at scale—but this isn't some gimmicky AI app. It's a clinically-informed, comprehensive facial analysis that would typically cost over $15,000 if done manually by experts.",
  },
  {
    q: "Can I really get results without surgery?",
    a: "Yes. The many small changes we recommend, combined together, compound to produce dramatic results. Every transformation you see on this page can be achieved without surgery. Indeed, for most people, surgery is unnecessary and often counterproductive.",
  },
  {
    q: "How much does it cost?",
    a: "$9.99 per analysis or $49.99 per year for unlimited analyses. Compare that to $15,000+ for an equivalent manual consultation at a top aesthetic clinic.",
  },
  {
    q: "Does it work for all ethnicities?",
    a: "Yes. We consider unique facial traits and characteristics common to your demographic and adjust our analysis accordingly. Every aesthetic test is adjusted based not only on your ethnicity, but also your age, sex and lifestyle factors.",
  },
  {
    q: "Are my photos and data private?",
    a: "Absolutely. Everything is encrypted and stored securely. Your photos are never shared publicly, and we only process anonymized biometric data through our AI—never your actual images.",
  },
  {
    q: "How long does it take?",
    a: "Your complete analysis is ready in under 5 minutes. We're fully AI-powered, so there's no waiting weeks for human reviewers.",
  },
];

const PROTOCOL_CATEGORIES = [
  "Skincare Routine",
  "Product Recommendations",
  "Hair & Brow Styling",
  "Makeup Techniques",
  "Color & Contrast",
  "Lifestyle Changes",
  "Facial Exercises",
  "Supplements",
  "At-Home Devices",
  "Dental Aesthetics",
  "Facial Posture",
  "Expression Control",
];

// ═══════════════════════════════════════════
// ANIMATION UTILITIES
// ═══════════════════════════════════════════

function useAnimatedCounter(end: number, duration: number = 2, startCounting: boolean = false) {
  const [count, setCount] = useState(0);
  const nodeRef = useRef<HTMLSpanElement>(null);
  const inView = useInView(nodeRef, { once: true, margin: "-50px" });

  useEffect(() => {
    if (!inView && !startCounting) return;
    let startTime: number;
    let animationFrame: number;

    const animate = (timestamp: number) => {
      if (!startTime) startTime = timestamp;
      const progress = Math.min((timestamp - startTime) / (duration * 1000), 1);
      // easeOutExpo
      const eased = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);
      setCount(Math.floor(eased * end));
      if (progress < 1) {
        animationFrame = requestAnimationFrame(animate);
      }
    };

    animationFrame = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(animationFrame);
  }, [end, duration, inView, startCounting]);

  return { count, nodeRef };
}

// ═══════════════════════════════════════════
// COMPONENTS
// ═══════════════════════════════════════════

function ScrollReveal({
  children,
  className = "",
  delay = 0,
  direction = "up",
}: {
  children: React.ReactNode;
  className?: string;
  delay?: number;
  direction?: "up" | "down" | "left" | "right" | "none";
}) {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-80px" });

  const directionMap = {
    up: { y: 30 },
    down: { y: -30 },
    left: { x: 30 },
    right: { x: -30 },
    none: {},
  };

  return (
    <motion.div
      ref={ref}
      className={className}
      initial={{ opacity: 0, ...directionMap[direction] }}
      animate={
        isInView
          ? { opacity: 1, x: 0, y: 0 }
          : { opacity: 0, ...directionMap[direction] }
      }
      transition={{ duration: 0.7, delay, ease: [0.16, 1, 0.3, 1] }}
    >
      {children}
    </motion.div>
  );
}

// ─── NAVBAR ───

function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <motion.nav
      initial={{ y: -80 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled
          ? "bg-white/90 backdrop-blur-xl border-b border-[#e8e9ea] shadow-[0_1px_3px_rgba(0,0,0,0.03)]"
          : "bg-transparent"
      }`}
    >
      <div className="container-page flex items-center justify-between h-[64px]">
        <Link href="/" className="flex items-center gap-2">
          <span className="text-[20px] font-bold tracking-[-0.02em] text-[#1a1b1c]">
            MORPHIC
          </span>
          <span className="hidden sm:inline text-[11px] uppercase tracking-[0.2em] text-[#8b9094] font-medium mt-0.5">
            Lab
          </span>
        </Link>

        <div className="hidden md:flex items-center gap-1">
          <a href="#how-it-works" className="btn-ghost">How It Works</a>
          <a href="#faq" className="btn-ghost">FAQ</a>
          <Link href="/upload" className="btn-dark ml-3">
            Start Now
          </Link>
        </div>

        <button
          className="md:hidden btn-ghost"
          onClick={() => setMobileOpen(!mobileOpen)}
        >
          {mobileOpen ? "Close" : "Menu"}
        </button>
      </div>

      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden bg-white border-b border-[#e8e9ea] overflow-hidden"
          >
            <div className="container-page py-4 flex flex-col gap-2">
              <a href="#how-it-works" className="btn-ghost justify-start" onClick={() => setMobileOpen(false)}>How It Works</a>
              <a href="#faq" className="btn-ghost justify-start" onClick={() => setMobileOpen(false)}>FAQ</a>
              <Link href="/upload" className="btn-dark mt-2 justify-center" onClick={() => setMobileOpen(false)}>Start Now</Link>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.nav>
  );
}

// ─── HERO ───

function HeroSection() {
  const { scrollY } = useScroll();
  const heroOpacity = useTransform(scrollY, [0, 500], [1, 0.3]);
  const heroY = useTransform(scrollY, [0, 500], [0, 80]);
  const badgeOpacity = useTransform(scrollY, [0, 300], [1, 0]);

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* Subtle background */}
      <div className="absolute inset-0 bg-gradient-to-b from-[#f8f9f9] via-white to-white" />
      <div className="absolute top-1/3 left-1/2 -translate-x-1/2 w-[800px] h-[500px] bg-gradient-to-b from-[#f0f1f2]/50 to-transparent rounded-full blur-3xl" />

      <motion.div style={{ opacity: heroOpacity, y: heroY }} className="container-narrow relative z-10 pt-24 pb-20 text-center">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          style={{ opacity: badgeOpacity }}
          className="badge mx-auto mb-8"
        >
          <span className="w-1.5 h-1.5 rounded-full bg-[#1a1b1c]" />
          AI-Powered Beauty Science
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.3, ease: [0.16, 1, 0.3, 1] }}
          className="text-[clamp(2.5rem,6vw,5rem)] font-bold leading-[1.06] tracking-[-0.03em] text-[#1a1b1c] mb-6 text-balance"
        >
          Science-Based Aesthetics.
          <br />
          Glow Up{" "}
          <span className="text-[#8b9094]">Without Surgery.</span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.45, ease: [0.16, 1, 0.3, 1] }}
          className="text-[17px] sm:text-[19px] text-[#5f6468] leading-relaxed max-w-[580px] mx-auto mb-10 text-balance"
        >
          Get your personalized facial analysis and transformation plan based on
          2,000+ academic studies. Every year.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.6, ease: [0.16, 1, 0.3, 1] }}
          className="flex flex-col sm:flex-row items-center justify-center gap-3"
        >
          <Link href="/upload" className="btn-dark text-[16px] px-8 py-3.5">
            Try It Free — No Card Required
          </Link>
          <a href="#how-it-works" className="btn-outline text-[16px] px-8 py-3.5">
            How It Works
          </a>
        </motion.div>

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 1 }}
          className="text-[13px] text-[#8b9094] mt-6"
        >
          No surgery. No filters. Just science.
        </motion.p>
      </motion.div>

      {/* Scroll indicator */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.5 }}
        className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2"
      >
        <span className="text-[11px] uppercase tracking-[0.2em] text-[#b0b1b2]">Scroll</span>
        <motion.div
          animate={{ y: [0, 6, 0] }}
          transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut" }}
          className="w-px h-8 bg-gradient-to-b from-[#d0d1d2] to-transparent"
        />
      </motion.div>
    </section>
  );
}

// ─── HOW IT WORKS ───

function HowItWorksSection() {
  const steps = [
    {
      num: "01",
      title: "Tell us about yourself",
      desc: "Share your demographics, lifestyle, and aesthetic goals. Our AI tailors every recommendation to your unique profile.",
    },
    {
      num: "02",
      title: "Upload your photos",
      desc: "Follow our guided capture for six specific angles. No special equipment. Takes two minutes from your phone or laptop.",
    },
    {
      num: "03",
      title: "Get your glow-up plan",
      desc: "Within minutes, receive your full facial analysis, biometric scores, before/after visualizations, and personalized protocol.",
    },
  ];

  return (
    <section id="how-it-works" className="py-24 sm:py-32 bg-[#f8f9f9]">
      <div className="container-page">
        <ScrollReveal className="text-center mb-16 sm:mb-20">
          <p className="text-[12px] uppercase tracking-[0.2em] text-[#8b9094] font-medium mb-4">
            How It Works
          </p>
          <h2 className="text-[clamp(1.8rem,4vw,2.8rem)] font-bold tracking-[-0.02em] text-[#1a1b1c] mb-4">
            Three steps to your best self
          </h2>
          <p className="text-[#5f6468] text-[16px] max-w-[500px] mx-auto">
            Simple, fast, and completely non-surgical.
          </p>
        </ScrollReveal>

        <div className="grid md:grid-cols-3 gap-6 max-w-[900px] mx-auto">
          {steps.map((step, i) => (
            <ScrollReveal key={step.num} delay={i * 0.15}>
              <div className="card-elevated p-8 h-full">
                <span className="text-[12px] font-mono text-[#8b9094] mb-6 block">
                  {step.num}
                </span>
                <h3 className="text-[18px] font-semibold text-[#1a1b1c] mb-3">
                  {step.title}
                </h3>
                <p className="text-[14px] text-[#5f6468] leading-relaxed">
                  {step.desc}
                </p>
              </div>
            </ScrollReveal>
          ))}
        </div>
      </div>
    </section>
  );
}

// ─── FACE ILLUSTRATION ───

function FaceIllustration({ variant }: { variant: "before" | "after" }) {
  const isAfter = variant === "after";
  return (
    <div className="relative w-48 h-56 sm:w-56 sm:h-64">
      <svg viewBox="0 0 200 240" className="w-full h-full">
        {/* Face outline */}
        <ellipse cx="100" cy="115" rx="62" ry="82" fill="none" stroke={isAfter ? "#8a9bb5" : "#b8a99a"} strokeWidth="2" />
        {/* Jaw */}
        <path d="M55 115 Q55 180 100 195 Q145 180 145 115" fill="none" stroke={isAfter ? "#8a9bb5" : "#b8a99a"} strokeWidth={isAfter ? "2.5" : "1.8"} />
        {/* Left eye */}
        <ellipse cx="75" cy="100" rx="15" ry={isAfter ? "10" : "8"} fill="none" stroke={isAfter ? "#6b7d99" : "#a89880"} strokeWidth="1.5" />
        <circle cx="75" cy="100" r="4" fill={isAfter ? "#6b7d99" : "#a89880"} />
        {/* Right eye */}
        <ellipse cx="125" cy="100" rx="15" ry={isAfter ? "10" : "8.5"} fill="none" stroke={isAfter ? "#6b7d99" : "#a89880"} strokeWidth="1.5" />
        <circle cx="125" cy="100" r="4" fill={isAfter ? "#6b7d99" : "#a89880"} />
        {/* Left brow */}
        <path d={isAfter ? "M58 82 Q75 76 92 80" : "M58 80 Q75 76 92 82"} fill="none" stroke={isAfter ? "#5a6d85" : "#9a8a72"} strokeWidth="2.5" />
        {/* Right brow */}
        <path d={isAfter ? "M108 80 Q125 76 142 82" : "M108 82 Q125 78 142 80"} fill="none" stroke={isAfter ? "#5a6d85" : "#9a8a72"} strokeWidth="2.5" />
        {/* Nose */}
        <path d="M100 95 L96 125 Q100 130 104 125 L100 95" fill="none" stroke={isAfter ? "#8a9bb5" : "#b8a99a"} strokeWidth="1.2" />
        {/* Mouth */}
        <path d={isAfter ? "M78 150 Q100 162 122 150" : "M80 148 Q100 158 120 148"} fill="none" stroke={isAfter ? "#8a9bb5" : "#b8a99a"} strokeWidth={isAfter ? "1.8" : "1.5"} />
        {/* Skin dots (blemishes) — fewer on "after" */}
        {!isAfter && (
          <>
            <circle cx="90" cy="130" r="1.5" fill="#c0b0a0" opacity="0.6" />
            <circle cx="105" cy="125" r="1" fill="#c0b0a0" opacity="0.5" />
            <circle cx="70" cy="118" r="1.2" fill="#c0b0a0" opacity="0.4" />
            <circle cx="115" cy="140" r="1.3" fill="#c0b0a0" opacity="0.5" />
          </>
        )}
        {/* Symmetry lines on "after" */}
        {isAfter && (
          <>
            <line x1="100" y1="35" x2="100" y2="195" stroke="#6b7d99" strokeWidth="0.5" strokeDasharray="4,4" opacity="0.5" />
            <line x1="38" y1="100" x2="162" y2="100" stroke="#6b7d99" strokeWidth="0.5" strokeDasharray="4,4" opacity="0.3" />
            <line x1="38" y1="150" x2="162" y2="150" stroke="#6b7d99" strokeWidth="0.5" strokeDasharray="4,4" opacity="0.3" />
          </>
        )}
      </svg>
      <div className={`absolute bottom-0 left-1/2 -translate-x-1/2 text-[11px] font-medium px-3 py-1 rounded-full ${
        isAfter ? "bg-[#dce4f0] text-[#5a6d85]" : "bg-[#e8e5e0] text-[#9a8a72]"
      }`}>
        {isAfter ? "After Glow-Up" : "Current"}
      </div>
    </div>
  );
}

// ─── COMPARISON CARDS ───

function ComparisonCards() {
  const items = [
    { label: "Symmetry", before: "78/100", after: "94/100", desc: "Brow alignment, eye balance, lip symmetry" },
    { label: "Skin Health", before: "62/100", after: "87/100", desc: "Texture refinement, tone evening, pore reduction" },
    { label: "Jawline", before: "71/100", after: "90/100", desc: "Facial exercises, posture correction, lymph drainage" },
    { label: "Eye Area", before: "74/100", after: "89/100", desc: "Dark circle reduction, brow lift, lash enhancement" },
  ];

  return (
    <section className="py-20 bg-[#f8f9f9]">
      <div className="container-page">
        <ScrollReveal className="text-center mb-14">
          <h2 className="text-[clamp(1.5rem,3vw,2rem)] font-bold tracking-[-0.02em] text-[#1a1b1c] mb-3">
            Real improvements, measured in numbers
          </h2>
          <p className="text-[#5f6468] text-[15px] max-w-[480px] mx-auto">
            Every metric is tracked across your glow-up journey. See exactly what changes.
          </p>
        </ScrollReveal>

        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 max-w-[900px] mx-auto">
          {items.map((item, i) => (
            <ScrollReveal key={item.label} delay={i * 0.1}>
              <div className="card-elevated p-5 text-center">
                <p className="text-[13px] font-semibold text-[#1a1b1c] mb-3">{item.label}</p>
                <div className="flex items-center justify-center gap-2 mb-2">
                  <span className="text-[#8b9094] text-[12px]">{item.before}</span>
                  <svg className="w-4 h-4 text-[#b0b1b2]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M17 8l4 4m0 0l-4 4m4-4H3" />
                  </svg>
                  <span className="text-[#1a1b1c] font-bold text-[15px]">{item.after}</span>
                </div>
                <p className="text-[12px] text-[#8b9094] leading-relaxed">{item.desc}</p>
              </div>
            </ScrollReveal>
          ))}
        </div>
      </div>
    </section>
  );
}

function BeforeAfterSlider() {
  const containerRef = useRef<HTMLDivElement>(null);
  const [position, setPosition] = useState(50);
  const dragging = useRef(false);

  const handleMove = useCallback(
    (clientX: number) => {
      if (!containerRef.current) return;
      const rect = containerRef.current.getBoundingClientRect();
      const x = Math.max(0, Math.min(clientX - rect.left, rect.width));
      setPosition((x / rect.width) * 100);
    },
    []
  );

  const handleMouseDown = () => { dragging.current = true; };
  const handleMouseUp = () => { dragging.current = false; };
  const handleMouseMove = (e: React.MouseEvent) => {
    if (dragging.current) handleMove(e.clientX);
  };
  const handleTouchMove = (e: React.TouchEvent) => {
    handleMove(e.touches[0].clientX);
  };

  return (
    <section className="py-24 sm:py-32">
      <div className="container-page">
        <ScrollReveal className="text-center mb-16">
          <p className="text-[12px] uppercase tracking-[0.2em] text-[#8b9094] font-medium mb-4">
            Real Transformations
          </p>
          <h2 className="text-[clamp(1.8rem,4vw,2.8rem)] font-bold tracking-[-0.02em] text-[#1a1b1c] mb-4">
            See the difference without surgery
          </h2>
          <p className="text-[#5f6468] text-[16px] max-w-[550px] mx-auto">
            Every result you see can be achieved without a single surgical procedure.
            Slide to compare.
          </p>
        </ScrollReveal>

        <ScrollReveal className="max-w-[800px] mx-auto">
          <div
            ref={containerRef}
            className="before-after-slider relative aspect-[4/3] rounded-2xl overflow-hidden cursor-ew-resize select-none"
            onMouseDown={handleMouseDown}
            onMouseUp={handleMouseUp}
            onMouseLeave={handleMouseUp}
            onMouseMove={handleMouseMove}
            onTouchMove={handleTouchMove}
          >
            {/* After Glow-Up (full background — what you see by default) */}
            <div className="w-full h-full bg-gradient-to-br from-[#e8eef5] to-[#dce4f0] flex items-center justify-center">
              <FaceIllustration variant="after" />
            </div>

            {/* Current (left side — revealed by dragging slider left) */}
            <div
              className="after-img bg-gradient-to-br from-[#f5f3f0] to-[#e8e5e0] flex items-center justify-center"
              style={{ clipPath: `inset(0 0 0 ${100 - position}%)` }}
            >
              <FaceIllustration variant="before" />
            </div>

            {/* Slider line */}
            <div className="slider-line" style={{ left: `${position}%` }} />

            {/* Handle */}
            <div
              className="slider-handle"
              style={{ left: `${position}%` }}
              onMouseDown={handleMouseDown}
              onTouchStart={handleMouseDown}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#1a1b1c" strokeWidth="1.5">
                <path d="M8 4l-6 8 6 8M16 4l6 8-6 8" />
              </svg>
            </div>

            {/* Labels */}
            <div className="absolute bottom-4 left-4 bg-white/90 backdrop-blur-sm text-[12px] font-medium px-3 py-1.5 rounded-full text-[#1a1b1c] shadow-sm">
              After Glow-Up
            </div>
            <div className="absolute bottom-4 right-4 bg-white/90 backdrop-blur-sm text-[12px] font-medium px-3 py-1.5 rounded-full text-[#5f6468] shadow-sm">
              Current
            </div>
          </div>
        </ScrollReveal>
      </div>
    </section>
  );
}

// ─── PROTOCOL PREVIEW ───

function ProtocolSection() {
  return (
    <section className="py-24 sm:py-32 bg-[#f8f9f9]">
      <div className="container-page">
        <ScrollReveal className="text-center mb-16">
          <p className="text-[12px] uppercase tracking-[0.2em] text-[#8b9094] font-medium mb-4">
            Your Personalized Protocol
          </p>
          <h2 className="text-[clamp(1.8rem,4vw,2.8rem)] font-bold tracking-[-0.02em] text-[#1a1b1c] mb-4">
            Everything you need to glow up
          </h2>
          <p className="text-[#5f6468] text-[16px] max-w-[550px] mx-auto">
            Every protocol includes 12 categories of non-surgical recommendations,
            each with premium, budget, and free options.
          </p>
        </ScrollReveal>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3 max-w-[800px] mx-auto">
          {PROTOCOL_CATEGORIES.map((cat, i) => (
            <ScrollReveal key={cat} delay={i * 0.05}>
              <div className="card-flat p-4 text-center hover:bg-[#f0f1f2] cursor-default">
                <span className="text-[13px] font-medium text-[#3a3b3c]">{cat}</span>
              </div>
            </ScrollReveal>
          ))}
        </div>
      </div>
    </section>
  );
}

// ─── RESEARCH ───

function ResearchSection() {
  const [tab, setTab] = useState("Finances");

  return (
    <section className="py-24 sm:py-32">
      <div className="container-page">
        <ScrollReveal className="text-center mb-16">
          <p className="text-[12px] uppercase tracking-[0.2em] text-[#8b9094] font-medium mb-4">
            Research
          </p>
          <h2 className="text-[clamp(1.8rem,4vw,2.8rem)] font-bold tracking-[-0.02em] text-[#1a1b1c] mb-4">
            Your appearance impacts your life
          </h2>
          <p className="text-[#5f6468] text-[16px] max-w-[550px] mx-auto">
            Decades of peer-reviewed research consistently demonstrate the
            wide-ranging benefits of physical attractiveness.
          </p>
        </ScrollReveal>

        {/* Tabs */}
        <div className="flex flex-wrap justify-center gap-2 mb-12">
          {RESEARCH.map(({ category }) => (
            <button
              key={category}
              onClick={() => setTab(category)}
              className={`px-5 py-2 rounded-full text-[13px] font-medium transition-all duration-200 ${
                tab === category
                  ? "bg-[#1a1b1c] text-white"
                  : "bg-[#f0f1f2] text-[#5f6468] hover:bg-[#e4e5e6]"
              }`}
            >
              {category}
            </button>
          ))}
        </div>

        {/* Cards */}
        <div className="grid md:grid-cols-3 gap-4 max-w-[900px] mx-auto">
          <AnimatePresence mode="wait">
            {RESEARCH.find((r) => r.category === tab)?.items.map((item, i) => (
              <motion.div
                key={item.ref}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -6 }}
                transition={{ duration: 0.4, delay: i * 0.08 }}
                className="card-elevated p-6 border-l-[3px] border-l-[#1a1b1c]"
              >
                <span className="text-[24px] font-bold text-[#1a1b1c] block mb-1">
                  {item.stat}
                </span>
                <p className="text-[14px] text-[#5f6468] mb-3 leading-snug">
                  {item.label}
                </p>
                <p className="text-[11px] text-[#b0b1b2] italic leading-tight">
                  {item.ref}
                </p>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      </div>
    </section>
  );
}

// ─── COUNTERS ───

function CountersSection() {
  const { count: landmarks, nodeRef: ref1 } = useAnimatedCounter(478, 2);
  const { count: studies, nodeRef: ref2 } = useAnimatedCounter(2000, 2.5);
  const { count: tests, nodeRef: ref3 } = useAnimatedCounter(100, 1.8);
  const { count: seconds, nodeRef: ref4 } = useAnimatedCounter(180, 2);

  return (
    <section className="py-24 sm:py-32 bg-[#1a1b1c] text-white">
      <div className="container-page">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 max-w-[800px] mx-auto text-center">
          {[
            { value: landmarks, ref: ref1, suffix: "", label: "Facial landmarks analyzed" },
            { value: studies, ref: ref2, suffix: "+", label: "Peer-reviewed studies" },
            { value: tests, ref: ref3, suffix: "+", label: "Aesthetic tests performed" },
            { value: seconds, ref: ref4, suffix: "s", label: "Average analysis time" },
          ].map((item) => (
            <div key={item.label}>
              <span ref={item.ref} className="text-[clamp(2rem,5vw,3rem)] font-bold tracking-[-0.03em] block">
                {item.value}{item.suffix}
              </span>
              <span className="text-[14px] text-[#8b9094]">{item.label}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

// ─── PRICING ───

function PricingSection() {
  return (
    <section className="py-24 sm:py-32 bg-[#f8f9f9]">
      <div className="container-narrow text-center">
        <ScrollReveal>
          <p className="text-[12px] uppercase tracking-[0.2em] text-[#8b9094] font-medium mb-4">
            Start Free — No Card Required
          </p>
          <h2 className="text-[clamp(1.8rem,4vw,2.8rem)] font-bold tracking-[-0.02em] text-[#1a1b1c] mb-4">
            Try it now, pay when you're ready
          </h2>
          <p className="text-[#5f6468] text-[16px] max-w-[500px] mx-auto mb-10">
            Get your first analysis completely free. No credit card. 
            If you love it, unlock unlimited analyses for .99/month.
          </p>
          <Link href="/upload" className="btn-dark text-[16px] px-10 py-4">
            Start Free Analysis →
          </Link>
          <p className="text-[#8b9094] text-[13px] mt-4">
            Coming soon: .99 one-time or .99/year unlimited
          </p>
        </ScrollReveal>
      </div>
    </section>
  );
}

// ─── FAQ ───

function FAQSection() {
  const [open, setOpen] = useState<number | null>(null);

  return (
    <section id="faq" className="py-24 sm:py-32">
      <div className="container-narrow">
        <ScrollReveal className="text-center mb-16">
          <p className="text-[12px] uppercase tracking-[0.2em] text-[#8b9094] font-medium mb-4">
            FAQ
          </p>
          <h2 className="text-[clamp(1.8rem,4vw,2.8rem)] font-bold tracking-[-0.02em] text-[#1a1b1c]">
            Frequently asked questions
          </h2>
        </ScrollReveal>

        <div className="space-y-2">
          {FAQS.map((faq, i) => (
            <ScrollReveal key={i} delay={i * 0.05}>
              <div className="border border-[#e8e9ea] rounded-xl overflow-hidden">
                <button
                  onClick={() => setOpen(open === i ? null : i)}
                  className="w-full flex items-center justify-between p-5 text-left hover:bg-[#f8f9f9] transition-colors"
                >
                  <span className="text-[15px] font-medium text-[#1a1b1c] pr-4">{faq.q}</span>
                  <motion.svg
                    animate={{ rotate: open === i ? 45 : 0 }}
                    transition={{ duration: 0.2 }}
                    className="w-5 h-5 text-[#8b9094] shrink-0"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    strokeWidth={1.5}
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 5v14M5 12h14" />
                  </motion.svg>
                </button>
                <AnimatePresence>
                  {open === i && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: "auto", opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
                      className="overflow-hidden"
                    >
                      <p className="px-5 pb-5 text-[14px] text-[#5f6468] leading-relaxed">
                        {faq.a}
                      </p>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </ScrollReveal>
          ))}
        </div>
      </div>
    </section>
  );
}

// ─── CTA ───

function CTASection() {
  return (
    <section className="py-24 sm:py-32 bg-[#1a1b1c] relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-b from-white/5 to-transparent" />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-white/[0.02] rounded-full blur-3xl" />

      <div className="container-narrow relative z-10 text-center">
        <ScrollReveal>
          <h2 className="text-[clamp(1.8rem,4vw,2.8rem)] font-bold tracking-[-0.02em] text-white mb-4 text-balance">
            Ready to see your best self?
          </h2>
          <p className="text-[#8b9094] text-[16px] max-w-[450px] mx-auto mb-8">
            Join thousands who have already started their science-backed glow up.
            No surgery. No filters. Just results.
          </p>
          <Link
            href="/upload"
            className="inline-flex items-center justify-center rounded-full bg-white text-[#1a1b1c] px-8 py-3.5 text-[16px] font-medium hover:bg-[#f0f1f2] active:scale-[0.97] transition-all duration-200"
          >
            Start Free Analysis
          </Link>
          <p className="text-[#5f6468] text-[13px] mt-4">
            Free trial. No credit card required.
          </p>
        </ScrollReveal>
      </div>
    </section>
  );
}

// ─── FOOTER ───

function Footer() {
  return (
    <footer className="py-10 border-t border-[#e8e9ea]">
      <div className="container-page">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
          <Link href="/" className="flex items-center gap-2">
            <span className="text-[18px] font-bold tracking-[-0.02em] text-[#1a1b1c]">MORPHIC</span>
            <span className="text-[10px] uppercase tracking-[0.2em] text-[#b0b1b2] font-medium">Lab</span>
          </Link>

          <div className="flex items-center gap-6 text-[13px] text-[#8b9094]">
            <Link href="/privacy" className="hover:text-[#1a1b1c] transition-colors">Privacy</Link>
            <Link href="/terms" className="hover:text-[#1a1b1c] transition-colors">Terms</Link>
            <a href="mailto:hello@morphic.ai" className="hover:text-[#1a1b1c] transition-colors">Contact</a>
          </div>

          <p className="text-[13px] text-[#b0b1b2]">
            &copy; {new Date().getFullYear()} MORPHIC. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
}

// ═══════════════════════════════════════════
// MAIN PAGE
// ═══════════════════════════════════════════

export default function HomePage() {
  return (
    <main>
      <Navbar />
      <HeroSection />
      <HowItWorksSection />
      <BeforeAfterSlider />
      <ComparisonCards />
      <ProtocolSection />
      <CountersSection />
      <ResearchSection />
      <PricingSection />
      <FAQSection />
      <CTASection />
      <Footer />
    </main>
  );
}
