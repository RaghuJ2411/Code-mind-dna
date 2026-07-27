import api from './client';

export async function listAssessments(assessmentType, difficulty) {
  const params = {};
  if (assessmentType) params.assessment_type = assessmentType;
  if (difficulty) params.difficulty = difficulty;
  const response = await api.get('/student/assessments', { params });
  return response.data;
}

export async function getAssessment(assessmentId) {
  const response = await api.get(`/student/assessments/${assessmentId}`);
  return response.data;
}

export async function startAssessment(assessmentId) {
  const response = await api.post(`/student/assessments/${assessmentId}/start`);
  return response.data;
}

export async function submitAssessment(assessmentId, answers) {
  const response = await api.post(`/student/assessments/${assessmentId}/submit`, { answers });
  return response.data;
}

export async function getAssessmentHistory() {
  const response = await api.get('/student/assessments/results/history');
  return response.data;
}

export async function getAssessmentResult(attemptId) {
  const response = await api.get(`/student/assessments/results/${attemptId}`);
  return response.data;
}

export async function getPerformanceAnalysis() {
  const response = await api.get('/student/assessments/performance/analysis');
  return response.data;
}

