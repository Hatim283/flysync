/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#1D4ED8", // Royal Blue
        success: "#10B981", // Emerald
        warning: "#F59E0B", // Amber
        background: "#0E1117",
        foreground: "#FFFFFF",
        surface: "#1F2937",
        border: "#374151"
      }
    },
  },
  plugins: [],
};
