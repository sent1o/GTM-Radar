import type { Config } from "tailwindcss";
import colors from "tailwindcss/colors";

const config: Config = {
  content: ["./app/**/*.{js,ts,jsx,tsx}", "./components/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#15233A",
        slate: { ...colors.slate, DEFAULT: "#60708A" },
        canvas: "#F7F8FC",
        radar: "#615FFF",
        mint: "#DDF8E8"
      },
      boxShadow: {
        card: "0 2px 5px rgba(21, 35, 58, 0.04), 0 16px 32px rgba(21, 35, 58, 0.04)"
      }
    }
  },
  plugins: []
};

export default config;
