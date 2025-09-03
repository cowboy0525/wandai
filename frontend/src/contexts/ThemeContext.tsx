/**
 * Wand AI - Professional Theme Context
 * Senior-Level Implementation with Dark Mode Support and System Preferences
 */

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';

// Theme types
export type Theme = 'light' | 'dark' | 'system';

// Theme context interface
interface ThemeContextType {
  theme: Theme;
  isDark: boolean;
  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;
}

// Theme context
const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

// Theme provider props
interface ThemeProviderProps {
  children: ReactNode;
  defaultTheme?: Theme;
  storageKey?: string;
  enableSystem?: boolean;
}

// Theme provider component
export const ThemeProvider: React.FC<ThemeProviderProps> = ({
  children,
  defaultTheme = 'system',
  storageKey = 'wand-ai-theme',
  enableSystem = true,
}) => {
  const [theme, setThemeState] = useState<Theme>(() => {
    // Try to get theme from localStorage
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem(storageKey) as Theme;
      if (stored && ['light', 'dark', 'system'].includes(stored)) {
        return stored;
      }
    }
    return defaultTheme;
  });

  const [isDark, setIsDark] = useState<boolean>(false);

  // Function to get system theme
  const getSystemTheme = (): boolean => {
    if (typeof window !== 'undefined' && window.matchMedia) {
      return window.matchMedia('(prefers-color-scheme: dark)').matches;
    }
    return false;
  };

  // Function to apply theme
  const applyTheme = (newTheme: Theme): void => {
    const root = document.documentElement;
    const isDarkMode = newTheme === 'dark' || (newTheme === 'system' && getSystemTheme());

    // Remove existing theme classes
    root.classList.remove('light', 'dark');

    // Add new theme class
    root.classList.add(isDarkMode ? 'dark' : 'light');

    // Update state
    setIsDark(isDarkMode);

    // Store in localStorage
    if (typeof window !== 'undefined') {
      localStorage.setItem(storageKey, newTheme);
    }
  };

  // Function to set theme
  const setTheme = (newTheme: Theme): void => {
    setThemeState(newTheme);
    applyTheme(newTheme);
  };

  // Function to toggle theme
  const toggleTheme = (): void => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
  };

  // Effect to apply theme on mount and theme change
  useEffect(() => {
    applyTheme(theme);
  }, [theme]);

  // Effect to listen for system theme changes
  useEffect(() => {
    if (theme === 'system' && enableSystem) {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      
      const handleChange = (e: MediaQueryListEvent): void => {
        applyTheme('system');
      };

      mediaQuery.addEventListener('change', handleChange);
      
      return () => {
        mediaQuery.removeEventListener('change', handleChange);
      };
    }
  }, [theme, enableSystem]);

  // Effect to add theme class to body for global styling
  useEffect(() => {
    const body = document.body;
    body.classList.remove('light-theme', 'dark-theme');
    body.classList.add(`${isDark ? 'dark' : 'light'}-theme`);
  }, [isDark]);

  const value: ThemeContextType = {
    theme,
    isDark,
    setTheme,
    toggleTheme,
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
};

// Hook to use theme context
export const useTheme = (): ThemeContextType => {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

// Hook to get current theme mode
export const useThemeMode = (): 'light' | 'dark' => {
  const { isDark } = useTheme();
  return isDark ? 'dark' : 'light';
};

// Hook to check if theme is system
export const useIsSystemTheme = (): boolean => {
  const { theme } = useTheme();
  return theme === 'system';
};

// Theme toggle component
export const ThemeToggle: React.FC<{
  className?: string;
  showLabel?: boolean;
  size?: 'sm' | 'md' | 'lg';
}> = ({ className = '', showLabel = true, size = 'md' }) => {
  const { theme, toggleTheme, isDark } = useTheme();

  const sizeClasses = {
    sm: 'w-8 h-8',
    md: 'w-10 h-10',
    lg: 'w-12 h-12',
  };

  const iconSize = {
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
    lg: 'w-6 h-6',
  };

  return (
    <button
      onClick={toggleTheme}
      className={`${sizeClasses[size]} rounded-lg bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors duration-200 flex items-center justify-center ${className}`}
      aria-label={`Switch to ${isDark ? 'light' : 'dark'} mode`}
      title={`Current: ${theme === 'system' ? 'System' : theme} mode`}
    >
      {isDark ? (
        // Sun icon for dark mode
        <svg
          className={`${iconSize[size]} text-yellow-500`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"
          />
        </svg>
      ) : (
        // Moon icon for light mode
        <svg
          className={`${iconSize[size]} text-gray-700`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"
          />
        </svg>
      )}
      
      {showLabel && (
        <span className="ml-2 text-sm font-medium text-gray-700 dark:text-gray-300">
          {isDark ? 'Light' : 'Dark'}
        </span>
      )}
    </button>
  );
};

// Theme selector component
export const ThemeSelector: React.FC<{
  className?: string;
  showSystem?: boolean;
}> = ({ className = '', showSystem = true }) => {
  const { theme, setTheme } = useTheme();

  return (
    <div className={`flex items-center space-x-2 ${className}`}>
      <label htmlFor="theme-select" className="text-sm font-medium text-gray-700 dark:text-gray-300">
        Theme:
      </label>
      
      <select
        id="theme-select"
        value={theme}
        onChange={(e) => setTheme(e.target.value as Theme)}
        className="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
      >
        <option value="light">Light</option>
        <option value="dark">Dark</option>
        {showSystem && <option value="system">System</option>}
      </select>
    </div>
  );
};

// Higher-order component to wrap components with theme
export function withTheme<P extends object>(
  Component: React.ComponentType<P>
) {
  return function ThemedComponent(props: P) {
    return (
      <ThemeProvider>
        <Component {...props} />
      </ThemeProvider>
    );
  };
}

export default ThemeProvider;
