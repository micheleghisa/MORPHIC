"use client";

import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useDropzone } from "react-dropzone";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowRight, Camera, X, Check } from "lucide-react";
import { API_BASE_URL } from "@/lib/utils";

const GUIDED_ANGLES = [
  { id: "front", label: "Front View", desc: "Face the camera directly. Neutral expression." },
  { id: "profile_right", label: "Right Profile", desc: "Turn your head 90° to the right." },
  { id: "profile_left", label: "Left Profile", desc: "Turn your head 90° to the left." },
  { id: "three_quarter_right", label: "3/4 Right", desc: "Turn 45° to the right." },
  { id: "three_quarter_left", label: "3/4 Left", desc: "Turn 45° to the left." },
  { id: "front_smiling", label: "Front Smiling", desc: "Face the camera and smile naturally." },
];

const GOALS = [
  "Symmetry", "Skin Quality", "Jawline", "Eye Area",
  "Hair & Brow", "Lip Shape", "Overall Harmony", "Anti-Aging",
];

export default function UploadPage() {
  const router = useRouter();
  const [step, setStep] = useState<"form" | "upload" | "processing">("form");
  const [photos, setPhotos] = useState<Record<string, File>>({});
  const [error, setError] = useState<string | null>(null);
  const [age, setAge] = useState("");
  const [gender, setGender] = useState("");
  const [ethnicity, setEthnicity] = useState("");
  const [skinType, setSkinType] = useState("");
  const [goals, setGoals] = useState<string[]>([]);

  const toggleGoal = (g: string) => setGoals((p) => p.includes(g) ? p.filter((x) => x !== g) : [...p, g]);
  const removePhoto = (id: string) => setPhotos((p) => { const n = { ...p }; delete n[id]; return n; });
  const onDrop = useCallback((angleId: string) => (files: File[]) => {
    if (files.length > 0) setPhotos((p) => ({ ...p, [angleId]: files[0] }));
  }, []);

  const handleSubmit = async () => {
    if (Object.keys(photos).length < 6) { setError("Upload all 6 photos."); return; }
    setError(null); setStep("processing");
    try {
      const fd = new FormData();
      fd.append("age", age); fd.append("gender", gender); fd.append("ethnicity", ethnicity);
      fd.append("skin_type", skinType); fd.append("skin_concerns", "[]");
      fd.append("goals", JSON.stringify(goals)); fd.append("lifestyle_factors", "{}");
      Object.values(photos).forEach((f) => fd.append("photos", f));
      const res = await fetch(`${API_BASE_URL}/api/v1/analyze`, { method: "POST", body: fd });
      if (!res.ok) throw new Error("Failed");
      const data = await res.json();
      const poll = setInterval(async () => {
        const sr = await fetch(`${API_BASE_URL}/api/v1/analysis/${data.analysis_id}`);
        const st = await sr.json();
        if (st.status === "completed") { clearInterval(poll); router.push(`/report/${data.analysis_id}`); }
        if (st.status === "failed") { clearInterval(poll); setError(st.error || "Failed"); setStep("upload"); }
      }, 2000);
    } catch (e: any) { setError(e.message); setStep("upload"); }
  };

  const allDone = Object.keys(photos).length === 6;

  return (
    <main className="min-h-screen bg-white">
      {/* HEADER */}
      <header className="border-b border-[#e8e9ea]">
        <div className="container-page flex items-center justify-between h-[64px]">
          <Link href="/" className="flex items-center gap-2">
            <span className="text-[20px] font-bold tracking-[-0.02em] text-[#1a1b1c]">MORPHIC</span>
            <span className="hidden sm:inline text-[11px] uppercase tracking-[0.2em] text-[#8b9094] font-medium mt-0.5">Lab</span>
          </Link>
          <Link href="/" className="btn-ghost text-[13px]">← Back to home</Link>
        </div>
      </header>

      <div className="container-narrow py-12 sm:py-20">
        {/* STEPPER */}
        <div className="flex items-center justify-center gap-2 mb-12">
          {["Details", "Photos", "Analysis"].map((l, i) => (
            <div key={l} className="flex items-center gap-2">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-[13px] font-medium transition-colors ${
                (i === 0 && step === "form") || (i === 1 && step !== "form") || (i === 2 && step === "processing")
                  ? "bg-[#1a1b1c] text-white" : "bg-[#f0f1f2] text-[#8b9094]"
              }`}>
                {i + 1}
              </div>
              <span className="text-[13px] text-[#8b9094] hidden sm:inline">{l}</span>
              {i < 2 && <div className="w-8 h-px bg-[#e8e9ea]" />}
            </div>
          ))}
        </div>

        <AnimatePresence mode="wait">
          {/* ─── STEP 1: FORM ─── */}
          {step === "form" && (
            <motion.div key="form" initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} transition={{ duration: 0.35 }}>
              <h1 className="text-[28px] sm:text-[36px] font-bold tracking-[-0.02em] text-[#1a1b1c] mb-2 text-center">Tell us about yourself</h1>
              <p className="text-[#5f6468] text-[15px] mb-10 text-center">This helps our AI tailor the perfect glow-up plan for you.</p>

              <div className="space-y-6 max-w-[480px] mx-auto">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-[13px] font-medium text-[#5f6468] mb-1.5">Age</label>
                    <input type="number" min={13} max={120} value={age} onChange={(e) => setAge(e.target.value)}
                      className="w-full rounded-xl border border-[#e0e1e2] px-4 py-3 text-[14px] focus:outline-none focus:ring-2 focus:ring-[#1a1b1c]/10 focus:border-[#c0c1c2] transition-all"
                      placeholder="25" />
                  </div>
                  <div>
                    <label className="block text-[13px] font-medium text-[#5f6468] mb-1.5">Gender</label>
                    <select value={gender} onChange={(e) => setGender(e.target.value)}
                      className="w-full rounded-xl border border-[#e0e1e2] px-4 py-3 text-[14px] focus:outline-none focus:ring-2 focus:ring-[#1a1b1c]/10 focus:border-[#c0c1c2] transition-all bg-white appearance-none">
                      <option value="">Select...</option>
                      <option value="male">Male</option>
                      <option value="female">Female</option>
                      <option value="other">Other</option>
                    </select>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-[13px] font-medium text-[#5f6468] mb-1.5">Ethnicity</label>
                    <input type="text" value={ethnicity} onChange={(e) => setEthnicity(e.target.value)}
                      className="w-full rounded-xl border border-[#e0e1e2] px-4 py-3 text-[14px] focus:outline-none focus:ring-2 focus:ring-[#1a1b1c]/10 focus:border-[#c0c1c2] transition-all"
                      placeholder="e.g. Caucasian, Asian..." />
                  </div>
                  <div>
                    <label className="block text-[13px] font-medium text-[#5f6468] mb-1.5">Skin Type</label>
                    <select value={skinType} onChange={(e) => setSkinType(e.target.value)}
                      className="w-full rounded-xl border border-[#e0e1e2] px-4 py-3 text-[14px] focus:outline-none focus:ring-2 focus:ring-[#1a1b1c]/10 focus:border-[#c0c1c2] transition-all bg-white appearance-none">
                      <option value="">Select...</option>
                      <option value="dry">Dry</option>
                      <option value="oily">Oily</option>
                      <option value="combination">Combination</option>
                      <option value="normal">Normal</option>
                      <option value="sensitive">Sensitive</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-[13px] font-medium text-[#5f6468] mb-3">Glow-Up Goals</label>
                  <div className="flex flex-wrap gap-2">
                    {GOALS.map((g) => (
                      <button key={g} onClick={() => toggleGoal(g)}
                        className={`px-4 py-2 rounded-full text-[13px] font-medium transition-all duration-200 ${
                          goals.includes(g) ? "bg-[#1a1b1c] text-white" : "bg-[#f0f1f2] text-[#5f6468] hover:bg-[#e4e5e6]"
                        }`}>{g}</button>
                    ))}
                  </div>
                </div>

                <button onClick={() => setStep("upload")} disabled={!age || !gender || !ethnicity || !skinType}
                  className="btn-dark w-full !py-3.5 text-[15px]">
                  Next: Upload Photos <ArrowRight className="w-4 h-4 ml-1.5" />
                </button>
              </div>
            </motion.div>
          )}

          {/* ─── STEP 2: UPLOAD ─── */}
          {step === "upload" && (
            <motion.div key="upload" initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} transition={{ duration: 0.35 }}>
              <h1 className="text-[28px] sm:text-[36px] font-bold tracking-[-0.02em] text-[#1a1b1c] mb-2 text-center">Upload Your Photos</h1>
              <p className="text-[#5f6468] text-[15px] mb-10 text-center">Follow the guide for each angle. Good lighting, plain background, no filters.</p>

              <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mb-8">
                {GUIDED_ANGLES.map((a) => {
                  const has = photos[a.id];
                  return (
                    <PhotoSlot
                      key={a.id}
                      angle={a}
                      hasPhoto={!!has}
                      preview={has ? URL.createObjectURL(has) : null}
                      onDrop={onDrop(a.id)}
                      onRemove={() => removePhoto(a.id)}
                    />
                  );
                })}
              </div>

              {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 rounded-xl p-4 text-[13px] mb-6">{error}</div>
              )}

              <button onClick={handleSubmit} disabled={!allDone} className="btn-dark w-full !py-3.5 text-[15px]">
                {allDone ? "Start AI Analysis" : `Upload ${6 - Object.keys(photos).length} more photo${Object.keys(photos).length === 5 ? "" : "s"}`}
              </button>
            </motion.div>
          )}

          {/* ─── STEP 3: PROCESSING ─── */}
          {step === "processing" && (
            <motion.div key="processing" initial={{ opacity: 0, scale: 0.98 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.4 }}
              className="text-center py-16">
              <motion.div animate={{ y: [0, -8, 0] }} transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
                className="w-16 h-16 rounded-2xl bg-[#f0f1f2] flex items-center justify-center mx-auto mb-6">
                <svg className="w-8 h-8 text-[#5f6468]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1}>
                  <path strokeLinecap="round" strokeLinejoin="round"
                    d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.455 2.456L21.75 6l-1.036.259a3.375 3.375 0 00-2.455 2.456z" />
                </svg>
              </motion.div>
              <h2 className="text-[24px] font-bold text-[#1a1b1c] mb-2">Analyzing Your Face</h2>
              <p className="text-[#5f6468] text-[14px] mb-8">
                Measuring 478 facial landmarks, assessing skin health,
                <br />generating your personalized protocol.
              </p>
              <div className="max-w-[320px] mx-auto">
                <div className="h-1.5 bg-[#f0f1f2] rounded-full overflow-hidden">
                  <motion.div className="h-full bg-[#1a1b1c] rounded-full"
                    animate={{ width: ["0%", "40%", "70%", "90%", "100%"] }}
                    transition={{ duration: 8, times: [0, 0.2, 0.5, 0.8, 1], ease: "easeInOut" }} />
                </div>
                <p className="text-[12px] text-[#b0b1b2] mt-3">This takes about 3-5 minutes...</p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </main>
  );
}

// ─── PHOTO SLOT COMPONENT ───

function PhotoSlot({
  angle, hasPhoto, preview, onDrop, onRemove,
}: {
  angle: { id: string; label: string; desc: string };
  hasPhoto: boolean;
  preview: string | null;
  onDrop: (files: File[]) => void;
  onRemove: () => void;
}) {
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "image/*": [".jpg", ".jpeg", ".png", ".webp"] },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024,
  });

  return (
    <div
      {...getRootProps()}
      className={`relative aspect-[3/4] rounded-xl border-2 border-dashed transition-all duration-200 cursor-pointer overflow-hidden ${
        isDragActive ? "border-[#1a1b1c] bg-[#f8f9f9]"
          : hasPhoto ? "border-green-300 bg-green-50/30"
          : "border-[#e0e1e2] hover:border-[#c0c1c2] bg-white"
      }`}
    >
      <input {...getInputProps()} />
      {hasPhoto && preview ? (
        <>
          <img src={preview} alt={angle.label} className="w-full h-full object-cover" />
          <button onClick={(e) => { e.stopPropagation(); onRemove(); }}
            className="absolute top-2 right-2 w-7 h-7 bg-white rounded-full flex items-center justify-center shadow-sm hover:bg-red-50 transition-colors">
            <X className="w-3.5 h-3.5 text-red-500" />
          </button>
          <div className="absolute bottom-2 left-2 bg-green-500 text-white text-[11px] font-medium px-2 py-0.5 rounded-full flex items-center gap-1">
            <Check className="w-3 h-3" /> Done
          </div>
        </>
      ) : (
        <div className="flex flex-col items-center justify-center h-full p-3 text-center">
          <Camera className="w-6 h-6 text-[#c0c1c2] mb-2" />
          <span className="text-[13px] font-medium text-[#5f6468]">{angle.label}</span>
          <span className="text-[11px] text-[#b0b1b2] mt-1 leading-tight">{angle.desc}</span>
        </div>
      )}
    </div>
  );
}
