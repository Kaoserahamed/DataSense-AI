/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class"],
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        indigo: {
          400: '#818cf8',
          500: '#6366f1',
          600: '#4f46e5',
        },
        cyan: {
          400: '#22d3ee',
          500: '#06b6d4',
        },
        slate: {
          750: '#1a2540',
          850: '#131c30',
          900: '#0f172a',
          950: '#080e1a',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      boxShadow: {
        'indigo': '0 0 0 1px rgba(99,102,241,0.3), 0 4px 24px rgba(99,102,241,0.15)',
        'card': '0 1px 3px rgba(0,0,0,0.07), 0 1px 2px rgba(0,0,0,0.04)',
      },
      backdropBlur: {
        md: '12px',
      },
    },
  },
  plugins: [],
}
