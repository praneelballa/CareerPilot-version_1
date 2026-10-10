import apiClient from './api';

export const uploadResumeFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await apiClient.post('/api/v1/resume/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const triggerResumeAnalysis = async (candidateId) => {
  const response = await apiClient.post('/api/v1/resume/analyze', {
    candidate_id: candidateId,
  });
  return response.data;
};

export const fetchCandidateProfile = async (candidateId) => {
  const response = await apiClient.get(`/api/v1/resume/candidate/${candidateId}`);
  return response.data;
};