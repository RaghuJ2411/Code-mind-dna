import api from './client';

export async function listCourses(category, difficulty, search) {
  const params = {};
  if (category) params.category = category;
  if (difficulty) params.difficulty = difficulty;
  if (search) params.search = search;
  const response = await api.get('/student/learning/courses', { params });
  return response.data;
}

export async function getCourse(courseId) {
  const response = await api.get(`/student/learning/courses/${courseId}`);
  return response.data;
}

export async function enrollCourse(courseId) {
  const response = await api.post(`/student/learning/enroll/${courseId}`);
  return response.data;
}

export async function listEnrollments() {
  const response = await api.get('/student/learning/enrollments');
  return response.data;
}

export async function getCourseProgress(courseId) {
  const response = await api.get(`/student/learning/progress/${courseId}`);
  return response.data;
}

export async function updateCourseProgress(courseId, moduleId, completedSections, currentSection) {
  const params = { completed_sections: completedSections };
  if (currentSection) params.current_section = currentSection;
  const response = await api.put(`/student/learning/progress/${courseId}/${moduleId}`, null, { params });
  return response.data;
}

export async function listBookmarks(resourceType) {
  const params = {};
  if (resourceType) params.resource_type = resourceType;
  const response = await api.get('/student/learning/bookmarks', { params });
  return response.data;
}

export async function createBookmark(payload) {
  const response = await api.post('/student/learning/bookmarks', payload);
  return response.data;
}

export async function deleteBookmark(bookmarkId) {
  await api.delete(`/student/learning/bookmarks/${bookmarkId}`);
}

export async function listNotes(resourceType) {
  const params = {};
  if (resourceType) params.resource_type = resourceType;
  const response = await api.get('/student/learning/notes', { params });
  return response.data;
}

export async function createNote(payload) {
  const response = await api.post('/student/learning/notes', payload);
  return response.data;
}

export async function updateNote(noteId, payload) {
  const response = await api.put(`/student/learning/notes/${noteId}`, payload);
  return response.data;
}

export async function deleteNote(noteId) {
  await api.delete(`/student/learning/notes/${noteId}`);
}

export async function listCertificates() {
  const response = await api.get('/student/learning/certificates');
  return response.data;
}

export async function getLearningHistory() {
  const response = await api.get('/student/learning/history');
  return response.data;
}

