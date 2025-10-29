import { useTheme, FontSize } from '../lib/theme';

export function FontSizeControl() {
  const { fontSize, setFontSize } = useTheme();

  const fontSizeOptions: { value: FontSize; label: string; icon: string }[] = [
    { value: 'small', label: 'Small', icon: 'A' },
    { value: 'medium', label: 'Medium', icon: 'A' },
    { value: 'large', label: 'Large', icon: 'A' },
    { value: 'extra-large', label: 'Extra Large', icon: 'A' },
  ];

  return (
    <div className="flex items-center gap-2">
      <label htmlFor="font-size-select" className="text-sm font-medium text-gray-700 dark:text-gray-300">
        Text Size:
      </label>
      <div className="flex gap-1 bg-gray-100 dark:bg-gray-700 rounded-lg p-1">
        {fontSizeOptions.map((option, index) => (
          <button
            key={option.value}
            onClick={() => setFontSize(option.value)}
            className={`px-3 py-1 rounded-md transition-colors font-medium ${
              fontSize === option.value
                ? 'bg-green-500 text-white'
                : 'text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
            }`}
            aria-label={`Set text size to ${option.label}`}
            aria-pressed={fontSize === option.value}
            title={option.label}
            style={{ 
              fontSize: index === 0 ? '0.75rem' : index === 1 ? '0.875rem' : index === 2 ? '1rem' : '1.125rem'
            }}
          >
            {option.icon}
          </button>
        ))}
      </div>
    </div>
  );
}
