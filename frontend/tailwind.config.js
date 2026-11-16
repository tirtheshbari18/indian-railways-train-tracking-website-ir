/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        railway: {
          dark: '#081627',
          navy: '#0c2340',
          blue: '#133e68',
          lightBlue: '#1e5a96',
          maroon: '#800020',
          crimson: '#9b111e',
          amber: '#d97706',
          gold: '#f59e0b',
          green: '#059669',
          lightGreen: '#10b981',
          surface: '#0f172a',
          card: '#1e293b'
        }
      }
    },
  },
  plugins: [],
}
