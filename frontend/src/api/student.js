import api from './client';

export async function getDashboardOverview() {
  const response = await api.get('/student/dashboard/overview');
  return response.data;
}

export async function refreshRecommendations() {
  const response = await api.post('/student/recommendations/refresh');
  return response.data;
}

export async function listRecommendations() {
  const response = await api.get('/student/recommendations');
  return response.data;
}

export async function listGoals() {
  const response = await api.get('/student/goals');
  return response.data;
}

export async function startRecommendation(recommendationId) {
  const response = await api.post(`/student/recommendations/${recommendationId}/start`);
  return response.data;
}

export async function completeRecommendation(recommendationId) {
  const response = await api.post(`/student/recommendations/${recommendationId}/complete`);
  return response.data;
}

export async function dismissRecommendation(recommendationId) {
  const response = await api.post(`/student/recommendations/${recommendationId}/dismiss`);
  return response.data;
}

export async function createGoal(payload) {
  const response = await api.post('/student/goals', payload);
  return response.data;
}

export async function updateGoal(goalId, payload) {
  const response = await api.patch(`/student/goals/${goalId}`, payload);
  return response.data;
}

export async function deleteGoal(goalId) {
  const response = await api.delete(`/student/goals/${goalId}`);
  return response.data;
}

export async function getAnalyticsProfile() {
  const response = await api.get('/analytics/profile');
  return response.data;
}

export async function getDnaProfile() {
  const response = await api.get('/dna/profile');
  return response.data;
}

export async function getDnaProfileHistory() {
  const response = await api.get('/dna/profile/history');
  return response.data;
}

export async function getAnalyticsDaily() {
  const response = await api.get('/analytics/daily');
  return response.data;
}

export async function getAnalyticsWeekly() {
  const response = await api.get('/analytics/weekly');
  return response.data;
}

export async function requestCodeReview(submissionId) {
  const response = await api.post(`/student/ai/code-review/${submissionId}`);
  return response.data;
}

export async function getCodeReview(submissionId) {
  const response = await api.get(`/student/ai/code-review/${submissionId}`);
  return response.data;
}

export async function requestErrorExplanation(submissionId) {
  const response = await api.post(`/student/ai/error-explanation/${submissionId}`);
  return response.data;
}

export async function requestSkillGap(submissionId) {
  const response = await api.post(`/student/ai/skill-gap/${submissionId}`);
  return response.data;
}

export async function requestRoadmap(submissionId) {
  const response = await api.post(`/student/ai/roadmap/${submissionId}`);
  return response.data;
}

export async function getAIUsageHistory() {
  const response = await api.get('/student/ai/usage-history');
  return response.data;
}

export async function getStudentJobs() {
  const response = await api.get('/student/jobs');
  return response.data;
}

export async function applyToStudentJob(jobId) {
  const response = await api.post(`/student/jobs/${jobId}/apply`);
  return response.data;
}

export async function getStudentApplications() {
  const response = await api.get('/student/applications');
  return response.data;
}

export async function getCareerOverview() {
  const response = await api.get('/student/career/overview');
  return response.data;
}

export async function getCareerRoles() {
  const response = await api.get('/student/career/roles');
  return response.data;
}

export async function getCareerRole(roleId) {
  const response = await api.get(`/student/career/roles/${roleId}`);
  return response.data;
}

export async function getResumeEntries() {
  const response = await api.get('/student/resume');
  return response.data;
}

export async function createResumeEntry(payload) {
  const response = await api.post('/student/resume', payload);
  return response.data;
}

export async function getProjects() {
  const response = await api.get('/student/projects');
  return response.data;
}

export async function createProject(payload) {
  const response = await api.post('/student/projects', payload);
  return response.data;
}

export async function getInterviewHistory() {
  const response = await api.get('/student/interview/history');
  return response.data;
}

export async function practiceInterview(payload) {
  const response = await api.post('/student/interview/practice', payload);
  return response.data;
}
