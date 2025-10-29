import { ThemeToggle } from './ThemeToggle';
import { FontSizeControl } from './FontSizeControl';

interface AccessibilityBarProps {
  className?: string;
}

export function AccessibilityBar({ className = '' }: AccessibilityBarProps) {
  return (
    <div 
      className={`bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 shadow-sm ${className}`}
      role="region"
      aria-label="Accessibility controls"
    >
      <div className="container mx-auto px-4 py-3">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <ThemeToggle />
          <FontSizeControl />
        </div>
      </div>
    </div>
  );
}
