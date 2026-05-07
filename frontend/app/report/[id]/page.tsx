"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import ReactMarkdown from "react-markdown";
import { motion, AnimatePresence } from "framer-motion";
import { Download, MessageCircle, Eye, Shield, Send } from "lucide-react";
import { API_BASE_URL, getScoreColor, getScoreBg, getScoreLabel } from "@/lib/utils";
import BeforeAfterSlider from "@/components/ui/BeforeAfterSlider";

interface ReportData {
  status: string;
  report?: { report_markdown: string; report_json: any; provider: string };
  biometric_data?: any;
  skin_metrics?: any;
  visualizations?: Record<string, string>;
  original_photo?: string;
  processing_time_seconds?: number;
}

function ScoreCard({ label, score }: { label: string; score: number }) {
  return (
    <div className={`${getScoreBg(score)} rounded-2xl p-5 text-center`}>
      <div className={`text-[32px] font-bold tracking-[-0.02em] ${getScoreColor(score)} mb-1`}>{score}</div>
      <div className="text-[13px] font-medium text-[#5f6468]">{label}</div>
      <div className={`text-[11px] ${getScoreColor(score)} mt-0.5`}>{getScoreLabel(score)}</div>
    </div>
  );
}

const METRIC_TOOLTIPS: Record<string, string> = {
  "Facial Index": "Ratio of face height to bizygomatic width. <84 = wide face, 84-89 = balanced, >89 = long face.",
  "Upper Third": "Forehead height as % of total face. Ideal ~33%. Higher = long forehead, lower = short forehead.",
  "Middle Third": "Nose height as % of total face. Ideal ~33%. Deviation affects facial harmony.",
  "Lower Third": "Jaw/chin height as % of total face. Ideal ~33%. Key for jawline aesthetics.",
  "Jaw Angle": "Angle formed at the chin between left and right jawline. ~80-95° is typical. Wider = rounder face.",
  "Canthal Tilt": "Angle of the eye corners. Positive = upturned (\"cat eyes\"), negative = downturned. -5° to +8° is typical range.",
  "Eyes": "How symmetric your eyes are in position and shape. Higher = more balanced appearance.",
  "Brows": "How symmetric your eyebrows are. Brow asymmetry can significantly impact perceived facial harmony.",
  "Nose": "How symmetric your nose is relative to facial midline. Even slight deviations are common.",
  "Lips": "How symmetric your lip line is. Lip asymmetry can affect smile aesthetics.",
  "Jaw": "How symmetric your jawline is. Jaw asymmetry often relates to chewing habits or dental alignment.",
  "Face Shape": "Classification based on facial proportions: Oval, Round, Square, Heart, Diamond, Triangle, Rectangle, Oblong.",
  "M/F Score": "Masculinity/Femininity score based on bone structure. >50 = more masculine traits, <50 = more feminine traits.",
};

function MetricRow({ label, value, unit = "" }: { label: string; value: number | string; unit?: string }) {
  const tooltip = METRIC_TOOLTIPS[label];
  return (
    <div className="flex justify-between items-center py-2.5 border-b border-[#f0f0f1] last:border-0 group relative">
      <span className="text-[13px] text-[#5f6468] cursor-help border-b border-dotted border-[#c0c1c2]">{label}</span>
      <span className="text-[13px] font-medium text-[#1a1b1c]">
        {typeof value === "number" ? value.toFixed(1) : value}{unit}
      </span>
      {tooltip && (
        <div className="absolute bottom-full left-0 mb-2 w-56 p-3 bg-[#1a1b1c] text-white text-[11px] leading-relaxed rounded-xl shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50 pointer-events-none">
          {tooltip}
          <div className="absolute top-full left-4 w-2 h-2 bg-[#1a1b1c] rotate-45 -mt-1" />
        </div>
      )}
    </div>
  );
}

