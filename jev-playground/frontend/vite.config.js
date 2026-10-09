import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Dev:  `npm run dev` serves on :5173 and proxies /api to FastAPI on :8000.
// Prod: `npm run build` writes into backend/static, which FastAPI serves.
export default defineConfig({
  plugins: [react()],
  build: {
    outDir: "../backend/static",
    emptyOutDir: true,
  },
  server: {
    port: 5173,
    proxy: { "/api": "http://localhost:8000" },
  },
});
