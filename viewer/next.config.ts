import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  // react-force-graph-3d ships ESM; transpile if Next complains
  transpilePackages: ["react-force-graph-3d", "three-spritetext"],
};

export default nextConfig;
