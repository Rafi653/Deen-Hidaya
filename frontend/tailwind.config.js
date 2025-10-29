/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        arabic: ['Amiri', 'serif'],
      },
      colors: {
        // Brand color palette
        brand: {
          primary: '#16a34a', // green-600
          'primary-dark': '#15803d', // green-700
          'primary-light': '#22c55e', // green-500
          secondary: '#2563eb', // blue-600
          'secondary-dark': '#1d4ed8', // blue-700
          'secondary-light': '#3b82f6', // blue-500
          accent: '#eab308', // yellow-500
        },
      },
    },
  },
  plugins: [],
}
