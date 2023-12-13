/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/templates/**/*.html",
    "./app/static/src/**/*.js"
  ],
  theme: {
    colors: {
      transparent: 'transparent',
      current: 'currentColor',
      'white': '#fefcfb',
      'amber': '#f2bb05',
      'burnt-sienna': '#ec7357',
    },
  },
  plugins: [],
}