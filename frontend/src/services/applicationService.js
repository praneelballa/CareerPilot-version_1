import apiClient from './api';

export const fetchResumeOptimizations = async (candidateId, jobId) => {
  const response = await apiClient.post('/api/v1/applications/optimize', {
    candidate_id: candidateId,
    job_id: jobId,
  });
  return response.data;
};

export const createApplicationDraft = async (candidateId, jobId, recipient = null) => {
  const response = await apiClient.post('/api/v1/applications/generate', {
    candidate_id: candidateId,
    job_id: jobId,
    recipient,
  });
  return response.data;
};

export const applySelectedResumeChanges = async (appId, selectedSuggestionIds) => {
  const response = await apiClient.post(`/api/v1/applications/${appId}/resume-changes`, {
    selected_suggestion_ids: selectedSuggestionIds,
  });
  return response.data;
};

export const approveApplicationDraft = async (appId) => {
  const response = await apiClient.post(`/api/v1/applications/${appId}/approve`);
  return response.data;
};

export const fetchApplicationById = async (appId) => {
  const response = await apiClient.get(`/api/v1/applications/${appId}`);
  return response.data;
};