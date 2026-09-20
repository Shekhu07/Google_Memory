import type { NextConfig } from "next";

// Local verification only. Set PROXY_PY=1 to forward /api/py/* to a retrieval service
// on 127.0.0.1:8000. On Vercel this is never set: webapp/vercel.json owns that route.
const nextConfig: NextConfig = {
  async rewrites() {
    if (process.env.PROXY_PY !== "1") return [];
    return [{ source: "/api/py/:path*", destination: "http://127.0.0.1:8000/:path*" }];
  },
};

export default nextConfig;
