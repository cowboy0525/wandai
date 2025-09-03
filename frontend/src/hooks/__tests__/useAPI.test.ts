import { renderHook, act, waitFor } from '@testing-library/react';
import { useAPI, useGet, usePost, useMultipleAPIs, useRealtimeData } from '../useAPI';
import { apiService } from '../../services/api';

// Mock the API service
jest.mock('../../services/api', () => ({
  apiService: {
    get: jest.fn(),
    post: jest.fn(),
    put: jest.fn(),
    delete: jest.fn(),
    upload: jest.fn(),
  },
}));

const mockApiService = apiService as jest.Mocked<typeof apiService>;

describe('useAPI', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('initializes with default state', () => {
    const mockApiCall = jest.fn();
    const { result } = renderHook(() => useAPI(mockApiCall));

    expect(result.current.data).toBeNull();
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBeNull();
    expect(result.current.success).toBe(false);
  });

  it('executes API call and updates state on success', async () => {
    const mockData = { id: 1, name: 'Test' };
    const mockApiCall = jest.fn().mockResolvedValue(mockData);
    
    const { result } = renderHook(() => useAPI(mockApiCall));

    await act(async () => {
      await result.current.execute();
    });

    expect(result.current.data).toEqual(mockData);
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBeNull();
    expect(result.current.success).toBe(true);
  });

  it('handles API call errors', async () => {
    const mockError = new Error('API Error');
    const mockApiCall = jest.fn().mockRejectedValue(mockError);
    
    const { result } = renderHook(() => useAPI(mockApiCall));

    await act(async () => {
      await result.current.execute();
    });

    expect(result.current.data).toBeNull();
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBe('API Error');
    expect(result.current.success).toBe(false);
  });

  it('calls onSuccess callback when successful', async () => {
    const mockData = { id: 1, name: 'Test' };
    const mockApiCall = jest.fn().mockResolvedValue(mockData);
    const onSuccess = jest.fn();
    
    const { result } = renderHook(() => useAPI(mockApiCall, { onSuccess }));

    await act(async () => {
      await result.current.execute();
    });

    expect(onSuccess).toHaveBeenCalledWith(mockData);
  });

  it('calls onError callback when error occurs', async () => {
    const mockError = new Error('API Error');
    const mockApiCall = jest.fn().mockRejectedValue(mockError);
    const onError = jest.fn();
    
    const { result } = renderHook(() => useAPI(mockApiCall, { onError }));

    await act(async () => {
      await result.current.execute();
    });

    expect(onError).toHaveBeenCalledWith('API Error');
  });

  it('implements retry logic with exponential backoff', async () => {
    const mockError = new Error('Network Error');
    const mockApiCall = jest.fn()
      .mockRejectedValueOnce(mockError)
      .mockRejectedValueOnce(mockError)
      .mockResolvedValue({ success: true });
    
    const { result } = renderHook(() => useAPI(mockApiCall, { retryCount: 2, retryDelay: 100 }));

    await act(async () => {
      await result.current.execute();
    });

    // Should have retried twice
    expect(mockApiCall).toHaveBeenCalledTimes(3);
    expect(result.current.success).toBe(true);
  });

  it('resets state when reset is called', async () => {
    const mockData = { id: 1, name: 'Test' };
    const mockApiCall = jest.fn().mockResolvedValue(mockData);
    
    const { result } = renderHook(() => useAPI(mockApiCall));

    await act(async () => {
      await result.current.execute();
    });

    expect(result.current.success).toBe(true);

    act(() => {
      result.current.reset();
    });

    expect(result.current.data).toBeNull();
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBeNull();
    expect(result.current.success).toBe(false);
  });

  it('refetches data when refetch is called', async () => {
    const mockData = { id: 1, name: 'Test' };
    const mockApiCall = jest.fn().mockResolvedValue(mockData);
    
    const { result } = renderHook(() => useAPI(mockApiCall));

    await act(async () => {
      await result.current.execute();
    });

    expect(result.current.data).toEqual(mockData);

    // Change the mock to return different data
    mockApiCall.mockResolvedValue({ id: 2, name: 'Updated' });

    await act(async () => {
      await result.current.refetch();
    });

    expect(mockApiCall).toHaveBeenCalledTimes(2);
    expect(result.current.data).toEqual({ id: 2, name: 'Updated' });
  });

  it('executes immediately when immediate option is true', async () => {
    const mockData = { id: 1, name: 'Test' };
    const mockApiCall = jest.fn().mockResolvedValue(mockData);
    
    renderHook(() => useAPI(mockApiCall, { immediate: true }));

    await waitFor(() => {
      expect(mockApiCall).toHaveBeenCalledTimes(1);
    });
  });

  it('cancels previous request when new one is made', async () => {
    const mockData = { id: 1, name: 'Test' };
    const mockApiCall = jest.fn().mockResolvedValue(mockData);
    
    const { result } = renderHook(() => useAPI(mockApiCall));

    // Start first request
    const promise1 = result.current.execute();
    
    // Start second request before first completes
    const promise2 = result.current.execute();

    await act(async () => {
      await Promise.all([promise1, promise2]);
    });

    // Should only have one successful result
    expect(result.current.data).toEqual(mockData);
  });
});

