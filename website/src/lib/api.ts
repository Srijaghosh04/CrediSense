import axios from 'axios';
import { supabase } from './supabase';

const API_BASE_URL = 'http://127.0.0.1:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
});

// Add a request interceptor to include the JWT token
apiClient.interceptors.request.use(async (config) => {
  const { data: { session } } = await supabase.auth.getSession();
  if (session?.access_token) {
    config.headers.Authorization = `Bearer ${session.access_token}`;
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

export const api = {
  uploadDocument: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    try {
      const response = await apiClient.post(`/ingest/document`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      console.error("Error uploading document:", error);
      throw error;
    }
  },

  researchCompany: async (companyName: string) => {
    try {
      const response = await apiClient.get(`/research/company/${encodeURIComponent(companyName)}`);
      return response.data;
    } catch (error) {
      console.error("Error researching company:", error);
      throw error;
    }
  },

  generateCAM: async (payload: {
    application_id: string;
    company_data: any;
    research_data: any;
    primary_insights: string;
  }) => {
    try {
      const response = await apiClient.post(`/engine/generate-cam`, payload);
      return response.data;
    } catch (error) {
      console.error("Error generating CAM:", error);
      throw error;
    }
  }
};
