const config = {
  // API base URL - this should match your Django backend URL
  apiBaseUrl: 'http://localhost:8000/api',
  
  // API endpoints
  endpoints: {
    bills: {
      list: '/bills/',
      create: '/bills/create/',
      detail: (id) => `/bills/${id}/`,
      activities: (id) => `/bills/${id}/activities/`,
      customers: '/customers/'
    }
  },
  
  // Default page size for pagination
  pageSize: 10,
  
  // Date format options
  dateFormat: {
    date: 'MM/DD/YYYY',
    dateTime: 'MM/DD/YYYY hh:mm A',
    apiDateFormat: 'YYYY-MM-DD',
    apiDateTimeFormat: 'YYYY-MM-DDTHH:mm:ssZ'
  }
};

export default config;
