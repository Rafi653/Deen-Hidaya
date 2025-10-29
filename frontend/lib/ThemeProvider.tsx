import React, { useEffect, useState, ReactNode } from 'react';
import { Theme, FontSize, ThemeContext, ThemeContextType } from './theme';

interface ThemeProviderProps {
  children: ReactNode;
}

const THEME_STORAGE_KEY = 'deen-hidaya-theme';
const FONT_SIZE_STORAGE_KEY = 'deen-hidaya-font-size';

export function ThemeProvider({ children }: ThemeProviderProps) {
  const [theme, setThemeState] = useState<Theme>('system');
  const [fontSize, setFontSizeState] = useState<FontSize>('medium');
  const [resolvedTheme, setResolvedTheme] = useState<'light' | 'dark'>('light');

  // Initialize theme from localStorage or system preference
  useEffect(() => {
    const savedTheme = localStorage.getItem(THEME_STORAGE_KEY) as Theme | null;
    const savedFontSize = localStorage.getItem(FONT_SIZE_STORAGE_KEY) as FontSize | null;

    if (savedTheme && ['light', 'dark', 'system'].includes(savedTheme)) {
      setThemeState(savedTheme);
    }

    if (savedFontSize && ['small', 'medium', 'large', 'extra-large'].includes(savedFontSize)) {
      setFontSizeState(savedFontSize);
    }
  }, []);

  // Resolve theme based on system preference if theme is 'system'
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    
    function resolveTheme(currentTheme: Theme) {
      if (currentTheme === 'system') {
        return mediaQuery.matches ? 'dark' : 'light';
      }
      return currentTheme as 'light' | 'dark';
    }

    function updateTheme() {
      const resolved = resolveTheme(theme);
      setResolvedTheme(resolved);
      
      // Update document class
      if (resolved === 'dark') {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
    }

    updateTheme();

    // Listen for system theme changes
    mediaQuery.addEventListener('change', updateTheme);
    return () => mediaQuery.removeEventListener('change', updateTheme);
  }, [theme]);

  const setTheme = (newTheme: Theme) => {
    setThemeState(newTheme);
    localStorage.setItem(THEME_STORAGE_KEY, newTheme);
  };

  const setFontSize = (newSize: FontSize) => {
    setFontSizeState(newSize);
    localStorage.setItem(FONT_SIZE_STORAGE_KEY, newSize);
  };

  const value: ThemeContextType = {
    theme,
    resolvedTheme,
    fontSize,
    setTheme,
    setFontSize,
  };

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}
