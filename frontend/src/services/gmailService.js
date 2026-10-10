import apiClient from './api';

export const fetchGmailStatus = async () => {
  const response = await apiClient.get('/api/v1/gmail/status');
  return response.data;
};

export const getGmailConnectUrl = async () => {
  const response = await apiClient.get('/api/v1/gmail/connect');
  return response.data.authorization_url;
};

export const approveApplicationHumanGate = async (appId, { recipient, subject, body, humanConfirmed }) => {
  const response = await apiClient.post(`/api/v1/applications/${appId}/approve`, {
    recipient,
    subject,
    body,
    human_confirmed: humanConfirmed,
  });
  return response.data;
};

export const dispatchApplicationGmail = async (appId) => {
  const response = await apiClient.post(`/api/v1/applications/${appId}/send`);
  return response.data;
};

export const fetchAllApplications = async () => {
  const response = await apiClient.get('/api/v1/applications/');
  return response.data;
};