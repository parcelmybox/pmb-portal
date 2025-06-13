import axios from 'axios';
import config from '../config';

// Create axios instance with base URL
const api = axios.create({
  baseURL: config.apiBaseUrl,
  headers: {
    'Content-Type': 'application/json',
    'X-Requested-With': 'XMLHttpRequest',
  },
  withCredentials: true, // Important for CSRF
});

// Request interceptor to add auth token if available
api.interceptors.request.use(
  (config) => {
    // You can add auth token here if needed
    // const token = localStorage.getItem('auth_token');
    // if (token) {
    //   config.headers.Authorization = `Token ${token}`;
    // }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle common errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle common errors (401, 403, 404, 500, etc.)
    if (error.response) {
      switch (error.response.status) {
        case 401:
          // Handle unauthorized
          console.error('Unauthorized access - please log in');
          break;
        case 403:
          // Handle forbidden
          console.error('You do not have permission to perform this action');
          break;
        case 404:
          // Handle not found
          console.error('The requested resource was not found');
          break;
        case 500:
          // Handle server error
          console.error('A server error occurred');
          break;
        default:
          console.error('An error occurred:', error.response.status);
      }
    } else if (error.request) {
      // The request was made but no response was received
      console.error('No response received from server');
    } else {
      // Something happened in setting up the request
      console.error('Error setting up request:', error.message);
    }
    return Promise.reject(error);
  }
);

// API methods
export const billingApi = {
  // Get all bills with optional filters
  getBills: (params = {}) => {
    return api.get(config.endpoints.bills.list, { params });
  },
  
  // Get a single bill by ID
  getBill: (id) => {
    return api.get(config.endpoints.bills.detail(id));
  },
  
  // Create a new bill
  createBill: (data) => {
    return api.post(config.endpoints.bills.create, data);
  },
  
  // Update an existing bill
  updateBill: (id, data) => {
    return api.put(config.endpoints.bills.detail(id), data);
  },
  
  // Get activity history for a bill
  getBillActivities: (id) => {
    return api.get(config.endpoints.bills.activities(id));
  },
  
  // Get customers list
  getCustomers: () => {
    return api.get(config.endpoints.bills.customers);
  },
};

export default api;
