import api from './client';

export async function getRoadmap() {
  const response = await api.get('/student/career-roadmap');
  return response.data;
}

export async function createRoadmap(payload) {
  const response = await api.post('/student/career-roadmap', payload);
  return response.data;
}

export async function updateRoadmap(roadmapId, payload) {
  const response = await api.put(`/student/career-roadmap/${roadmapId}`, payload);
  return response.data;
}

export async function createMilestone(roadmapId, payload) {
  const response = await api.post(`/student/career-roadmap/${roadmapId}/milestones`, payload);
  return response.data;
}

export async function updateMilestone(milestoneId, payload) {
  const response = await api.put(`/student/career-roadmap/milestones/${milestoneId}`, payload);
  return response.data;
}

export async function getAISuggestions() {
  const response = await api.get('/student/career-roadmap/ai-suggestions');
  return response.data;
}

export async function listWeeklyGoals() {
  const response = await api.get('/student/career-roadmap/weekly-goals');
  return response.data;
}

export async function createWeeklyGoal(payload) {
  const response = await api.post('/student/career-roadmap/weekly-goals', payload);
  return response.data;
}

export async function listMonthlyGoals() {
  const response = await api.get('/student/career-roadmap/monthly-goals');
  return response.data;
}

export async function createMonthlyGoal(payload) {
  const response = await api.post('/student/career-roadmap/monthly-goals', payload);
  return response.data;
}

