/**
 * Wand AI - Professional Custom Hooks
 * Senior-Level Implementation with React Query patterns and proper state management
 */

import { useState, useCallback, useRef, useEffect } from 'react';
import { apiService, APIError, NetworkError } from '../services/api';

// Hook return types
export interface UseAPIState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  success: boolean;
}

export interface UseAPIResult<T> extends UseAPIState<T> {
  execute: (...args: any[]) => Promise<void>;
  reset: () => void;
  refetch: () => Promise<void>;
}

export interface UseAPIOptions {
  immediate?: boolean;
  onSuccess?: (data: any) => void;
  onError?: (error: string) => void;
  retryCount?: number;
  retryDelay?: number;
}

// Generic API hook with advanced features
export function useAPI<T = any>(
  apiCall: (...args: any[]) => Promise<T>,
  options: UseAPIOptions = {}
): UseAPIResult<T> {
  const [state, setState] = useState<UseAPIState<T>>({
    data: null,
    loading: false,
    error: null,
    success: false,
  });

  const { immediate = false, onSuccess, onError, retryCount = 3, retryDelay = 1000 } = options;
  const abortControllerRef = useRef<AbortController | null>(null);
  const retryCountRef = useRef(0);

  // Reset state
  const reset = useCallback(() => {
    setState({
      data: null,
      loading: false,
      error: null,
      success: false,
    });
    retryCountRef.current = 0;
  }, []);

  // Execute API call with retry logic
  const execute = useCallback(
    async (...args: any[]) => {
      // Cancel previous request if still pending
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }

      // Create new abort controller
      abortControllerRef.current = new AbortController();

      setState(prev => ({ ...prev, loading: true, error: null, success: false }));

      try {
        const result = await apiCall(...args);
        
        setState({
          data: result,
          loading: false,
          error: null,
          success: true,
        });

        onSuccess?.(result);
        retryCountRef.current = 0;

      } catch (error) {
        // Handle abort
        if (abortControllerRef.current?.signal.aborted) {
          return;
        }

        const errorMessage = error instanceof Error ? error.message : 'An unknown error occurred';
        
        // Implement retry logic
        if (retryCountRef.current < retryCount && shouldRetry(error)) {
          retryCountRef.current++;
          
          setTimeout(() => {
            execute(...args);
          }, retryDelay * Math.pow(2, retryCountRef.current - 1));
          
          return;
        }

        setState(prev => ({
          ...prev,
          loading: false,
          error: errorMessage,
          success: false,
        }));

        onError?.(errorMessage);
        retryCountRef.current = 0;
      }
    },
    [apiCall, onSuccess, onError, retryCount, retryDelay]
  );

  // Refetch function
  const refetch = useCallback(async () => {
    if (state.data !== null) {
      await execute();
    }
  }, [execute, state.data]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  // Execute immediately if requested
  useEffect(() => {
    if (immediate) {
      execute();
    }
  }, [immediate, execute]);

  return {
    ...state,
    execute,
    reset,
    refetch,
  };
}

// Specialized hooks for common operations
export function useGet<T = any>(url: string, options?: UseAPIOptions): UseAPIResult<T> {
  const apiCall = useCallback(() => apiService.get<T>(url), [url]);
  return useAPI(apiCall, options);
}

export function usePost<T = any>(url: string, options?: UseAPIOptions): UseAPIResult<T> {
  const apiCall = useCallback((data?: any) => apiService.post<T>(url, data), [url]);
  return useAPI(apiCall, options);
}

export function usePut<T = any>(url: string, options?: UseAPIOptions): UseAPIResult<T> {
  const apiCall = useCallback((data?: any) => apiService.put<T>(url, data), [url]);
  return useAPI(apiCall, options);
}

export function useDelete<T = any>(url: string, options?: UseAPIOptions): UseAPIResult<T> {
  const apiCall = useCallback(() => apiService.delete<T>(url), [url]);
  return useAPI(apiCall, options);
}

export function useUpload<T = any>(url: string, options?: UseAPIOptions): UseAPIResult<T> {
  const apiCall = useCallback((file: File, onProgress?: (progress: number) => void) => 
    apiService.upload<T>(url, file, onProgress), [url]);
  return useAPI(apiCall, options);
}

// Utility function to determine if request should be retried
function shouldRetry(error: any): boolean {
  // Don't retry on client errors (4xx)
  if (error instanceof APIError && error.status >= 400 && error.status < 500) {
    return false;
  }
  
  // Don't retry on network errors that aren't timeout-related
  if (error instanceof NetworkError) {
    return true; // Retry network errors
  }
  
  // Retry on server errors (5xx) and timeouts
  return error instanceof APIError && error.status >= 500;
}

// Hook for managing multiple API calls
export function useMultipleAPIs<T extends Record<string, any>>(
  apiCalls: Record<keyof T, () => Promise<any>>,
  options?: UseAPIOptions
) {
  const [results, setResults] = useState<Partial<T>>({});
  const [loading, setLoading] = useState<Record<keyof T, boolean>>({} as any);
  const [errors, setErrors] = useState<Record<keyof T, string | null>>({} as any);

  const executeAll = useCallback(async () => {
    const keys = Object.keys(apiCalls) as (keyof T)[];
    
    // Set all to loading
    setLoading(prev => {
      const newLoading = { ...prev };
      keys.forEach(key => newLoading[key] = true);
      return newLoading;
    });

    // Clear previous errors
    setErrors(prev => {
      const newErrors = { ...prev };
      keys.forEach(key => newErrors[key] = null);
      return newErrors;
    });

    try {
      const promises = keys.map(async (key) => {
        try {
          const result = await apiCalls[key]();
          setResults(prev => ({ ...prev, [key]: result }));
          setLoading(prev => ({ ...prev, [key]: false }));
          return { key, success: true, data: result };
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Unknown error';
          setErrors(prev => ({ ...prev, [key]: errorMessage }));
          setLoading(prev => ({ ...prev, [key]: false }));
          return { key, success: false, error: errorMessage };
        }
      });

      await Promise.allSettled(promises);
    } catch (error) {
      console.error('Multiple API execution failed:', error);
    }
  }, [apiCalls]);

  const reset = useCallback(() => {
    setResults({});
    setLoading({} as any);
    setErrors({} as any);
  }, []);

  return {
    results,
    loading,
    errors,
    executeAll,
    reset,
    isLoading: Object.values(loading).some(Boolean),
    hasErrors: Object.values(errors).some(Boolean),
  };
}

// Hook for real-time data updates
export function useRealtimeData<T>(
  fetchData: () => Promise<T>,
  interval: number = 5000,
  enabled: boolean = true
): UseAPIResult<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const execute = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await fetchData();
      setData(result);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch data';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [fetchData]);

  // Set up interval
  useEffect(() => {
    if (enabled && interval > 0) {
      execute(); // Initial fetch
      intervalRef.current = setInterval(execute, interval);
      
      return () => {
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
        }
      };
    }
  }, [enabled, interval, execute]);

  const reset = useCallback(() => {
    setData(null);
    setLoading(false);
    setError(null);
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }
  }, []);

  return {
    data,
    loading,
    error,
    success: data !== null && error === null,
    execute,
    reset,
    refetch: execute,
  };
}
