import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Local development only. In production, webapp/vercel.json routes /api/py/* to the
  // retrieval service; this rewrite never applies there.
  async rewrites() {
    if (process.env.NODE_ENV === "production") return [];
    return [{ source: "/api/py/:path*", destination: "http://127.0.0.1:8000/:path*" }];
  },
};

export default nextConfig;
