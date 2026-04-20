import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        background: "#0a0f1e",
        foreground: "#e2e8f0",
        accent: {
          cyan: "#10b981",
          blue: "#3b82f6",
          violet: "#8b5cf6",
        },
      },
      fontFamily: {
        sans: ["system-ui", "-apple-system", "sans-serif"],
      },
    },
  },
  plugins: [],
};

export default config;
