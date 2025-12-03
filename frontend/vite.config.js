import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";

export default defineConfig({
  plugins: [react()],
  envDir: '../',
  server: {
    port: process.env.VITE_PORT,
    proxy: {
      "/api": process.env.VITE_API_BASE,
    }
  }
});
