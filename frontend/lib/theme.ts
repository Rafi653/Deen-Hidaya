import { createContext, useContext } from 'react';

export type Theme = 'light' | 'dark' | 'system';
export type FontSize = 'small' | 'medium' | 'large' | 'extra-large';

export interface ThemeContextType {
  theme: Theme;
  resolvedTheme: 'light' | 'dark';
  fontSize: FontSize;
  setTheme: (theme: Theme) => void;
  setFontSize: (size: FontSize) => void;
}

export const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export function useTheme(): ThemeContextType {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
}

// Font size mappings for different text types
export const fontSizeClasses = {
  small: {
    arabic: 'text-2xl',
    translation: 'text-sm',
    body: 'text-sm',
    heading: 'text-2xl',
  },
  medium: {
    arabic: 'text-3xl',
    translation: 'text-base',
    body: 'text-base',
    heading: 'text-3xl',
  },
  large: {
    arabic: 'text-4xl',
    translation: 'text-lg',
    body: 'text-lg',
    heading: 'text-4xl',
  },
  'extra-large': {
    arabic: 'text-5xl',
    translation: 'text-xl',
    body: 'text-xl',
    heading: 'text-5xl',
  },
};

// Helper to get current font size classes
export function getFontSizeClasses(fontSize: FontSize) {
  return fontSizeClasses[fontSize];
}
