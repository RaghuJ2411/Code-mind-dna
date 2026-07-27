import api from './client';

// Existing alert functions
export async function listMentorAlerts() {
  const response = await api.get('/mentor/alerts');
  return response.data;
}

export async function createMentorAlert(payload) {
  const response = await api.post('/mentor/alerts', payload);
  return response.data;
}

export async function generateMentorAlerts(studentId = null) {
  const params = studentId ? `?student_id=${studentId}` : '';
  const response = await api.post(`/mentor/alerts/generate${params}`);
  return response.data;
}

export async function acknowledgeMentorAlert(alertId) {
  const response = await api.post(`/mentor/alerts/${alertId}/acknowledge`);
  return response.data;
}

export async function resolveMentorAlert(alertId) {
  const response = await api.post(`/mentor/alerts/${alertId}/resolve`);
  return response.data;
}

export async function listMentorStudents() {
  const response = await api.get('/mentor/students');
  return response.data;
}

// Sessions
export async function listMentorSessions(filters = {}) {
  const response = await api.get('/mentor/sessions', { params: filters });
  return response.data;
}

export async function createMentorSession(payload) {
  const response = await api.post('/mentor/sessions', payload);
  return response.data;
}

export async function getMentorSession(sessionId) {
  const response = await api.get(`/mentor/sessions/${sessionId}`);
  return response.data;
}

export async function updateMentorSession(sessionId, payload) {
  const response = await api.put(`/mentor/sessions/${sessionId}`, payload);
  return response.data;
}

// Assignments
export async function listMentorAssignments(filters = {}) {
  const response = await api.get('/mentor/assignments', { params: filters });
  return response.data;
}

export async function createMentorAssignment(payload) {
  const response = await api.post('/mentor/assignments', payload);
  return response.data;
}

export async function getMentorAssignment(assignmentId) {
  const response = await api.get(`/mentor/assignments/${assignmentId}`);
  return response.data;
}

// Resources
export async function listMentorResources(filters = {}) {
  const response = await api.get('/mentor/resources', { params: filters });
  return response.data;
}

export async function createMentorResource(payload) {
  const response = await api.post('/mentor/resources', payload);
  return response.data;
}

export async function deleteMentorResource(resourceId) {
  await api.delete(`/mentor/resources/${resourceId}`);
}

// Notifications
export async function listMentorNotifications(filters = {}) {
  const response = await api.get('/mentor/notifications', { params: filters });
  return response.data;
}

export async function createMentorNotification(payload) {
  const response = await api.post('/mentor/notifications', payload);
  return response.data;
}

export async function getMentorUnreadCount() {
  const response = await api.get('/mentor/notifications/unread-count');
  return response.data;
}

export async function markNotificationRead(notificationId) {
  const response = await api.post(`/mentor/notifications/${notificationId}/read`);
  return response.data;
}

export async function markAllNotificationsRead() {
  const response = await api.post('/mentor/notifications/read-all');
  return response.data;
}

// Analytics
export async function getMentorAnalyticsOverview(days = 30) {
  const response = await api.get('/mentor/analytics/overview', { params: { days } });
  return response.data;
}

export async function getMentorStudentAnalytics(studentId) {
  const response = await api.get(`/mentor/analytics/student/${studentId}`);
  return response.data;
}

// Reports
export async function generateStudentProgressReport(studentId = null, days = 30) {
  const params = { days };
  if (studentId) params.student_id = studentId;
  const response = await api.get('/mentor/reports/student-progress', { params });
  return response.data;
}

export async function generateAlertsSummaryReport(days = 30) {
  const response = await api.get('/mentor/reports/alerts-summary', { params: { days } });
  return response.data;
}

export async function generateEngagementReport(days = 30) {
  const response = await api.get('/mentor/reports/engagement', { params: { days } });
  return response.data;
}

// Intelligence
export async function listStudentIntelligence() {
  const response = await api.get('/mentor/intelligence/students');
  return response.data;
}

export async function getStudentIntelligence(studentId) {
  const response = await api.get(`/mentor/intelligence/${studentId}`);
  return response.data;
}

// Messages
export async function listMentorConversations(filters = {}) {
  const response = await api.get('/mentor/messages/conversations', { params: filters });
  return response.data;
}

export async function getMentorConversation(conversationId) {
  const response = await api.get(`/mentor/messages/conversations/${conversationId}`);
  return response.data;
}

export async function sendMentorMessage(conversationId, payload) {
  const response = await api.post(`/mentor/messages/conversations/${conversationId}/send`, payload);
  return response.data;
}

export async function getMentorUnreadMessageCount() {
  const response = await api.get('/mentor/messages/unread-count');
  return response.data;
}

// Profile
export async function getMentorProfile() {
  const response = await api.get('/mentor/profile');
  return response.data;
}

export async function updateMentorProfile(payload) {
  const response = await api.put('/mentor/profile', payload);
  return response.data;
}

export async function uploadMentorPhoto(file) {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post('/mentor/profile/photo', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
}

// Assessments (view student assessments)
export async function listMentorStudentAssessments(studentId) {
  const response = await api.get('/student/assessments', { params: { student_id: studentId } });
  return response.data;
}

export async function getMentorStudentAssessmentHistory(studentId) {
  const response = await api.get('/student/assessments/results/history', { params: { student_id: studentId } });
  return response.data;
}

