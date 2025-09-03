import React, { ReactElement } from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { ThemeProvider } from '../contexts/ThemeContext';

// Custom render function that includes providers
const AllTheProviders = ({ children }: { children: React.ReactNode }) => {
  return (
    <ThemeProvider>
      {children}
    </ThemeProvider>
  );
};

const customRender = (
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) => render(ui, { wrapper: AllTheProviders, ...options });

// Re-export everything
export * from '@testing-library/react';

// Override render method
export { customRender as render };

// Mock API responses
export const mockApiResponses = {
  health: { status: 'healthy', timestamp: '2024-01-01T00:00:00Z' },
  tasks: {
    task_id: 'task_123',
    status: 'completed',
    result: 'Task completed successfully',
    agents_used: ['planner', 'researcher'],
  },
  documents: [
    {
      id: 'doc_1',
      filename: 'test.pdf',
      upload_date: '2024-01-01T00:00:00Z',
      file_size: 1024,
    },
  ],
};

// Mock API error responses
export const mockApiErrors = {
  notFound: { status: 404, message: 'Resource not found' },
  serverError: { status: 500, message: 'Internal server error' },
  unauthorized: { status: 401, message: 'Unauthorized' },
};

// Test data factories
export const createMockTask = (overrides = {}) => ({
  id: 'task_123',
  description: 'Test task description',
  priority: 'medium',
  status: 'pending',
  created_at: '2024-01-01T00:00:00Z',
  ...overrides,
});

export const createMockDocument = (overrides = {}) => ({
  id: 'doc_123',
  filename: 'test.pdf',
  document_type: 'PDF',
  upload_date: '2024-01-01T00:00:00Z',
  file_size: 1024,
  description: 'Test document',
  ...overrides,
});

// Mock functions
export const mockFunctions = {
  onSuccess: jest.fn(),
  onError: jest.fn(),
  onProgress: jest.fn(),
  onReset: jest.fn(),
  onRefetch: jest.fn(),
};
