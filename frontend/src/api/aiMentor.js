import api from './client';

export async function chatWithMentor(message, conversationId) {
  const response = await api.post('/student/ai-mentor/chat', { message, conversation_id: conversationId });
  return response.data;
}

export async function getChatHistory() {
  const response = await api.get('/student/ai-mentor/history');
  return response.data;
}

export async function generateInterviewQuestions(roleName, questionCount = 5) {
  const response = await api.post('/student/ai-mentor/interview-questions', { role_name: roleName, question_count: questionCount });
  return response.data;
}

export async function reviewResume(resumeContent, targetRole) {
  const response = await api.post('/student/ai-mentor/resume-review', { resume_content: resumeContent, target_role: targetRole });
  return response.data;
}

export async function explainCode(code, language, context) {
  const response = await api.post('/student/ai-mentor/code-explanation', { code, language, context });
  return response.data;
}

export async function fixBug(code, errorMessage, language) {
  const response = await api.post('/student/ai-mentor/bug-fix', { code, error_message: errorMessage, language });
  return response.data;
}

