import type { Config } from 'tailwindcss';

const config: Config = {
  darkMode: 'class',
  content: [
    './app/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './lib/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      // Colors are driven by CSS variables (see app/globals.css) so a single
      // set of classes works in both light and dark themes.
      colors: {
        cream: {
          DEFAULT: 'rgb(var(--c-cream) / <alpha-value>)',
          surface: 'rgb(var(--c-surface) / <alpha-value>)',
          warm: 'rgb(var(--c-warm) / <alpha-value>)',
          border: 'rgb(var(--c-border) / <alpha-value>)',
          borderDark: 'rgb(var(--c-border-dark) / <alpha-value>)',
        },
        charcoal: {
          DEFAULT: 'rgb(var(--c-charcoal) / <alpha-value>)',
          muted: 'rgb(var(--c-muted) / <alpha-value>)',
          subtle: 'rgb(var(--c-subtle) / <alpha-value>)',
        },
        terracotta: {
          DEFAULT: 'rgb(var(--c-terra) / <alpha-value>)',
          hover: 'rgb(var(--c-terra-hover) / <alpha-value>)',
          light: 'rgb(var(--c-terra-light) / <alpha-value>)',
        },
        sage: {
          DEFAULT: 'rgb(var(--c-sage) / <alpha-value>)',
          light: 'rgb(var(--c-sage-light) / <alpha-value>)',
        },
        amber: {
          DEFAULT: 'rgb(var(--c-amber) / <alpha-value>)',
          light: 'rgb(var(--c-amber-light) / <alpha-value>)',
        },
      },
      fontFamily: {
        sans: ['var(--font-inter)', 'sans-serif'],
        mono: ['var(--font-mono)', 'monospace'],
        serif: ['var(--font-serif)', 'serif'],
      },
    },
  },
  plugins: [],
};

export default config;
