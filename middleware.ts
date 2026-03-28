// middleware.ts
import { NextRequest, NextResponse } from "next/server";

export function middleware(req: NextRequest) {
  // Optional: tell search engines to ignore the site
  const res = NextResponse.next();
  res.headers.set("X-Robots-Tag", "noindex, nofollow");

  const user = process.env.BASIC_AUTH_USER;
  const pass = process.env.BASIC_AUTH_PASS;

  // If not configured, let requests through (so local dev doesn't block you)
  if (!user || !pass) return res;

  const header = req.headers.get("authorization") || "";
  const [scheme, encoded] = header.split(" ");

  if (scheme === "Basic" && encoded) {
    // Edge runtime has atob()
    const decoded = atob(encoded);
    const [u, p] = decoded.split(":");
    if (u === user && p === pass) return res;
  }

  return new NextResponse("Authentication required", {
    status: 401,
    headers: { "WWW-Authenticate": 'Basic realm="Flo-Fi"' },
  });
}

// Protect everything except Next static assets & robots
export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|robots.txt).*)"],
};
