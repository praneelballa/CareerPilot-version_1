import apiClient from './api';

export const fetchSystemHealth = async () => {
  const response = await apiClient.get('/health');
  return response.data;
};