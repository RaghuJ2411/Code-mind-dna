import api from './client';

export async function listConversations(conversationType) {
  const params = {};
  if (conversationType) params.conversation_type = conversationType;
  const response = await api.get('/student/messages/conversations', { params });
  return response.data;
}

export async function getConversation(conversationId) {
  const response = await api.get(`/student/messages/conversations/${conversationId}`);
  return response.data;
}

export async function sendMessage(conversationId, payload) {
  const response = await api.post(`/student/messages/conversations/${conversationId}/send`, payload);
  return response.data;
}

export async function getUnreadCount() {
  const response = await api.get('/student/messages/unread-count');
  return response.data;
}

