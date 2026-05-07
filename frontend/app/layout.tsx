import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import CookieConsent from "@/components/ui/CookieConsent";

const inter = Inter({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "MORPHIC — Science-Based Facial Analysis & Glow Up Without Surgery",
  description:
    "Get a personalized facial analysis based on 2,000+ academic studies. Objective beauty advice and a non-surgical transformation protocol tailored to your face.",
  keywords: [
    "facial analysis",
    "glow up",
    "facial aesthetics",
    "non-surgical",
    "science-based beauty",
    "face analysis",
    "morphic",
  ],
  authors: [{ name: "MORPHIC" }],
  creator: "MORPHIC",
  publisher: "MORPHIC",
  metadataBase: new URL("https://morphic.ai"),
  openGraph: {
    type: "website",
    locale: "en_US",
    siteName: "MORPHIC",
    title: "MORPHIC — Science-Based Facial Analysis",
    description:
      "Get a personalized facial analysis based on 2,000+ academic studies. Non-surgical glow up, 100% AI-powered.",
  },
  twitter: {
    card: "summary_large_image",
    title: "MORPHIC — Science-Based Facial Analysis",
    description: "Get a personalized facial analysis and non-surgical transformation protocol.",
  },
  robots: { index: true, follow: true },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={inter.variable}>
      <body className="min-h-screen bg-white font-sans antialiased">
        {children}
        <CookieConsent />
      </body>
    </html>
  );
}
