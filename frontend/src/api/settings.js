import api from './client';

export async function getProfile() {
  const response = await api.get('/student/settings/profile');
  return response.data;
}

export async function updateProfile(payload) {
  const response = await api.put('/student/settings/profile', payload);
  return response.data;
}

export async function uploadPhoto(file) {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post('/student/settings/photo', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
}

export async function changePassword(payload) {
  const response = await api.put('/student/settings/password', payload);
  return response.data;
}

export async function getSettings() {
  const response = await api.get('/student/settings');
  return response.data;
}

export async function updateSettings(payload) {
  const response = await api.put('/student/settings', payload);
  return response.data;
}

export async function enableTwoFactor(secret, code) {
  const response = await api.post('/student/settings/2fa/enable', { secret, code });
  return response.data;
}

export async function disableTwoFactor(code) {
  const response = await api.post('/student/settings/2fa/disable', { code });
  return response.data;
}

export async function verifyTwoFactor(code) {
  const response = await api.post('/student/settings/2fa/verify', { code });
  return response.data;
}