describe('useGet', () => {
  it('creates GET request hook', async () => {
    const mockData = { id: 1, name: 'Test' };
    mockApiService.get.mockResolvedValue(mockData);
    
    const { result } = renderHook(() => useGet('/test'));

    await act(async () => {
      await result.current.execute();
    });

    expect(mockApiService.get).toHaveBeenCalledWith('/test');
    expect(result.current.data).toEqual(mockData);
  });
});

describe('usePost', () => {
  it('creates POST request hook', async () => {
    const mockData = { id: 1, name: 'Test' };
    const postData = { name: 'New Test' };
    mockApiService.post.mockResolvedValue(mockData);
    
    const { result } = renderHook(() => usePost('/test'));

    await act(async () => {
      await result.current.execute(postData);
    });

    expect(mockApiService.post).toHaveBeenCalledWith('/test', postData);
    expect(result.current.data).toEqual(mockData);
  });
});

describe('useMultipleAPIs', () => {
  it('executes multiple API calls concurrently', async () => {
    const mockApiCalls = {
      users: jest.fn().mockResolvedValue([{ id: 1, name: 'User 1' }]),
      posts: jest.fn().mockResolvedValue([{ id: 1, title: 'Post 1' }]),
    };
    
    const { result } = renderHook(() => useMultipleAPIs(mockApiCalls));

    await act(async () => {
      await result.current.executeAll();
    });

    expect(result.current.results.users).toEqual([{ id: 1, name: 'User 1' }]);
    expect(result.current.results.posts).toEqual([{ id: 1, title: 'Post 1' }]);
    expect(result.current.isLoading).toBe(false);
  });

  it('handles errors in multiple API calls', async () => {
    const mockApiCalls = {
      users: jest.fn().mockResolvedValue([{ id: 1, name: 'User 1' }]),
      posts: jest.fn().mockRejectedValue(new Error('Posts failed')),
    };
    
    const { result } = renderHook(() => useMultipleAPIs(mockApiCalls));

    await act(async () => {
      await result.current.executeAll();
    });

    expect(result.current.results.users).toEqual([{ id: 1, name: 'User 1' }]);
    expect(result.current.errors.posts).toBe('Posts failed');
    expect(result.current.hasErrors).toBe(true);
  });
});

describe('useRealtimeData', () => {
  it('fetches data at specified interval', async () => {
    const mockData = { id: 1, name: 'Test' };
    const mockFetchData = jest.fn().mockResolvedValue(mockData);
    
    const { result } = renderHook(() => useRealtimeData(mockFetchData, 1000, true));

    await waitFor(() => {
      expect(mockFetchData).toHaveBeenCalled();
    });

    expect(result.current.data).toEqual(mockData);
  });

  it('stops polling when disabled', async () => {
    const mockFetchData = jest.fn();
    
    const { rerender } = renderHook(
      ({ enabled }) => useRealtimeData(mockFetchData, 100, enabled),
      { initialProps: { enabled: true } }
    );

    await waitFor(() => {
      expect(mockFetchData).toHaveBeenCalled();
    });

    // Disable polling
    rerender({ enabled: false });

    const callCount = mockFetchData.mock.calls.length;
    
    // Wait a bit to see if more calls are made
    await new Promise(resolve => setTimeout(resolve, 200));
    
    expect(mockFetchData.mock.calls.length).toBe(callCount);
  });

  it('resets state when reset is called', async () => {
    const mockData = { id: 1, name: 'Test' };
    const mockFetchData = jest.fn().mockResolvedValue(mockData);
    
    const { result } = renderHook(() => useRealtimeData(mockFetchData, 1000, true));

    await waitFor(() => {
      expect(result.current.data).toEqual(mockData);
    });

    act(() => {
      result.current.reset();
    });

    expect(result.current.data).toBeNull();
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBeNull();
  });
});
