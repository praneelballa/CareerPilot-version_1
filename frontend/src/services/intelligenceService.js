import apiClient from './api';

export const autoDiscoverJobsForCandidate = async (candidateId, location = '', remoteOnly = false) => {
  const response = await apiClient.post('/api/v1/intelligence/auto-discover', {
    candidate_id: candidateId,
    location: location || null,
    remote_only: remoteOnly,
    limit: 25,
  });
  return response.data;
};

export const fetchResumeTailoring = async (candidateId, jobId) => {
  const response = await apiClient.post('/api/v1/intelligence/tailor-resume', {
    candidate_id: candidateId,
    job_id: jobId,
  });
  return response.data;
};

export const fetchApplicationEmail = async (candidateId, jobId) => {
  const response = await apiClient.post('/api/v1/intelligence/generate-email', {
    candidate_id: candidateId,
    job_id: jobId,
  });
  return response.data;
};