export default function ReportPage() {
  const params = useParams();
  const analysisId = params.id as string;
  const [data, setData] = useState<ReportData | null>(null);
  const [loading, setLoading] = useState(true);
  const [chatMessage, setChatMessage] = useState("");
  const [chatHistory, setChatHistory] = useState<{ role: string; content: string }[]>([]);
  const [activeTab, setActiveTab] = useState<"report" | "chat">("report");

  useEffect(() => {
    async function fetchReport() {
      try {
        const statusRes = await fetch(`${API_BASE_URL}/api/v1/analysis/${analysisId}`);
        if (statusRes.ok) {
          const status = await statusRes.json();
          const reportJson = status.report?.report_json || {};
          setData({
            status: status.status,
            report: {
              report_markdown: reportJson.markdown_report || "",
              report_json: reportJson,
              provider: status.report?.provider || "",
            },
            biometric_data: status.biometric_data || {},
            skin_metrics: status.skin_metrics || {},
            visualizations: status.visualizations || {},
            original_photo: status.original_photo || "",
            processing_time_seconds: status.processing_time_seconds,
          });
        }
      } catch (err) { console.error(err); }
      finally { setLoading(false); }
    }
    if (analysisId) fetchReport();
  }, [analysisId]);

  const sendChat = async () => {
    if (!chatMessage.trim()) return;
    const newHistory = [...chatHistory, { role: "user", content: chatMessage }];
    setChatHistory(newHistory); setChatMessage("");
    try {
      const fd = new FormData();
      fd.append("question", chatMessage);
      fd.append("analysis_id", analysisId);
      fd.append("history", JSON.stringify(chatHistory));
      const res = await fetch(`${API_BASE_URL}/api/v1/chat`, { method: "POST", body: fd });
      const r = await res.json();
      setChatHistory([...newHistory, { role: "assistant", content: r.response }]);
    } catch (err) { console.error(err); }
  };

  const handleDownload = () => {
    if (!data?.report?.report_markdown) return;
    const blob = new Blob([data.report.report_markdown], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url; a.download = `morphic-report-${analysisId}.md`; a.click();
    URL.revokeObjectURL(url);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-white">
        <div className="text-center">
          <motion.div animate={{ y: [0, -6, 0] }} transition={{ duration: 2, repeat: Infinity }}
            className="w-12 h-12 rounded-xl bg-[#f0f1f2] mx-auto mb-4" />
          <p className="text-[#8b9094] text-[14px]">Loading your report...</p>
        </div>
      </div>
    );
  }

  if (!data?.report) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-white">
        <div className="text-center">
          <p className="text-[#5f6468] mb-4">Report is being generated...</p>
          <Link href="/" className="btn-dark">Go Home</Link>
        </div>
      </div>
    );
  }

  const biometrics = data.biometric_data || {};
  const skin = data.skin_metrics || {};

  return (
    <main className="min-h-screen bg-white">
      {/* HEADER */}
      <header className="border-b border-[#e8e9ea] sticky top-0 z-40 bg-white/90 backdrop-blur-xl">
        <div className="container-page flex items-center justify-between h-[64px]">
          <Link href="/" className="flex items-center gap-2">
            <span className="text-[20px] font-bold tracking-[-0.02em] text-[#1a1b1c]">MORPHIC</span>
            <span className="hidden sm:inline text-[11px] uppercase tracking-[0.2em] text-[#8b9094] font-medium mt-0.5">Lab</span>
          </Link>
          <button onClick={handleDownload} className="btn-ghost text-[13px]">
            <Download className="w-4 h-4 mr-1.5" /> Export
          </button>
        </div>
      </header>

      <div className="container-page py-8 max-w-5xl">
        {/* HERO */}
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="text-center mb-10">
          <div className="inline-flex items-center gap-1.5 bg-green-50 text-green-700 text-[13px] font-medium px-3.5 py-1.5 rounded-full mb-4">
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}><path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" /></svg>
            Analysis Complete
          </div>
          <h1 className="text-[28px] sm:text-[36px] font-bold tracking-[-0.02em] text-[#1a1b1c] mb-2">Your Glow-Up Report</h1>
          <p className="text-[#8b9094] text-[14px]">
            Generated in {data.processing_time_seconds?.toFixed(0) || "—"}s via {data.report?.provider || "AI"}
          </p>
        </motion.div>

        {/* SCORE CARDS */}
        {biometrics.symmetry && (
          <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
            className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-10">
            <ScoreCard label="Symmetry" score={biometrics.symmetry.overall_symmetry || 0} />
            <ScoreCard label="Skin Health" score={skin.overall_skin_health || 0} />
            <ScoreCard label="Facial Harmony" score={
              biometrics.proportions ? Math.round(100 - Math.abs((biometrics.proportions.upper_third_ratio || 0.33) * 100 - 33) * 2) : 0
            } />
            <ScoreCard label="Confidence" score={85} />
          </motion.div>
        )}

        {/* TABS */}
        <div className="flex gap-1 bg-[#f8f9f9] rounded-2xl p-1 border border-[#e8e9ea] mb-8">
          {[
            { id: "report" as const, label: "Report", icon: Eye },
            { id: "chat" as const, label: "AI Assistant", icon: MessageCircle },
          ].map((tab) => (
            <button key={tab.id} onClick={() => setActiveTab(tab.id)}
              className={`flex-1 flex items-center justify-center gap-2 py-3 rounded-xl text-[13px] font-medium transition-all duration-200 ${
                activeTab === tab.id ? "bg-white text-[#1a1b1c] shadow-sm" : "text-[#8b9094] hover:text-[#5f6468]"
              }`}>
              <tab.icon className="w-4 h-4" />
              <span className="hidden sm:inline">{tab.label}</span>
            </button>
          ))}
        </div>

        {/* TAB: REPORT */}
        <AnimatePresence mode="wait">
          {activeTab === "report" && (
            <motion.div key="report" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
              className="grid lg:grid-cols-3 gap-8">
              <div className="lg:col-span-1">
                <div className="bg-[#f8f9f9] rounded-2xl border border-[#e8e9ea] p-6 sticky top-24">
                  <h3 className="text-[15px] font-semibold text-[#1a1b1c] mb-4">Biometric Scores</h3>
                  {biometrics.proportions && (
                    <div className="mb-5">
                      <p className="text-[10px] uppercase tracking-[0.15em] text-[#b0b1b2] font-medium mb-2">Proportions</p>
                      <MetricRow label="Facial Index" value={biometrics.proportions.facial_index} />
                      <MetricRow label="Upper Third" value={(biometrics.proportions.upper_third_ratio * 100).toFixed(1)} unit="%" />
                      <MetricRow label="Middle Third" value={(biometrics.proportions.middle_third_ratio * 100).toFixed(1)} unit="%" />
                      <MetricRow label="Lower Third" value={(biometrics.proportions.lower_third_ratio * 100).toFixed(1)} unit="%" />
                      <MetricRow label="Jaw Angle" value={biometrics.proportions.jaw_angle} unit="°" />
                      <MetricRow label="Canthal Tilt" value={biometrics.canthal_tilt_degrees} unit="°" />
                    </div>
                  )}
                  {biometrics.symmetry && (
                    <div className="mb-5">
                      <p className="text-[10px] uppercase tracking-[0.15em] text-[#b0b1b2] font-medium mb-2">Symmetry</p>
                      <MetricRow label="Eyes" value={biometrics.symmetry.eye_symmetry} unit="/100" />
                      <MetricRow label="Brows" value={biometrics.symmetry.brow_symmetry} unit="/100" />
                      <MetricRow label="Nose" value={biometrics.symmetry.nose_symmetry} unit="/100" />
                      <MetricRow label="Lips" value={biometrics.symmetry.lip_symmetry} unit="/100" />
                      <MetricRow label="Jaw" value={biometrics.symmetry.jaw_symmetry} unit="/100" />
                    </div>
                  )}
                  <div>
                    <p className="text-[10px] uppercase tracking-[0.15em] text-[#b0b1b2] font-medium mb-2">Additional</p>
                    <MetricRow label="Face Shape" value={biometrics.face_shape || "—"} />
                    <MetricRow label="M/F Score" value={biometrics.masculinity_femininity_score || "—"} unit="/100" />
                  </div>
                </div>
              </div>
              <div className="lg:col-span-2">
                <div className="bg-white rounded-2xl border border-[#e8e9ea] p-8">
                  <article className="prose prose-gray max-w-none prose-headings:text-[#1a1b1c] prose-p:text-[#5f6468] prose-strong:text-[#1a1b1c] prose-li:text-[#5f6468] text-[14px]">
                    <ReactMarkdown>{data.report.report_markdown}</ReactMarkdown>
                  </article>
                </div>
              </div>
            </motion.div>
          )}

          {/* TAB: VISUALIZATIONS */}

          {activeTab === "chat" && (
            <motion.div key="chat" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
              className="max-w-2xl mx-auto">
              <div className="bg-white rounded-2xl border border-[#e8e9ea]">
                <div className="h-96 overflow-y-auto p-6 space-y-4">
                  {chatHistory.length === 0 && (
                    <div className="text-center py-12">
                      <MessageCircle className="w-10 h-10 text-[#d0d1d2] mx-auto mb-3" />
                      <p className="text-[14px] text-[#8b9094]">Ask questions about your analysis,<br />recommendations, or your report.</p>
                    </div>
                  )}
                  {chatHistory.map((msg, i) => (
                    <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                      <div className={`max-w-[80%] rounded-2xl px-4 py-3 text-[13px] ${
                        msg.role === "user" ? "bg-[#1a1b1c] text-white rounded-br-md" : "bg-[#f0f1f2] text-[#1a1b1c] rounded-bl-md"
                      }`}>{msg.content}</div>
                    </div>
                  ))}
                </div>
                <div className="border-t border-[#e8e9ea] p-4 flex gap-2">
                  <input type="text" value={chatMessage} onChange={(e) => setChatMessage(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && sendChat()} placeholder="Ask about your results..."
                    className="flex-1 rounded-xl border border-[#e0e1e2] px-4 py-2.5 text-[13px] focus:outline-none focus:ring-2 focus:ring-[#1a1b1c]/10" />
                  <button onClick={sendChat} className="btn-dark !p-2.5"><Send className="w-4 h-4" /></button>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </main>
  );
}
