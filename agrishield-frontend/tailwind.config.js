/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        field: {
          950: "#081210",
          900: "#0B1410",
          800: "#101D18",
          700: "#182920",
        },
        canopy: {
          DEFAULT: "#22C55E",
          600: "#16A34A",
          700: "#15803D",
        },
        sky: {
          DEFAULT: "#2563EB",
        },
        clay: "#D97706",
        alert: "#DC2626",
        mist: "#F5F7F5",
      },
      fontFamily: {
        display: ["'Space Grotesk'", "sans-serif"],
        body: ["'Inter'", "sans-serif"],
        mono: ["'JetBrains Mono'", "monospace"],
      },
      backgroundImage: {
        rows: "repeating-linear-gradient(0deg, rgba(34,197,94,0.07) 0px, rgba(34,197,94,0.07) 1px, transparent 1px, transparent 28px)",
      },
      keyframes: {
        scan: {
          "0%": { transform: "translateY(-100%)" },
          "100%": { transform: "translateY(100%)" },
        },
        rise: {
          "0%": { opacity: 0, transform: "translateY(14px)" },
          "100%": { opacity: 1, transform: "translateY(0)" },
        },
      },
      animation: {
        scan: "scan 3.5s linear infinite",
        rise: "rise 0.5s ease-out both",
      },
    },
  },
  plugins: [],
};
