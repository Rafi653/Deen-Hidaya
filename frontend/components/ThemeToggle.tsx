import { useTheme } from '../lib/theme';

export function ThemeToggle() {
  const { theme, resolvedTheme, setTheme } = useTheme();

  return (
    <div className="flex items-center gap-2">
      <label htmlFor="theme-select" className="text-sm font-medium text-gray-700 dark:text-gray-300">
        Theme:
      </label>
      <div className="relative inline-flex items-center">
        <select
          id="theme-select"
          value={theme}
          onChange={(e) => setTheme(e.target.value as 'light' | 'dark' | 'system')}
          className="appearance-none px-3 py-2 pr-8 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-green-500 text-sm cursor-pointer"
          aria-label="Select theme preference"
        >
          <option value="light">☀️ Light</option>
          <option value="dark">🌙 Dark</option>
          <option value="system">💻 System</option>
        </select>
        <div className="absolute right-2 pointer-events-none">
          <svg className="w-4 h-4 text-gray-500 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </div>
      <span className="text-xs text-gray-500 dark:text-gray-400" aria-live="polite">
        ({resolvedTheme === 'dark' ? 'Dark' : 'Light'})
      </span>
    </div>
  );
}
