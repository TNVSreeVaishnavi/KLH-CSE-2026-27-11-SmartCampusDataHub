/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Plus Jakarta Sans', 'system-ui', 'sans-serif'],
        display: ['Sora', 'system-ui', 'sans-serif'],
      },
      colors: {
        navy: {
          50: '#eef2f9',
          100: '#d6def0',
          200: '#aabce2',
          300: '#7d95cf',
          400: '#4f6cb8',
          500: '#34539c',
          600: '#27417a',
          700: '#1d3260',
          800: '#152544',
          900: '#0e1a31',
          950: '#080f1f',
        },
        royal: {
          50: '#eef5ff',
          100: '#d9e8ff',
          200: '#bcd6ff',
          300: '#8ebcff',
          400: '#5a96ff',
          500: '#3273fc',
          600: '#1d54f0',
          700: '#1640d6',
          800: '#1736ac',
          900: '#1a3389',
          950: '#142055',
        },
        canvas: '#eef2f8',
      },
      boxShadow: {
        container:
          '0 30px 80px -20px rgba(13, 26, 49, 0.35), 0 12px 32px -12px rgba(13, 26, 49, 0.2)',
        card: '0 8px 24px -10px rgba(20, 40, 85, 0.25)',
        glow: '0 0 0 4px rgba(50, 115, 252, 0.15)',
      },
      keyframes: {
        'fade-in-up': {
          '0%': { opacity: '0', transform: 'translateY(16px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'fade-in': {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        'scale-in': {
          '0%': { opacity: '0', transform: 'scale(0.96)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
        shake: {
          '0%, 100%': { transform: 'translateX(0)' },
          '20%, 60%': { transform: 'translateX(-6px)' },
          '40%, 80%': { transform: 'translateX(6px)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
      },
      animation: {
        'fade-in-up': 'fade-in-up 0.6s cubic-bezier(0.22, 1, 0.36, 1) both',
        'fade-in': 'fade-in 0.5s ease both',
        'scale-in': 'scale-in 0.4s cubic-bezier(0.22, 1, 0.36, 1) both',
        shake: 'shake 0.45s ease both',
        shimmer: 'shimmer 1.6s linear infinite',
      },
    },
  },
  plugins: [],
};
