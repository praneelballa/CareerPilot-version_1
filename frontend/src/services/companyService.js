import apiClient from './api';

export const fetchCompanyResearch = async (jobId) => {
  const response = await apiClient.post('/api/v1/company/research', {
    job_id: jobId,
  });
  return response.data;
};