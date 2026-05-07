import { NextRequest, NextResponse } from "next/server";

// Stripe Checkout session creator
// Requires STRIPE_SECRET_KEY in .env.local

export async function POST(request: NextRequest) {
  const formData = await request.formData();
  const plan = formData.get("plan") as string;

  // In production, use actual Stripe Price IDs
  const priceIds: Record<string, string> = {
    "one-time": process.env.STRIPE_PRICE_ONETIME || "price_placeholder_one_time",
    annual: process.env.STRIPE_PRICE_ANNUAL || "price_placeholder_annual",
  };

  const priceId = priceIds[plan] || priceIds["one-time"];

  try {
    const stripeKey = process.env.STRIPE_SECRET_KEY;

    if (!stripeKey) {
      // Stripe not configured — redirect to thank-you as demo mode
      return NextResponse.redirect(new URL("/upload?demo=true", request.url));
    }

    // Dynamic import to avoid build issues when Stripe key missing
    const { default: Stripe } = await import("stripe");
    const stripe = new Stripe(stripeKey);

    const session = await stripe.checkout.sessions.create({
      line_items: [{ price: priceId, quantity: 1 }],
      mode: plan === "annual" ? "subscription" : "payment",
      success_url: `${request.nextUrl.origin}/upload?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${request.nextUrl.origin}/pricing`,
      metadata: { plan },
    });

    return NextResponse.redirect(session.url || "/pricing");
  } catch (error) {
    console.error("Stripe error:", error);
    // Fallback: redirect to upload with demo mode
    return NextResponse.redirect(new URL("/upload?demo=true", request.url));
  }
}
