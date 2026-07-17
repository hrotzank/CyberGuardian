/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // CyberGuardian Design System
        'cg-bg': '#0A0F1C',
        'cg-panel': '#131B2E',
        'cg-panel-light': '#1A2540',
        'cg-blue': '#00AEEF',
        'cg-blue-dark': '#0086B8',
        'cg-blue-glow': 'rgba(0,174,239,0.15)',
        'cg-green': '#00D26A',
        'cg-yellow': '#FFC857',
        'cg-red': '#FF4D4D',
        'cg-text': '#F5F7FA',
        'cg-text-muted': '#8892A4',
        'cg-border': 'rgba(0,174,239,0.2)',
        'cg-border-subtle': 'rgba(255,255,255,0.06)',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      backgroundImage: {
        'grid-pattern': "url(\"data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%2300AEEF' fill-opacity='0.03'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E\")",
        'hero-gradient': 'linear-gradient(135deg, #0A0F1C 0%, #0D1525 50%, #0A0F1C 100%)',
        'card-gradient': 'linear-gradient(135deg, #131B2E 0%, #1A2540 100%)',
        'blue-glow': 'radial-gradient(ellipse at center, rgba(0,174,239,0.12) 0%, transparent 70%)',
      },
      boxShadow: {
        'cg': '0 4px 32px rgba(0,174,239,0.12)',
        'cg-lg': '0 8px 48px rgba(0,174,239,0.18)',
        'cg-inset': 'inset 0 1px 0 rgba(255,255,255,0.05)',
        'red-glow': '0 0 20px rgba(255,77,77,0.3)',
        'green-glow': '0 0 20px rgba(0,210,106,0.3)',
        'blue-glow': '0 0 20px rgba(0,174,239,0.3)',
        'yellow-glow': '0 0 20px rgba(255,200,87,0.3)',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'spin-slow': 'spin 8s linear infinite',
        'float': 'float 6s ease-in-out infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        glow: {
          '0%': { boxShadow: '0 0 5px rgba(0,174,239,0.3)' },
          '100%': { boxShadow: '0 0 25px rgba(0,174,239,0.7)' },
        },
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [],
}
