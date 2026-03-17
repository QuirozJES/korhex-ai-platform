/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'hpe-bg': '#141517',
        'hpe-sidebar': '#1a1d21',
        'hpe-panel': '#22252a',
        'hpe-border': '#32363d',
        'hpe-green': '#01A982',
        'hpe-green-hover': '#008C6B',
      }
    },
  },
  plugins: [],
}
