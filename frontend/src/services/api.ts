import axios, { AxiosInstance, AxiosResponse, AxiosError, AxiosRequestConfig } from 'axios';

const API_CONFIG = {
  BASE_URL: (window as any).__ENV__?.REACT_APP_API_URL || 'http://localhost:8000',
  TIMEOUT: 30000,
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000,
} as const;

export class APIError extends Error {
  constructor(
    message: string,
    public status: number,
    public code?: string,
    public details?: any
  ) {
    super(message);
    this.name = 'APIError';
  }
}

export class NetworkError extends Error {
  constructor(message: string, public originalError?: any) {
    super(message);
    this.name = 'NetworkError';
  }
}

export interface APIResponse<T = any> {
  data: T;
  message?: string;
  status: 'success' | 'error';
  timestamp: string;
}

export interface PaginatedResponse<T> extends APIResponse<T[]> {
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
}

const requestInterceptor = (config: any) => {
  const token = localStorage.getItem('auth_token');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  config.headers = {
    ...config.headers,
    'X-Request-ID': generateRequestId(),
    'X-Client-Version': (window as any).__ENV__?.REACT_APP_VERSION || '1.0.0',
  };

  return config;
};

const responseInterceptor = (response: AxiosResponse) => {
  if ((window as any).__ENV__?.NODE_ENV === 'development') {
    console.log(`✅ API Success: ${response.config.method?.toUpperCase()} ${response.config.url}`, response.data);
  }

  return response;
};

const errorInterceptor = async (error: AxiosError) => {
  const originalRequest = error.config as any;

  console.error('❌ API Error:', {
    url: error.config?.url,
    method: error.config?.method,
    status: error.response?.status,
    message: error.message,
    data: error.response?.data,
  });

  if (error.code === 'ECONNABORTED' && !originalRequest._retry) {
    originalRequest._retry = true;
    
    const delay = API_CONFIG.RETRY_DELAY * Math.pow(2, originalRequest._retryCount || 0);
    await new Promise(resolve => setTimeout(resolve, delay));
    
    return axios(originalRequest);
  }

  if (error.response) {
    const { status, data } = error.response;
    throw new APIError(
      (data as any)?.message || error.message,
      status,
      (data as any)?.code,
      data
    );
  } else if (error.request) {
    throw new NetworkError('Network error - no response received', error);
  } else {
    throw new NetworkError('Request setup failed', error);
  }
};

function generateRequestId(): string {
  return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

function createAxiosInstance(): AxiosInstance {
  const instance = axios.create({
    baseURL: API_CONFIG.BASE_URL,
    timeout: API_CONFIG.TIMEOUT,
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
  });

  instance.interceptors.request.use(requestInterceptor);
  instance.interceptors.response.use(responseInterceptor, errorInterceptor);

  return instance;
}

export const apiClient = createAxiosInstance();

export class APIService {
  private static instance: APIService;
  private client: AxiosInstance;

  private constructor() {
    this.client = apiClient;
  }

  public static getInstance(): APIService {
    if (!APIService.instance) {
      APIService.instance = new APIService();
    }
    return APIService.instance;
  }

  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    try {
      const response = await this.client.get<T>(url, config);
      return response.data;
    } catch (error) {
      this.handleError(error);
      throw error;
    }
  }

  async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    try {
      const response = await this.client.post<T>(url, data, config);
      return response.data;
    } catch (error) {
      this.handleError(error);
      throw error;
    }
  }

  async put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    try {
      const response = await this.client.put<T>(url, data, config);
      return response.data;
    } catch (error) {
      this.handleError(error);
      throw error;
    }
  }

  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    try {
      const response = await this.client.delete<T>(url, config);
      return response.data;
    } catch (error) {
      this.handleError(error);
      throw error;
    }
  }

  async upload<T>(url: string, file: File, onProgress?: (progress: number) => void): Promise<T> {
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await this.client.post<T>(url, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          if (onProgress && progressEvent.total) {
            const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            onProgress(progress);
          }
        },
      });

      return response.data;
    } catch (error) {
      this.handleError(error);
      throw error;
    }
  }

  async healthCheck(): Promise<boolean> {
    try {
      await this.client.get('/health', { timeout: 5000 });
      return true;
    } catch (error) {
      return false;
    }
  }

  private handleError(error: any): void {
    if ((window as any).__ENV__?.NODE_ENV === 'development') {
      console.error('API Service Error:', error);
    }

    if (error instanceof APIError) {
      switch (error.status) {
        case 401:
          localStorage.removeItem('auth_token');
          window.location.href = '/login';
          break;
        case 403:
          console.warn('Access forbidden:', error.message);
          break;
        case 429:
          console.warn('Rate limited:', error.message);
          break;
        case 500:
          console.error('Server error:', error.message);
          break;
      }
    }
  }
}

export const apiService = APIService.getInstance();

export type { AxiosInstance, AxiosResponse, AxiosRequestConfig };
