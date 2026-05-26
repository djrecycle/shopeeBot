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
        shopee: '#FF4D2D',
        shopeeHover: '#E03E20',
        darkBg: '#0A0A0C',
        darkCard: '#16161A',
        darkBorder: 'rgba(255, 255, 255, 0.08)',
        glassBg: 'rgba(255, 255, 255, 0.03)'
      },
      fontFamily: {
        sans: ['Outfit', 'Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
};
