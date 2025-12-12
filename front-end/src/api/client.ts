/**
 * Axios client configuration for RPGChat.AI API
 */

import axios from 'axios';

// API base URL: use environment variable or fallback to localhost for development
// In Docker (nginx), the frontend proxies /api to the backend
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // 60 seconds for LLM calls
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
apiClient.interceptors.request.use(
  (config) => {
    console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response) {
      // Server responded with error status
      console.error(`[API Error] ${error.response.status}: ${error.response.data?.detail || error.message}`);
    } else if (error.request) {
      // Request was made but no response
      console.error('[API Error] No response from server. Is the backend running?');
    } else {
      console.error('[API Error]', error.message);
    }
    return Promise.reject(error);
  }
);

export default apiClient;

// ============================================
// Health Check Functions (root-level endpoints)
// ============================================

// Base URL for health checks (same host as API, but without /api path)
const HEALTH_BASE_URL = import.meta.env.VITE_API_URL 
  ? import.meta.env.VITE_API_URL.replace('/api', '') 
  : 'http://127.0.0.1:8000';

/**
 * Check if backend API is healthy
 */
export async function checkBackendHealth(): Promise<boolean> {
  try {
    const response = await axios.get(`${HEALTH_BASE_URL}/health`, { timeout: 5000 });
    return response.data?.status === 'healthy';
  } catch {
    return false;
  }
}

/**
 * Check if database is connected
 */
export async function checkDatabaseHealth(): Promise<boolean> {
  try {
    const response = await axios.get(`${HEALTH_BASE_URL}/health/db`, { timeout: 5000 });
    return response.data?.database === 'connected';
  } catch {
    return false;
  }
}

