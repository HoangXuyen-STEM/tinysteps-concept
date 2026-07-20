import { defineConfig } from "vitest/config";
import path from "path";

export default defineConfig({
  test: {
    globals: true,
    environment: "node",
    include: ["**/__tests__/**/*.test.ts"],
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "."),
      // See test/server-only-stub.ts for why this alias exists.
      "server-only": path.resolve(__dirname, "test/server-only-stub.ts"),
    },
  },
});
