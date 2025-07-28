import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create an axios instance for authenticated requests
const axiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    'Accept': 'application/json',
  },
  timeout: 10000, // 10 seconds timeout
});

// Flag to prevent multiple token refresh attempts
let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

// Add a request interceptor to handle token refresh
axiosInstance.interceptors.request.use(
  (config) => {
    const isAuthEndpoint = config.url.includes('/auth/');
    const isTokenRefresh = config.url.endsWith('/token/refresh/');
    const isSupportRequest = config.url.endsWith('/support-requests/') && config.method === 'post';
    
    // For support requests, explicitly remove any Authorization header and common auth headers
    if (isSupportRequest) {
      // Completely remove the Authorization header
      if (config.headers) {
        delete config.headers.Authorization;
        delete config.headers.authorization;
        delete config.headers.common?.Authorization;
        delete config.headers.common?.authorization;
      }
      // Ensure we don't send any tokens in the request
      config.withCredentials = false;
    } 
    // Only add Authorization header for authenticated endpoints
    else if (!isAuthEndpoint && !isTokenRefresh) {
      const accessToken = localStorage.getItem('access_token');
      if (accessToken) {
        config.headers.Authorization = `Bearer ${accessToken}`;
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add a response interceptor to handle token refresh
axiosInstance.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // If the error is 401 and we haven't tried to refresh the token yet
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // If we're already refreshing the token, queue the request
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`;
            return axios(originalRequest);
          })
          .catch((err) => {
            return Promise.reject(err);
          });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) {
          throw new Error('No refresh token available');
        }

        // Get new access token
        const response = await axios.post(
          `${API_URL}/auth/token/refresh/`,
          { refresh: refreshToken },
          {
            headers: {
              'Content-Type': 'application/json',
            },
          }
        );

        const { access } = response.data;
        localStorage.setItem('access_token', access);
        
        // Update the Authorization header
        originalRequest.headers.Authorization = `Bearer ${access}`;
        
        // Process any queued requests
        processQueue(null, access);
        
        // Retry the original request
        return axios(originalRequest);
      } catch (error) {
        // If refresh fails, clear tokens and redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        processQueue(error, null);
        return Promise.reject(error);
      } finally {
        isRefreshing = false;
      }
    }
    
    return Promise.reject(error);
  }
);

export { axiosInstance, API_URL };
export default axiosInstance;
