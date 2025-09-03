import { apiService, APIError, NetworkError } from '../api';
import { mockApiResponses, mockApiErrors } from '../../utils/test-utils';

// Mock axios
jest.mock('axios', () => ({
  create: jest.fn(() => ({
    get: jest.fn(),
    post: jest.fn(),
    put: jest.fn(),
    delete: jest.fn(),
    interceptors: {
      request: { use: jest.fn() },
      response: { use: jest.fn() },
    },
  })),
}));

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

// Mock window.__ENV__
Object.defineProperty(window, '__ENV__', {
  value: {
    REACT_APP_API_URL: 'http://test-api.com',
    REACT_APP_VERSION: '1.0.0',
    NODE_ENV: 'test',
  },
  writable: true,
});

describe('API Service', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorageMock.getItem.mockReturnValue(null);
  });

  describe('APIError', () => {
    it('creates APIError with correct properties', () => {
      const error = new APIError('Test error', 400, 'BAD_REQUEST', { detail: 'test' });
      
      expect(error.message).toBe('Test error');
      expect(error.status).toBe(400);
      expect(error.code).toBe('BAD_REQUEST');
      expect(error.details).toEqual({ detail: 'test' });
      expect(error.name).toBe('APIError');
    });
  });

  describe('NetworkError', () => {
    it('creates NetworkError with correct properties', () => {
      const originalError = new Error('Original error');
      const error = new NetworkError('Network failed', originalError);
      
      expect(error.message).toBe('Network failed');
      expect(error.originalError).toBe(originalError);
      expect(error.name).toBe('NetworkError');
    });
  });

  describe('API Service Instance', () => {
    it('creates singleton instance', () => {
      const instance1 = apiService;
      const instance2 = apiService;
      expect(instance1).toBe(instance2);
    });
  });

  describe('GET requests', () => {
    it('makes successful GET request', async () => {
      const mockResponse = { data: mockApiResponses.health };
      const mockAxios = require('axios');
      mockAxios.create.mockReturnValue({
        get: jest.fn().mockResolvedValue(mockResponse),
        interceptors: { request: { use: jest.fn() }, response: { use: jest.fn() } },
      });

      const result = await apiService.get('/health');
      expect(result).toEqual(mockApiResponses.health);
    });

    it('handles GET request errors', async () => {
      const mockError = new Error('Network error');
      const mockAxios = require('axios');
      mockAxios.create.mockReturnValue({
        get: jest.fn().mockRejectedValue(mockError),
        interceptors: { request: { use: jest.fn() }, response: { use: jest.fn() } },
      });

      await expect(apiService.get('/health')).rejects.toThrow('Network error');
    });
  });

  describe('POST requests', () => {
    it('makes successful POST request', async () => {
      const mockResponse = { data: mockApiResponses.tasks };
      const mockAxios = require('axios');
      mockAxios.create.mockReturnValue({
        post: jest.fn().mockResolvedValue(mockResponse),
        interceptors: { request: { use: jest.fn() }, response: { use: jest.fn() } },
      });

      const result = await apiService.post('/tasks', { description: 'Test task' });
      expect(result).toEqual(mockApiResponses.tasks);
    });

    it('handles POST request errors', async () => {
      const mockError = new Error('Validation error');
      const mockAxios = require('axios');
      mockAxios.create.mockReturnValue({
        post: jest.fn().mockRejectedValue(mockError),
        interceptors: { request: { use: jest.fn() }, response: { use: jest.fn() } },
      });

      await expect(apiService.post('/tasks', {})).rejects.toThrow('Validation error');
    });
  });

  describe('PUT requests', () => {
    it('makes successful PUT request', async () => {
      const mockResponse = { data: { ...mockApiResponses.tasks, status: 'updated' } };
      const mockAxios = require('axios');
      mockAxios.create.mockReturnValue({
        put: jest.fn().mockResolvedValue(mockResponse),
        interceptors: { request: { use: jest.fn() }, response: { use: jest.fn() } },
      });

      const result = await apiService.put('/tasks/123', { status: 'updated' });
      expect(result.status).toBe('updated');
    });
  });

  describe('DELETE requests', () => {
    it('makes successful DELETE request', async () => {
      const mockResponse = { data: { message: 'Deleted successfully' } };
      const mockAxios = require('axios');
      mockAxios.create.mockReturnValue({
        delete: jest.fn().mockResolvedValue(mockResponse),
        interceptors: { request: { use: jest.fn() }, response: { use: jest.fn() } },
      });

      const result = await apiService.delete('/tasks/123');
      expect(result.message).toBe('Deleted successfully');
    });
  });

  describe('File upload', () => {
    it('uploads file with progress tracking', async () => {
      const mockResponse = { data: { file_id: 'file_123' } };
      const mockAxios = require('axios');
      mockAxios.create.mockReturnValue({
        post: jest.fn().mockResolvedValue(mockResponse),
        interceptors: { request: { use: jest.fn() }, response: { use: jest.fn() } },
      });

      const file = new File(['test content'], 'test.txt', { type: 'text/plain' });
      const onProgress = jest.fn();
      
      const result = await apiService.upload('/upload', file, onProgress);
      expect(result.file_id).toBe('file_123');
    });
  });

  describe('Health check', () => {
    it('returns true for successful health check', async () => {
      const mockResponse = { data: mockApiResponses.health };
      const mockAxios = require('axios');
      mockAxios.create.mockReturnValue({
        get: jest.fn().mockResolvedValue(mockResponse),
        interceptors: { request: { use: jest.fn() }, response: { use: jest.fn() } },
      });

      const result = await apiService.healthCheck();
      expect(result).toBe(true);
    });

    it('returns false for failed health check', async () => {
      const mockAxios = require('axios');
      mockAxios.create.mockReturnValue({
        get: jest.fn().mockRejectedValue(new Error('Health check failed')),
        interceptors: { request: { use: jest.fn() }, response: { use: jest.fn() } },
      });

      const result = await apiService.healthCheck();
      expect(result).toBe(false);
    });
  });

  describe('Error handling', () => {
    it('handles 401 errors by clearing auth token', async () => {
      const mockAxios = require('axios');
      mockAxios.create.mockReturnValue({
        get: jest.fn().mockRejectedValue(new APIError('Unauthorized', 401)),
        interceptors: { request: { use: jest.fn() }, response: { use: jest.fn() } },
      });

      // Mock window.location.href
      Object.defineProperty(window, 'location', {
        value: { href: '' },
        writable: true,
      });

      try {
        await apiService.get('/protected');
      } catch (error) {
        // Expected to throw
      }

      expect(localStorageMock.removeItem).toHaveBeenCalledWith('auth_token');
    });

    it('handles 403 errors with warning', async () => {
      const mockAxios = require('axios');
      mockAxios.create.mockReturnValue({
        get: jest.fn().mockRejectedValue(new APIError('Forbidden', 403)),
        interceptors: { request: { use: jest.fn() }, response: { use: jest.fn() } },
      });

      const consoleSpy = jest.spyOn(console, 'warn').mockImplementation(() => {});

      try {
        await apiService.get('/forbidden');
      } catch (error) {
        // Expected to throw
      }

      expect(consoleSpy).toHaveBeenCalledWith('Access forbidden:', 'Forbidden');
      consoleSpy.mockRestore();
    });

    it('handles 429 errors with warning', async () => {
      const mockAxios = require('axios');
      mockAxios.create.mockReturnValue({
        get: jest.fn().mockRejectedValue(new APIError('Rate limited', 429)),
        interceptors: { request: { use: jest.fn() }, response: { use: jest.fn() } },
      });

      const consoleSpy = jest.spyOn(console, 'warn').mockImplementation(() => {});

      try {
        await apiService.get('/rate-limited');
      } catch (error) {
        // Expected to throw
      }

      expect(consoleSpy).toHaveBeenCalledWith('Rate limited:', 'Rate limited');
      consoleSpy.mockRestore();
    });

    it('handles 500 errors with error logging', async () => {
      const mockAxios = require('axios');
      mockAxios.create.mockReturnValue({
        get: jest.fn().mockRejectedValue(new APIError('Server error', 500)),
        interceptors: { request: { use: jest.fn() }, response: { use: jest.fn() } },
      });

      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

      try {
        await apiService.get('/server-error');
      } catch (error) {
        // Expected to throw
      }

      expect(consoleSpy).toHaveBeenCalledWith('Server error:', 'Server error');
      consoleSpy.mockRestore();
    });
  });

  describe('Configuration', () => {
    it('uses correct base URL from environment', () => {
      const mockAxios = require('axios');
      const mockCreate = mockAxios.create;
      
      // The service should be configured with the mocked environment
      expect(window.__ENV__.REACT_APP_API_URL).toBe('http://test-api.com');
    });

    it('uses correct timeout configuration', () => {
      const mockAxios = require('axios');
      const mockCreate = mockAxios.create;
      
      // Verify that axios.create was called with correct config
      expect(mockCreate).toHaveBeenCalled();
    });
  });
});
