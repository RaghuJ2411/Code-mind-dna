import api from './client';

export async function listMentorCareerRoles() {
  const response = await api.get('/mentor/career-reviews/roles');
  return response.data;
}

export async function createMentorCareerReview(payload) {
  const response = await api.post('/mentor/career-reviews', payload);
  return response.data;
}

export async function listMentorCareerReviews() {
  const response = await api.get('/mentor/career-reviews');
  return response.data;
}
