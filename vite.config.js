import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  base: "/build-a-modern-real-estate-property-management-portal-the-application-must-be-se-5ca14a/",
  build: { outDir: "dist", assetsDir: "assets" },
  server: { port: 3000 },
});
