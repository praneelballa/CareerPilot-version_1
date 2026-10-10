import apiClient from './api';

export const analyzeJobMatch = async (candidateId, jobId) => {
  const response = await apiClient.post('/api/v1/matching/analyze', {
    candidate_id: candidateId,
    job_id: jobId,
  });
  return response.data;
};