module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
    "./node_modules/flowbite/**/*.js"
  ],
  theme: {
    extend: {
      fontFamily:{
        'rubik': ['Rubik', 'sans-serif'],
        'roboto': ['Roboto', 'sans-serif'],
      },
    },
    screens: {
      'xs': '353px',
      'sm': '385px',
      'md': '478px',
      'lg': '1024px',
      'xl': '1280px',
      '2xl':'1536px',
    }
  },
  plugins: [
    require('flowbite/plugin') // подключаем плагин Flowbite
  ],
}
