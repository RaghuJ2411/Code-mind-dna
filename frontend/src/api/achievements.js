import api from './client';

export async function listAchievements(category) {
  const params = {};
  if (category) params.category = category;
  const response = await api.get('/student/achievements', { params });
  return response.data;
}

export async function listEarnedAchievements() {
  const response = await api.get('/student/achievements/earned');
  return response.data;
}

export async function listMilestones() {
  const response = await api.get('/student/achievements/milestones');
  return response.data;
}

export async function getLeaderboard(limit = 20) {
  const response = await api.get('/student/achievements/leaderboard', { params: { limit } });
  return response.data;
}

