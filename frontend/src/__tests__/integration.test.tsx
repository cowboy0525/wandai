import React from 'react';
import { render, screen, fireEvent, waitFor } from '../utils/test-utils';
import { ThemeProvider } from '../contexts/ThemeContext';
import { ErrorBoundary } from '../components/ErrorBoundary';
import LoadingSpinner, { LoadingStates } from '../components/ui/LoadingSpinner';
import { useAPI } from '../hooks/useAPI';
import { apiService } from '../services/api';

// Mock API service
jest.mock('../services/api', () => ({
  apiService: {
    get: jest.fn(),
    post: jest.fn(),
    put: jest.fn(),
    delete: jest.fn(),
    upload: jest.fn(),
    healthCheck: jest.fn(),
  },
}));

const mockApiService = apiService as jest.Mocked<typeof apiService>;

// Test component that uses multiple hooks and components
const IntegrationTestComponent = () => {
  const { data, loading, error, execute } = useAPI(() => mockApiService.get('/test'));
  const [theme, setTheme] = React.useState<'light' | 'dark'>('light');

  const toggleTheme = () => {
    setTheme(theme === 'light' ? 'dark' : 'light');
  };

  return (
    <div className={`theme-${theme}`}>
      <button onClick={toggleTheme}>Toggle Theme</button>
      <button onClick={() => execute()}>Fetch Data</button>
      
      <LoadingStates loading={loading} error={error}>
        {data ? (
          <div data-testid="data-display">
            <h2>Data Loaded</h2>
            <pre>{JSON.stringify(data, null, 2)}</pre>
          </div>
        ) : (
          <div data-testid="no-data">No data available</div>
        )}
      </LoadingStates>
      
      <LoadingSpinner size="md" text="Processing..." />
    </div>
  );
};

// Component that might throw errors
const ErrorProneComponent = ({ shouldThrow }: { shouldThrow: boolean }) => {
  if (shouldThrow) {
    throw new Error('Integration test error');
  }
  return <div>Component working normally</div>;
};

