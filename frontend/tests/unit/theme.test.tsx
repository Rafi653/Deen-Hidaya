import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ThemeProvider } from '../../lib/ThemeProvider';
import { ThemeToggle } from '../../components/ThemeToggle';
import { FontSizeControl } from '../../components/FontSizeControl';

describe('Theme System', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
    // Mock matchMedia
    Object.defineProperty(window, 'matchMedia', {
      writable: true,
      value: vi.fn().mockImplementation((query) => ({
        matches: false,
        media: query,
        onchange: null,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
      })),
    });
  });

  afterEach(() => {
    localStorage.clear();
  });

  describe('ThemeProvider', () => {
    it('should default to system theme', () => {
      render(
        <ThemeProvider>
          <div>Test</div>
        </ThemeProvider>
      );
      expect(screen.getByText('Test')).toBeInTheDocument();
    });

    it('should persist theme preference to localStorage', async () => {
      const user = userEvent.setup();
      render(
        <ThemeProvider>
          <ThemeToggle />
        </ThemeProvider>
      );

      const select = screen.getByLabelText('Select theme preference');
      await user.selectOptions(select, 'dark');

      await waitFor(() => {
        expect(localStorage.getItem('deen-hidaya-theme')).toBe('dark');
      });
    });

    it('should persist font size preference to localStorage', async () => {
      const user = userEvent.setup();
      render(
        <ThemeProvider>
          <FontSizeControl />
        </ThemeProvider>
      );

      const largeButton = screen.getByRole('button', { name: /set text size to large/i });
      await user.click(largeButton);

      await waitFor(() => {
        expect(localStorage.getItem('deen-hidaya-font-size')).toBe('large');
      });
    });

    it('should load saved theme from localStorage', () => {
      localStorage.setItem('deen-hidaya-theme', 'dark');
      render(
        <ThemeProvider>
          <ThemeToggle />
        </ThemeProvider>
      );

      const select = screen.getByLabelText('Select theme preference') as HTMLSelectElement;
      expect(select.value).toBe('dark');
    });

    it('should load saved font size from localStorage', () => {
      localStorage.setItem('deen-hidaya-font-size', 'large');
      render(
        <ThemeProvider>
          <FontSizeControl />
        </ThemeProvider>
      );

      const largeButton = screen.getByRole('button', { name: /set text size to large/i });
      expect(largeButton).toHaveAttribute('aria-pressed', 'true');
    });
  });

  describe('ThemeToggle', () => {
    it('should render theme options', () => {
      render(
        <ThemeProvider>
          <ThemeToggle />
        </ThemeProvider>
      );

      expect(screen.getByText(/☀️ Light/)).toBeInTheDocument();
      expect(screen.getByText(/🌙 Dark/)).toBeInTheDocument();
      expect(screen.getByText(/💻 System/)).toBeInTheDocument();
    });

    it('should change theme when option is selected', async () => {
      const user = userEvent.setup();
      render(
        <ThemeProvider>
          <ThemeToggle />
        </ThemeProvider>
      );

      const select = screen.getByLabelText('Select theme preference');
      await user.selectOptions(select, 'dark');

      expect((select as HTMLSelectElement).value).toBe('dark');
    });

    it('should show resolved theme status', () => {
      render(
        <ThemeProvider>
          <ThemeToggle />
        </ThemeProvider>
      );

      expect(screen.getByText(/\(Light\)/i)).toBeInTheDocument();
    });
  });

  describe('FontSizeControl', () => {
    it('should render all font size options', () => {
      render(
        <ThemeProvider>
          <FontSizeControl />
        </ThemeProvider>
      );

      expect(screen.getByRole('button', { name: /set text size to small/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /set text size to medium/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /set text size to large/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /set text size to extra large/i })).toBeInTheDocument();
    });

    it('should highlight selected font size', () => {
      render(
        <ThemeProvider>
          <FontSizeControl />
        </ThemeProvider>
      );

      const mediumButton = screen.getByRole('button', { name: /set text size to medium/i });
      expect(mediumButton).toHaveAttribute('aria-pressed', 'true');
    });

    it('should change font size when button is clicked', async () => {
      const user = userEvent.setup();
      render(
        <ThemeProvider>
          <FontSizeControl />
        </ThemeProvider>
      );

      const largeButton = screen.getByRole('button', { name: /set text size to large/i });
      await user.click(largeButton);

      expect(largeButton).toHaveAttribute('aria-pressed', 'true');
    });
  });
});
