import api from './client';

export async function getDailyProgress(days = 30) {
  const response = await api.get('/student/progress/daily', { params: { days } });
  return response.data;
}

export async function getWeeklyProgress(weeks = 12) {
  const response = await api.get('/student/progress/weekly', { params: { weeks } });
  return response.data;
}

export async function getMonthlyProgress(months = 12) {
  const response = await api.get('/student/progress/monthly', { params: { months } });
  return response.data;
}

export async function getCodingHeatmap(year) {
  const params = {};
  if (year) params.year = year;
  const response = await api.get('/student/progress/heatmap', { params });
  return response.data;
}

export async function getSkillGrowth(days = 90) {
  const response = await api.get('/student/progress/skill-growth', { params: { days } });
  return response.data;
}

export async function getGoalProgress() {
  const response = await api.get('/student/progress/goals');
  return response.data;
}

export async function getProgressOverview() {
  const response = await api.get('/student/progress/overview');
  return response.data;
}

