import api from './client';

export async function getRecruiterDashboard() {
  const response = await api.get('/recruiter/dashboard');
  return response.data;
}

export async function listRecruiterJobs(filters = {}) {
  const response = await api.get('/recruiter/jobs', { params: filters });
  return response.data;
}

export async function getRecruiterJob(jobId) {
  const response = await api.get(`/recruiter/jobs/${jobId}`);
  return response.data;
}

export async function createRecruiterJob(payload) {
  const response = await api.post('/recruiter/jobs', payload);
  return response.data;
}

export async function listRecruiterCandidates(filters = {}) {
  const response = await api.get('/recruiter/candidates', { params: filters });
  return response.data;
}

export async function getRecruiterCandidate(candidateId) {
  const response = await api.get(`/recruiter/candidates/${candidateId}`);
  return response.data;
}

// ─── Interviews ──────────────────────────────────────────────────

export async function listRecruiterInterviews(filters = {}) {
  const response = await api.get('/recruiter/interviews', { params: filters });
  return response.data;
}

export async function createRecruiterInterview(payload) {
  const response = await api.post('/recruiter/interviews', payload);
  return response.data;
}

export async function getRecruiterInterview(interviewId) {
  const response = await api.get(`/recruiter/interviews/${interviewId}`);
  return response.data;
}

export async function updateRecruiterInterview(interviewId, payload) {
  const response = await api.put(`/recruiter/interviews/${interviewId}`, payload);
  return response.data;
}

// ─── Applications ─────────────────────────────────────────────────

export async function listRecruiterApplications(filters = {}) {
  const response = await api.get('/recruiter/applications', { params: filters });
  return response.data;
}

export async function updateRecruiterApplication(applicationId, payload) {
  const response = await api.put(`/recruiter/applications/${applicationId}`, payload);
  return response.data;
}

// ─── Shortlist ────────────────────────────────────────────────────

export async function listRecruiterShortlisted() {
  const response = await api.get('/recruiter/shortlisted');
  return response.data;
}

export async function addRecruiterShortlist(payload) {
  const response = await api.post('/recruiter/shortlisted', payload);
  return response.data;
}

export async function removeRecruiterShortlist(shortlistId) {
  const response = await api.delete(`/recruiter/shortlisted/${shortlistId}`);
  return response.data;
}

// ─── Messages ─────────────────────────────────────────────────────

export async function listRecruiterConversations() {
  const response = await api.get('/recruiter/messages/conversations');
  return response.data;
}

export async function sendRecruiterMessage(payload) {
  const response = await api.post('/recruiter/messages', payload);
  return response.data;
}

// ─── Company Profile ─────────────────────────────────────────────

export async function getRecruiterCompanyProfile() {
  const response = await api.get('/recruiter/company');
  return response.data;
}

export async function upsertRecruiterCompanyProfile(payload) {
  const response = await api.put('/recruiter/company', payload);
  return response.data;
}

// ─── Analytics ───────────────────────────────────────────────────

export async function getRecruiterHiringAnalytics() {
  const response = await api.get('/recruiter/analytics/hiring');
  return response.data;
}

// ─── Reports ──────────────────────────────────────────────────────

export async function generateRecruiterReport(reportType) {
  const response = await api.post('/recruiter/reports/generate', null, { params: { report_type: reportType } });
  return response.data;
}

export async function listRecruiterReports() {
  const response = await api.get('/recruiter/reports');
  return response.data;
}

// ─── AI Matching / Ranking ────────────────────────────────────────

export async function rankRecruiterCandidates(limit = 20) {
  const response = await api.get('/recruiter/matching/rankings', { params: { limit } });
  return response.data;
}

export async function getRecruiterAIMatch(candidateId, jobId) {
  const response = await api.get(`/recruiter/matching/match/${candidateId}/${jobId}`);
  return response.data;
}

// ─── Settings ─────────────────────────────────────────────────────

export async function getRecruiterSettings() {
  const response = await api.get('/recruiter/settings');
  return response.data;
}

export async function updateRecruiterSettings(payload) {
  const response = await api.put('/recruiter/settings', payload);
  return response.data;
}

