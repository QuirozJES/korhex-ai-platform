/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'obsidian-bg': '#0c0d0f',
        'obsidian-surface-1': '#111214',
        'obsidian-surface-2': '#161719',
        'obsidian-border': '#1f2022',
        'obsidian-border-light': '#25272a',
        'korhex-green': '#01A982',
        'korhex-mint': '#59dcb2',
        'korhex-text': '#9ca3af',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['Space Grotesk', 'monospace'],
      },
      animation: {
        'slide-up-fade': 'slideUpFade 0.3s ease-out forwards',
        'staggered-fade-in': 'fadeIn 0.4s ease-out forwards',
        'pulse-scan': 'pulseScan 3s ease-in-out infinite',
      },
      keyframes: {
        slideUpFade: {
          '0%': { opacity: 0, transform: 'translateY(10px)' },
          '10%': { opacity: 0, transform: 'translateY(10px)' },
          '100%': { opacity: 1, transform: 'translateY(0)' },
        },
        fadeIn: {
          '0%': { opacity: 0 },
          '100%': { opacity: 1 },
        },
        pulseScan: {
          '0%, 100%': { opacity: 1 },
          '50%': { opacity: 0.6 },
        }
      }
    },
  },
  plugins: [],
}
