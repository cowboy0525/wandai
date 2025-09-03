import React from 'react';
import { render, screen, fireEvent, act } from '../../utils/test-utils';
import { ThemeProvider, useTheme, ThemeToggle, ThemeSelector } from '../ThemeContext';

// Test component to use the theme context
const TestComponent = () => {
  const { theme, isDark, setTheme, toggleTheme } = useTheme();
  return (
    <div>
      <span data-testid="current-theme">{theme}</span>
      <span data-testid="is-dark">{isDark.toString()}</span>
      <button onClick={() => setTheme('light')}>Set Light</button>
      <button onClick={() => setTheme('dark')}>Set Dark</button>
      <button onClick={() => setTheme('system')}>Set System</button>
      <button onClick={toggleTheme}>Toggle</button>
    </div>
  );
};

describe('ThemeContext', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
    // Reset document classes
    document.documentElement.classList.remove('light', 'dark');
  });

  describe('ThemeProvider', () => {
    it('renders children with theme context', () => {
      render(
        <ThemeProvider>
          <TestComponent />
        </ThemeProvider>
      );
      expect(screen.getByTestId('current-theme')).toBeInTheDocument();
    });

    it('defaults to system theme', () => {
      render(
        <ThemeProvider>
          <TestComponent />
        </ThemeProvider>
      );
      expect(screen.getByTestId('current-theme')).toHaveTextContent('system');
    });

    it('uses stored theme from localStorage', () => {
      localStorage.setItem('wand-ai-theme', 'dark');
      render(
        <ThemeProvider>
          <TestComponent />
        </ThemeProvider>
      );
      expect(screen.getByTestId('current-theme')).toHaveTextContent('dark');
    });

    it('applies theme classes to document', () => {
      render(
        <ThemeProvider>
          <TestComponent />
        </ThemeProvider>
      );
      
      // Initially should have light class (system defaults to light in tests)
      expect(document.documentElement).toHaveClass('light');
      
      // Change to dark theme
      fireEvent.click(screen.getByText('Set Dark'));
      expect(document.documentElement).toHaveClass('dark');
      expect(document.documentElement).not.toHaveClass('light');
    });

    it('persists theme changes to localStorage', () => {
      render(
        <ThemeProvider>
          <TestComponent />
        </ThemeProvider>
      );
      
      fireEvent.click(screen.getByText('Set Dark'));
      expect(localStorage.getItem('wand-ai-theme')).toBe('dark');
      
      fireEvent.click(screen.getByText('Set Light'));
      expect(localStorage.getItem('wand-ai-theme')).toBe('light');
    });
  });

  describe('useTheme hook', () => {
    it('provides theme state and functions', () => {
      render(
        <ThemeProvider>
          <TestComponent />
        </ThemeProvider>
      );
      
      expect(screen.getByTestId('current-theme')).toBeInTheDocument();
      expect(screen.getByTestId('is-dark')).toBeInTheDocument();
      expect(screen.getByText('Set Light')).toBeInTheDocument();
      expect(screen.getByText('Set Dark')).toBeInTheDocument();
    });

    it('changes theme when setTheme is called', () => {
      render(
        <ThemeProvider>
          <TestComponent />
        </ThemeProvider>
      );
      
      fireEvent.click(screen.getByText('Set Dark'));
      expect(screen.getByTestId('current-theme')).toHaveTextContent('dark');
      
      fireEvent.click(screen.getByText('Set Light'));
      expect(screen.getByTestId('current-theme')).toHaveTextContent('light');
    });

    it('toggles theme when toggleTheme is called', () => {
      render(
        <ThemeProvider>
          <TestComponent />
        </ThemeProvider>
      );
      
      // Start with system theme (defaults to light in tests)
      expect(screen.getByTestId('is-dark')).toHaveTextContent('false');
      
      fireEvent.click(screen.getByText('Toggle'));
      expect(screen.getByTestId('is-dark')).toHaveTextContent('true');
      
      fireEvent.click(screen.getByText('Toggle'));
      expect(screen.getByTestId('is-dark')).toHaveTextContent('false');
    });

    it('throws error when used outside provider', () => {
      // Suppress console.error for this test
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
      
      expect(() => {
        render(<TestComponent />);
      }).toThrow('useTheme must be used within a ThemeProvider');
      
      consoleSpy.mockRestore();
    });
  });

  describe('ThemeToggle', () => {
    it('renders toggle button', () => {
      render(
        <ThemeProvider>
          <ThemeToggle />
        </ThemeProvider>
      );
      
      const toggleButton = screen.getByRole('button');
      expect(toggleButton).toBeInTheDocument();
      expect(toggleButton).toHaveAttribute('aria-label');
    });

    it('toggles theme when clicked', () => {
      render(
        <ThemeProvider>
          <ThemeToggle />
        </ThemeProvider>
      );
      
      const toggleButton = screen.getByRole('button');
      fireEvent.click(toggleButton);
      
      // Should now be in dark mode
      expect(document.documentElement).toHaveClass('dark');
    });

    it('shows correct icon based on current theme', () => {
      const { rerender } = render(
        <ThemeProvider>
          <ThemeToggle />
        </ThemeProvider>
      );
      
      // Initially light mode, should show moon icon
      expect(screen.getByRole('button')).toBeInTheDocument();
      
      // Switch to dark mode
      fireEvent.click(screen.getByRole('button'));
      rerender(
        <ThemeProvider>
          <ThemeToggle />
        </ThemeProvider>
      );
      
      // Should now show sun icon
      expect(screen.getByRole('button')).toBeInTheDocument();
    });

    it('applies correct size classes', () => {
      render(
        <ThemeProvider>
          <ThemeToggle size="lg" />
        </ThemeProvider>
      );
      
      const toggleButton = screen.getByRole('button');
      expect(toggleButton).toHaveClass('w-12', 'h-12');
    });
  });

  describe('ThemeSelector', () => {
    it('renders theme selector dropdown', () => {
      render(
        <ThemeProvider>
          <ThemeSelector />
        </ThemeProvider>
      );
      
      expect(screen.getByLabelText('Theme:')).toBeInTheDocument();
      expect(screen.getByRole('combobox')).toBeInTheDocument();
    });

    it('shows all theme options', () => {
      render(
        <ThemeProvider>
          <ThemeSelector />
        </ThemeProvider>
      );
      
      const select = screen.getByRole('combobox');
      expect(select).toHaveValue('system');
      
      const options = screen.getAllByRole('option');
      expect(options).toHaveLength(3);
      expect(options[0]).toHaveValue('light');
      expect(options[1]).toHaveValue('dark');
      expect(options[2]).toHaveValue('system');
    });

    it('changes theme when option is selected', () => {
      render(
        <ThemeProvider>
          <ThemeSelector />
        </ThemeProvider>
      );
      
      const select = screen.getByRole('combobox');
      fireEvent.change(select, { target: { value: 'dark' } });
      
      expect(select).toHaveValue('dark');
      expect(document.documentElement).toHaveClass('dark');
    });

    it('hides system option when showSystem is false', () => {
      render(
        <ThemeProvider>
          <ThemeSelector showSystem={false} />
        </ThemeProvider>
      );
      
      const options = screen.getAllByRole('option');
      expect(options).toHaveLength(2);
      expect(options[0]).toHaveValue('light');
      expect(options[1]).toHaveValue('dark');
    });
  });

  describe('System theme detection', () => {
    it('responds to system theme changes', () => {
      // Mock system theme as dark
      Object.defineProperty(window, 'matchMedia', {
        writable: true,
        value: jest.fn().mockImplementation(query => ({
          matches: query === '(prefers-color-scheme: dark)',
          media: query,
          onchange: null,
          addEventListener: jest.fn(),
          removeEventListener: jest.fn(),
          dispatchEvent: jest.fn(),
        })),
      });

      render(
        <ThemeProvider>
          <TestComponent />
        </ThemeProvider>
      );
      
      // Should be in dark mode when system prefers dark
      expect(screen.getByTestId('is-dark')).toHaveTextContent('true');
    });
  });
});