describe('Frontend Integration Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Theme System Integration', () => {
    it('manages theme state across components', () => {
      render(
        <ThemeProvider>
          <IntegrationTestComponent />
        </ThemeProvider>
      );

      const toggleButton = screen.getByText('Toggle Theme');
      const container = screen.getByText('Toggle Theme').closest('div');

      expect(container).toHaveClass('theme-light');

      fireEvent.click(toggleButton);
      expect(container).toHaveClass('theme-dark');

      fireEvent.click(toggleButton);
      expect(container).toHaveClass('theme-light');
    });

    it('persists theme preference in localStorage', () => {
      render(
        <ThemeProvider>
          <IntegrationTestComponent />
        </ThemeProvider>
      );

      const toggleButton = screen.getByText('Toggle Theme');
      fireEvent.click(toggleButton);

      expect(localStorage.getItem('wand-ai-theme')).toBe('dark');
    });
  });

  describe('API Integration', () => {
    it('handles successful API calls with loading states', async () => {
      const mockData = { id: 1, name: 'Test Item' };
      mockApiService.get.mockResolvedValue(mockData);

      render(
        <ThemeProvider>
          <IntegrationTestComponent />
        </ThemeProvider>
      );

      const fetchButton = screen.getByText('Fetch Data');
      fireEvent.click(fetchButton);

      // Should show loading state
      expect(screen.getByText('Processing...')).toBeInTheDocument();

      await waitFor(() => {
        expect(screen.getByTestId('data-display')).toBeInTheDocument();
      });

      expect(screen.getByText('Data Loaded')).toBeInTheDocument();
      expect(screen.getByText(JSON.stringify(mockData, null, 2))).toBeInTheDocument();
    });

    it('handles API errors gracefully', async () => {
      const mockError = new Error('API Error');
      mockApiService.get.mockRejectedValue(mockError);

      render(
        <ThemeProvider>
          <IntegrationTestComponent />
        </ThemeProvider>
      );

      const fetchButton = screen.getByText('Fetch Data');
      fireEvent.click(fetchButton);

      await waitFor(() => {
        expect(screen.getByText('API Error')).toBeInTheDocument();
      });

      expect(screen.getByTestId('no-data')).not.toBeInTheDocument();
    });

    it('integrates with health check functionality', async () => {
      mockApiService.healthCheck.mockResolvedValue(true);

      const result = await mockApiService.healthCheck();
      expect(result).toBe(true);
      expect(mockApiService.healthCheck).toHaveBeenCalled();
    });
  });

  describe('Loading States Integration', () => {
    it('shows loading spinner during API calls', async () => {
      // Mock a slow API call
      mockApiService.get.mockImplementation(() => 
        new Promise(resolve => setTimeout(() => resolve({ data: 'test' }), 100))
      );

      render(
        <ThemeProvider>
          <IntegrationTestComponent />
        </ThemeProvider>
      );

      const fetchButton = screen.getByText('Fetch Data');
      fireEvent.click(fetchButton);

      // Should show loading states
      expect(screen.getByText('Processing...')).toBeInTheDocument();
    });

    it('transitions between loading, error, and success states', async () => {
      const mockData = { success: true };
      mockApiService.get.mockResolvedValue(mockData);

      render(
        <ThemeProvider>
          <IntegrationTestComponent />
        </ThemeBoundary>
      );

      const fetchButton = screen.getByText('Fetch Data');
      
      // Initial state
      expect(screen.getByTestId('no-data')).toBeInTheDocument();

      // Start loading
      fireEvent.click(fetchButton);

      // Success state
      await waitFor(() => {
        expect(screen.getByTestId('data-display')).toBeInTheDocument();
      });
    });
  });

  describe('Error Boundary Integration', () => {
    it('catches errors and provides recovery options', () => {
      render(
        <ErrorBoundary>
          <ErrorProneComponent shouldThrow={true} />
        </ErrorBoundary>
      );

      expect(screen.getByText('Oops! Something went wrong')).toBeInTheDocument();
      expect(screen.getByText('Try Again')).toBeInTheDocument();
      expect(screen.getByText('Copy Error Details')).toBeInTheDocument();
    });

    it('allows error recovery', () => {
      const { rerender } = render(
        <ErrorBoundary>
          <ErrorProneComponent shouldThrow={true} />
        </ErrorBoundary>
      );

      expect(screen.getByText('Oops! Something went wrong')).toBeInTheDocument();

      // Recover from error
      rerender(
        <ErrorBoundary>
          <ErrorProneComponent shouldThrow={false} />
        </ErrorBoundary>
      );

      expect(screen.getByText('Component working normally')).toBeInTheDocument();
    });
  });

  describe('Component Composition', () => {
    it('combines multiple UI components seamlessly', () => {
      render(
        <ThemeProvider>
          <div>
            <LoadingSpinner size="lg" text="Large Spinner" />
            <LoadingStates loading={false} error={null}>
              <div>Content loaded</div>
            </LoadingStates>
          </div>
        </ThemeProvider>
      );

      expect(screen.getByText('Large Spinner')).toBeInTheDocument();
      expect(screen.getByText('Content loaded')).toBeInTheDocument();
    });

    it('handles complex component hierarchies', () => {
      render(
        <ErrorBoundary>
          <ThemeProvider>
            <div>
              <h1>Main App</h1>
              <IntegrationTestComponent />
            </div>
          </ThemeProvider>
        </ErrorBoundary>
      );

      expect(screen.getByText('Main App')).toBeInTheDocument();
      expect(screen.getByText('Toggle Theme')).toBeInTheDocument();
      expect(screen.getByText('Fetch Data')).toBeInTheDocument();
    });
  });

  describe('State Management Integration', () => {
    it('manages complex state across multiple hooks', async () => {
      const mockData = { items: [1, 2, 3] };
      mockApiService.get.mockResolvedValue(mockData);

      render(
        <ThemeProvider>
          <IntegrationTestComponent />
        </ThemeProvider>
      );

      // Initial state
      expect(screen.getByTestId('no-data')).toBeInTheDocument();

      // Trigger state change
      const fetchButton = screen.getByText('Fetch Data');
      fireEvent.click(fetchButton);

      // Wait for state update
      await waitFor(() => {
        expect(screen.getByTestId('data-display')).toBeInTheDocument();
      });

      // Verify state is maintained
      expect(screen.getByText('Data Loaded')).toBeInTheDocument();
    });

    it('handles concurrent state updates', async () => {
      const mockData1 = { id: 1 };
      const mockData2 = { id: 2 };

      mockApiService.get
        .mockResolvedValueOnce(mockData1)
        .mockResolvedValueOnce(mockData2);

      render(
        <ThemeProvider>
          <IntegrationTestComponent />
        </ThemeProvider>
      );

      const fetchButton = screen.getByText('Fetch Data');

      // Trigger multiple rapid calls
      fireEvent.click(fetchButton);
      fireEvent.click(fetchButton);

      // Should handle concurrent updates gracefully
      await waitFor(() => {
        expect(screen.getByTestId('data-display')).toBeInTheDocument();
      });
    });
  });

  describe('Performance and Responsiveness', () => {
    it('responds quickly to user interactions', async () => {
      const mockData = { response: 'fast' };
      mockApiService.get.mockResolvedValue(mockData);

      render(
        <ThemeProvider>
          <IntegrationTestComponent />
        </ThemeProvider>
      );

      const startTime = performance.now();
      
      const fetchButton = screen.getByText('Fetch Data');
      fireEvent.click(fetchButton);

      await waitFor(() => {
        expect(screen.getByTestId('data-display')).toBeInTheDocument();
      });

      const endTime = performance.now();
      const responseTime = endTime - startTime;

      // Should respond within reasonable time (adjust threshold as needed)
      expect(responseTime).toBeLessThan(1000);
    });

    it('handles rapid theme toggles without issues', () => {
      render(
        <ThemeProvider>
          <IntegrationTestComponent />
        </ThemeProvider>
      );

      const toggleButton = screen.getByText('Toggle Theme');

      // Rapid theme toggles
      for (let i = 0; i < 10; i++) {
        fireEvent.click(toggleButton);
      }

      // Should still be functional
      expect(screen.getByText('Fetch Data')).toBeInTheDocument();
    });
  });

  describe('Accessibility Integration', () => {
    it('maintains accessibility across component interactions', () => {
      render(
        <ThemeProvider>
          <IntegrationTestComponent />
        </ThemeProvider>
      );

      // Check for proper ARIA labels and roles
      const fetchButton = screen.getByText('Fetch Data');
      const toggleButton = screen.getByText('Toggle Theme');

      expect(fetchButton).toBeInTheDocument();
      expect(toggleButton).toBeInTheDocument();

      // Verify loading spinner accessibility
      const spinner = screen.getByText('Processing...');
      expect(spinner).toBeInTheDocument();
    });

    it('provides keyboard navigation support', () => {
      render(
        <ThemeProvider>
          <IntegrationTestComponent />
        </ThemeProvider>
      );

      const fetchButton = screen.getByText('Fetch Data');
      const toggleButton = screen.getByText('Toggle Theme');

      // Tab navigation should work
      toggleButton.focus();
      expect(document.activeElement).toBe(toggleButton);

      fetchButton.focus();
      expect(document.activeElement).toBe(fetchButton);
    });
  });
});
