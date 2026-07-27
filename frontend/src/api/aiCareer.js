import api from './client';

/**
 * AI Career Intelligence API Client
 * All endpoints are daily-rate-limited and use the AI provider (Mock/OpenAI).
 */

export async function analyzeSkillGap(roleId, includeRecommendations = true) {
  const response = await api.post('/student/ai-career/skill-gap', {
    role_id: roleId,
    include_recommendations: includeRecommendations,
  });
  return response.data;
}

export async function predictCareerPaths(includeAlternativePaths = true) {
  const response = await api.post('/student/ai-career/career-prediction', {
    include_alternative_paths: includeAlternativePaths,
  });
  return response.data;
}

export async function parseResume(resumeContent, targetRole = null) {
  const response = await api.post('/student/ai-career/parse-resume', {
    resume_content: resumeContent,
    target_role: targetRole,
  });
  return response.data;
}

export async function getInterviewFeedback(question, answer, roleName = null, seniorityLevel = null) {
  const response = await api.post('/student/ai-career/interview-feedback', {
    question,
    answer,
    role_name: roleName,
    seniority_level: seniorityLevel,
  });
  return response.data;
}

