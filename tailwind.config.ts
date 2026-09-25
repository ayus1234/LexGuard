import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        surface: {
          DEFAULT: '#f8f9ff',
          dim: '#cbdbf5',
          bright: '#f8f9ff',
          lowest: '#ffffff',
          low: '#eff4ff',
          container: '#e5eeff',
          high: '#dce9ff',
          highest: '#d3e4fe',
        },
        'on-surface': {
          DEFAULT: '#0b1c30',
          variant: '#45464d',
        },
        'inverse-surface': '#213145',
        'inverse-on-surface': '#eaf1ff',
        outline: {
          DEFAULT: '#76777d',
          variant: '#c6c6cd',
        },
        brand: {
          primary: '#0F172A',
          hover: '#1E293B',
          blue: '#0284C7',
          'blue-light': '#0EA5E9',
          'blue-dark': '#006398',
          'blue-surface': '#EFF6FF',
          amber: '#D97706',
          'amber-surface': '#FEF3C7',
          'amber-text': '#92400E',
          emerald: '#059669',
          'emerald-surface': '#ECFDF5',
          'emerald-text': '#065F46',
          red: '#BA1A1A',
          'red-surface': '#FEF2F2',
          'red-text': '#991B1B',
        },
      },
      fontFamily: {
        display: ['var(--font-jakarta)', 'Plus Jakarta Sans', 'sans-serif'],
        sans: ['var(--font-inter)', 'Inter', 'sans-serif'],
        mono: ['var(--font-mono)', 'JetBrains Mono', 'monospace'],
      },
      borderRadius: {
        sm: '0.125rem',
        DEFAULT: '0.25rem',
        md: '0.375rem',
        lg: '0.5rem',
        xl: '0.75rem',
        full: '9999px',
      },
      boxShadow: {
        subtle: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        popover: '0 4px 12px -2px rgba(15, 23, 42, 0.08), 0 2px 6px -1px rgba(15, 23, 42, 0.04)',
        modal: '0 20px 25px -5px rgba(15, 23, 42, 0.12), 0 8px 10px -6px rgba(15, 23, 42, 0.08)',
      },
    },
  },
  plugins: [],
};

export default config;
