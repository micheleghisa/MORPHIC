import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(date: string | Date): string {
  return new Date(date).toLocaleDateString("en-US", {
    month: "long",
    day: "numeric",
    year: "numeric",
  });
}

export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(amount);
}

export function getScoreColor(score: number): string {
  if (score >= 85) return "text-green-600";
  if (score >= 70) return "text-yellow-600";
  if (score >= 50) return "text-orange-600";
  return "text-red-600";
}

export function getScoreBg(score: number): string {
  if (score >= 85) return "bg-green-50";
  if (score >= 70) return "bg-yellow-50";
  if (score >= 50) return "bg-orange-50";
  return "bg-red-50";
}

export function getScoreLabel(score: number): string {
  if (score >= 90) return "Excellent";
  if (score >= 80) return "Very Good";
  if (score >= 70) return "Good";
  if (score >= 60) return "Above Average";
  if (score >= 50) return "Average";
  if (score >= 40) return "Below Average";
  return "Needs Attention";
}

export function getFaceShapeLabel(shape: string): string {
  const labels: Record<string, string> = {
    oval: "Oval",
    round: "Round",
    square: "Square",
    heart: "Heart",
    diamond: "Diamond",
    triangle: "Triangle",
    rectangle: "Rectangle",
    oblong: "Oblong",
  };
  return labels[shape] || shape;
}

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";
