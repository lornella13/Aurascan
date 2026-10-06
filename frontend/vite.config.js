import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { VitePWA } from "vite-plugin-pwa";

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: "autoUpdate",
      includeAssets: ["favicon.svg", "apple-touch-icon.png"],
      manifest: {
        name: "AuraScan",
        short_name: "AuraScan",
        description: "Scan your face and outfit to get makeup, clothing and colour recommendations.",
        start_url: "/",
        display: "standalone",
        orientation: "portrait",
        theme_color: "#1C1530",
        background_color: "#EFEBF5",
        icons: [
          { src: "icon-192.png", sizes: "192x192", type: "image/png" },
          { src: "icon-512.png", sizes: "512x512", type: "image/png" },
          { src: "icon-maskable-512.png", sizes: "512x512", type: "image/png", purpose: "maskable" },
        ],
      },
      workbox: {
        // The app shell is cached; API calls always go to the network.
        navigateFallbackDenylist: [/^\/api/],
      },
    }),
  ],
  server: {
    proxy: { "/api": "http://localhost:8000" },
  },
});
