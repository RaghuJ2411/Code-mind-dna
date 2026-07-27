import api from './client';

// ─── Dashboard ───────────────────────────────────────────────────

export async function getAdminDashboard() {
  const response = await api.get('/admin/dashboard');
  return response.data;
}

// ─── Users ───────────────────────────────────────────────────────

export async function listAdminUsers(params = {}) {
  const response = await api.get('/admin/users', { params });
  return response.data;
}

export async function updateAdminUser(userId, data) {
  const response = await api.put(`/admin/users/${userId}`, data);
  return response.data;
}

// ─── Audit Logs ──────────────────────────────────────────────────

export async function listAuditLogs(params = {}) {
  const response = await api.get('/admin/audit-logs', { params });
  return response.data;
}

// ─── System Monitoring ──────────────────────────────────────────

export async function getSystemOverview() {
  const response = await api.get('/admin/system/overview');
  return response.data;
}

export async function getSystemServices() {
  const response = await api.get('/admin/system/services');
  return response.data;
}

export async function getSystemLogs(params = {}) {
  const response = await api.get('/admin/system/logs', { params });
  return response.data;
}

// ─── Platform Analytics ─────────────────────────────────────────

export async function getPlatformAnalyticsOverview() {
  const response = await api.get('/admin/analytics/overview');
  return response.data;
}

export async function getPlatformEngagement(params = {}) {
  const response = await api.get('/admin/analytics/engagement', { params });
  return response.data;
}

export async function getPlatformUsage() {
  const response = await api.get('/admin/analytics/usage');
  return response.data;
}

// ─── Database Health ────────────────────────────────────────────

export async function getDatabaseHealth() {
  const response = await api.get('/admin/database/health');
  return response.data;
}

export async function getDatabaseTables() {
  const response = await api.get('/admin/database/tables');
  return response.data;
}

// ─── AI Monitoring ──────────────────────────────────────────────

export async function getAIUsageOverview() {
  const response = await api.get('/admin/ai/usage');
  return response.data;
}

export async function listAIRequests(params = {}) {
  const response = await api.get('/admin/ai/requests', { params });
  return response.data;
}

export async function getAILimits() {
  const response = await api.get('/admin/ai/limits');
  return response.data;
}

export async function updateAILimits(data) {
  const response = await api.put('/admin/ai/limits', data);
  return response.data;
}

// ─── Reports ────────────────────────────────────────────────────

export async function listAdminReports() {
  const response = await api.get('/admin/reports');
  return response.data;
}

export async function generateAdminReport(data) {
  const response = await api.post('/admin/reports/generate', data);
  return response.data;
}

export async function getAdminReport(reportId) {
  const response = await api.get(`/admin/reports/${reportId}`);
  return response.data;
}

// ─── Settings ───────────────────────────────────────────────────

export async function getAdminSettings() {
  const response = await api.get('/admin/settings');
  return response.data;
}

export async function updateAdminSettings(data) {
  const response = await api.put('/admin/settings', data);
  return response.data;
}

// ─── Permissions ────────────────────────────────────────────────

export async function listPermissions() {
  const response = await api.get('/admin/permissions');
  return response.data;
}

export async function getRolePermissions(role) {
  const response = await api.get(`/admin/permissions/roles/${role}`);
  return response.data;
}

export async function updateRolePermissions(role, data) {
  const response = await api.put(`/admin/permissions/roles/${role}`, data);
  return response.data;
}

