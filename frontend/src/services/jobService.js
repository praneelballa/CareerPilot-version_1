import apiClient from './api';

export const searchLiveJobs = async ({ role, location, remoteOnly = false, limit = 20 }) => {
  const response = await apiClient.post('/api/v1/jobs/search', {
    role,
    location: location || null,
    remote_only: remoteOnly,
    limit,
  });
  return response.data;
};

export const fetchStoredJobs = async () => {
  const response = await apiClient.get('/api/v1/jobs');
  return response.data;
};