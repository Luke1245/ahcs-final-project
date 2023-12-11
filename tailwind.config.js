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
      'cerulean': '#1282a2',
      'thistle': '#dec5e3',
      'penn-blue': '#001f54',
      'oxford-blue': '#0a1128',
    },
  },
  plugins: [],
}