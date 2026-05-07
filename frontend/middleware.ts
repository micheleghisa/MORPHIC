import { NextRequest, NextResponse } from "next/server";

// In-memory rate limit store (production: use Upstash Redis)
const rateMap = new Map<string, { count: number; resetAt: number }>();

export function rateLimit(limit: number = 10, windowMs: number = 60000) {
  return async (request: NextRequest) => {
    const ip = request.headers.get("x-forwarded-for") || request.headers.get("x-real-ip") || "unknown";
    const key = `${ip}:${request.nextUrl.pathname}`;
    const now = Date.now();

    const entry = rateMap.get(key);
    if (!entry || now > entry.resetAt) {
      rateMap.set(key, { count: 1, resetAt: now + windowMs });
      return NextResponse.next();
    }

    entry.count++;
    if (entry.count > limit) {
      return NextResponse.json(
        { error: "Too many requests. Please try again later." },
        { status: 429, headers: { "Retry-After": String(Math.ceil((entry.resetAt - now) / 1000)) } }
      );
    }

    return NextResponse.next();
  };
}

// Apply rate limiting to API routes
export async function middleware(request: NextRequest) {
  if (request.nextUrl.pathname.startsWith("/api/v1/analyze")) {
    return rateLimit(5, 60000)(request); // 5 analyses per minute per IP
  }
  if (request.nextUrl.pathname.startsWith("/api/stripe")) {
    return rateLimit(10, 60000)(request); // 10 stripe requests per minute
  }
  return NextResponse.next();
}

export const config = {
  matcher: ["/api/:path*"],
};
