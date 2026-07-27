import api from './client';

export async function getProblems(filters = {}) {
  const params = new URLSearchParams();
  if (filters.page) params.set('page', filters.page);
  if (filters.pageSize) params.set('page_size', filters.pageSize);
  if (filters.search) params.set('search', filters.search);
  if (filters.difficulty) params.set('difficulty', filters.difficulty);
  if (filters.topic) params.set('topic', filters.topic);
  const response = await api.get(`/problems?${params.toString()}`);
  return response.data;
}

export async function getProblemBySlug(slug) {
  const response = await api.get(`/problems/${slug}`);
  return response.data;
}

export async function getDraft(problemId, language = 'python') {
  const response = await api.get(`/problems/${problemId}/draft`, { params: { language } });
  return response.data;
}

export async function saveDraft(problemId, language, code) {
  const response = await api.put(`/problems/${problemId}/draft`, { language, code });
  return response.data;
}

export async function createProblem(data) {
  const response = await api.post('/admin/problems', data);
  return response.data;
}

export async function updateProblem(id, data) {
  const response = await api.put(`/admin/problems/${id}`, data);
  return response.data;
}

export async function createTestCase(problemId, data) {
  const response = await api.post(`/admin/problems/${problemId}/test-cases`, data);
  return response.data;
}

export async function runCode(problemId, language, sourceCode) {
  const response = await api.post('/execution/run', { problem_id: problemId, language, source_code: sourceCode });
  return response.data;
}

export async function submitCode(problemId, language, sourceCode) {
  const response = await api.post('/execution/submit', { problem_id: problemId, language, source_code: sourceCode });
  return response.data;
}

export async function getMySubmissions(params = {}) {
  const query = new URLSearchParams();
  if (params.page) query.set('page', params.page);
  if (params.pageSize) query.set('page_size', params.pageSize);
  if (params.problemId) query.set('problem_id', params.problemId);
  if (params.verdict) query.set('verdict', params.verdict);
  if (params.language) query.set('language', params.language);
  const response = await api.get(`/submissions/me?${query.toString()}`);
  return response.data;
}
