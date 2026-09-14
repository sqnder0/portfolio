tailwind.config = {
  theme: {
    extend: {
      colors: {
        ink: "#e2e8f0",
        slateBlue: "#0b1220",
        panel: "rgba(15, 23, 42, 0.72)",
        panelStrong: "rgba(15, 23, 42, 0.92)",
        line: "rgba(148, 163, 184, 0.22)",
        accent: "#88f2d5",
        accentDeep: "#1f8ea3",
        warm: "#f8c07d",
        danger: "#ff8c8c",
      },
      fontFamily: {
        sans: ["Space Grotesk", "sans-serif"],
        mono: ["IBM Plex Mono", "monospace"],
      },
      boxShadow: {
        glow: "0 0 35px rgba(136, 242, 213, 0.18)",
      },
      animation: {
        enter: "enter 0.6s ease-out forwards",
      },
      keyframes: {
        enter: {
          "0%": { opacity: "0", transform: "translateY(12px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
      },
    },
  },
};
