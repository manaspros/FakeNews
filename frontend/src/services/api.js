import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: process.env.NODE_ENV === 'development'
    ? 'http://localhost:8000'
    : '',
  timeout: 30000,
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// API functions
export const apiService = {
  // Health check
  healthCheck: () => api.get('/health'),

  // Companies
  getCompanies: () => api.get('/companies'),
  addCompany: (companyData) => api.post('/companies', companyData),
  getCompanyStats: (companyName) => api.get(`/companies/${companyName}/stats`),
  getCompanyNews: (companyName, limit = 20) =>
    api.get(`/companies/${companyName}/news?limit=${limit}`),
  getCompanyAnalyses: (companyName, limit = 10) =>
    api.get(`/companies/${companyName}/analyses?limit=${limit}`),

  // Analysis
  analyzeCompany: (analysisData) => api.post('/analyze', analysisData),

  // News
  addNewsUpdate: (newsData) => api.post('/news', newsData),

  // Alerts
  getAlerts: (companyName = null) =>
    api.get('/alerts', { params: companyName ? { company_name: companyName } : {} }),
  markAlertRead: (alertId) => api.post(`/alerts/${alertId}/read`),

  // File upload
  uploadDocument: (companyName, docType, file) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('company', companyName);
    formData.append('doc_type', docType);

    return api.post('/upload-document', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
};

export default api;