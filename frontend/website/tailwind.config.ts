import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Primary Palette
        'pure-black': '#000000',
        'royal-blue': '#1E3A8A',
        'brilliant-blue': '#3B82F6',
        'light-blue': '#60A5FA',
        'ice-white': '#E6F3FF',

        // Functional Colors
        'success': '#10B981',
        'warning': '#F59E0B',
        'error': '#EF4444',
        'info': '#3B82F6',

        // Glass Surfaces
        'glass-level1': 'rgba(255, 255, 255, 0.03)',
        'glass-level2': 'rgba(255, 255, 255, 0.05)',
        'glass-elevated': 'rgba(30, 58, 138, 0.15)',
        'glass-border': 'rgba(59, 130, 246, 0.2)',
      },
      fontFamily: {
        sans: [
          '-apple-system',
          'BlinkMacSystemFont',
          'Segoe UI',
          'SF Pro Display',
          'Roboto',
          'sans-serif',
        ],
      },
      backdropBlur: {
        xs: '2px',
        sm: '4px',
        md: '8px',
        lg: '16px',
        xl: '24px',
        '2xl': '32px',
        '3xl': '40px',
      },
      animation: {
        'gradient-shift': 'gradientShift 25s ease-in-out infinite',
        'royal-flow': 'royalFlow 20s ease-in-out infinite',
        'fade-slide': 'fadeSlide 0.4s ease-out',
      },
      keyframes: {
        gradientShift: {
          '0%': { backgroundPosition: '0% 50%' },
          '25%': { backgroundPosition: '100% 50%' },
          '50%': { backgroundPosition: '100% 100%' },
          '75%': { backgroundPosition: '0% 100%' },
          '100%': { backgroundPosition: '0% 50%' },
        },
        royalFlow: {
          '0%, 100%': { transform: 'translateY(0px) scale(1)' },
          '50%': { transform: 'translateY(-15px) scale(1.02)' },
        },
        fadeSlide: {
          from: {
            opacity: '0',
            transform: 'translateY(20px)',
          },
          to: {
            opacity: '1',
            transform: 'translateY(0)',
          },
        },
      },
    },
  },
  plugins: [],
};

export default config;
