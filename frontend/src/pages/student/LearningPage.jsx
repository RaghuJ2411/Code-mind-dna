import { useEffect, useState } from 'react';
import DashboardLayout from '../../layouts/DashboardLayout';
import {
  listCourses,
  enrollCourse,
  listEnrollments,
  getCourseProgress,
  listBookmarks,
  createBookmark,
  deleteBookmark,
  listNotes,
  createNote,
  updateNote,
  deleteNote,
  listCertificates,
  getLearningHistory,
} from '../../api/learning';

const TABS = ['Courses', 'My Learning', 'Bookmarks', 'Notes', 'Certificates', 'History'];

export default function LearningPage() {
  const [activeTab, setActiveTab] = useState('Courses');
  const [courses, setCourses] = useState([]);
  const [enrollments, setEnrollments] = useState([]);
  const [bookmarks, setBookmarks] = useState([]);
  const [notes, setNotes] = useState([]);
  const [certificates, setCertificates] = useState([]);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState('');
  const [noteForm, setNoteForm] = useState({ title: '', content: '', tags: [] });
  const [editingNote, setEditingNote] = useState(null);
  const [tagInput, setTagInput] = useState('');

  const loadData = async () => {
    setLoading(true);
    try {
      const [coursesData, enrollmentsData, bookmarksData, notesData, certsData, historyData] = await Promise.all([
        listCourses(),
        listEnrollments(),
        listBookmarks(),
        listNotes(),
        listCertificates(),
        getLearningHistory(),
      ]);
      setCourses(coursesData);
      setEnrollments(enrollmentsData);
      setBookmarks(bookmarksData);
      setNotes(notesData);
      setCertificates(certsData);
      setHistory(historyData.items || []);
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to load learning data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleEnroll = async (courseId) => {
    try {
      await enrollCourse(courseId);
      await loadData();
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to enroll');
    }
  };

  const handleBookmarkToggle = async (resource) => {
    const existing = bookmarks.find((b) => b.resource_type === 'course' && b.resource_id === resource.id);
    if (existing) {
      await deleteBookmark(existing.id);
    } else {
      await createBookmark({ resource_type: 'course', resource_id: resource.id, resource_title: resource.title });
    }
    const refreshed = await listBookmarks();
    setBookmarks(refreshed);
  };

  const handleSaveNote = async (e) => {
    e.preventDefault();
    try {
      if (editingNote) {
        await updateNote(editingNote.id, noteForm);
      } else {
        await createNote(noteForm);
      }
      setNoteForm({ title: '', content: '', tags: [] });
      setEditingNote(null);
      const refreshed = await listNotes();
      setNotes(refreshed);
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to save note');
    }
  };

  const enrolledIds = new Set(enrollments.map((e) => e.course_id));
  const bookmarkIds = new Set(bookmarks.filter((b) => b.resource_type === 'course').map((b) => b.resource_id));
  const filteredCourses = courses.filter((c) => !search || c.title.toLowerCase().includes(search.toLowerCase()));

  return (
    <DashboardLayout title="Learning" role="STUDENT">
      <div className="space-y-6">
        {error && <div className="rounded-[24px] border border-red-200 bg-red-50 p-4 text-sm text-red-600">{error}</div>}

        <section className="panel p-4 sm:p-6">
          <div className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <p className="kicker">Knowledge Hub</p>
              <h2 className="section-title">Learn, grow, and track your progress</h2>
            </div>
          </div>
          <div className="mt-4 flex flex-wrap gap-2">
            {TABS.map((tab) => (
              <button key={tab} onClick={() => setActiveTab(tab)} className={`rounded-full px-4 py-2 text-sm font-medium transition ${activeTab === tab ? 'bg-[var(--brand-primary)] text-white' : 'bg-[var(--surface-elevated)] text-[var(--text-secondary)] hover:bg-[var(--surface-interactive)]'}`}>{tab}</button>
            ))}
          </div>
        </section>

        {activeTab === 'Courses' && (
          <section className="panel p-6">
            <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search courses..." className="mb-4 w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface-elevated)] px-4 py-2.5 text-sm outline-none focus:border-[var(--brand-primary)]" />
            {loading ? (
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {[1, 2, 3].map((i) => <div key={i} className="h-40 animate-pulse rounded-[24px] bg-[var(--surface-elevated)]" />)}
              </div>
            ) : filteredCourses.length === 0 ? (
              <p className="body-copy">No courses available.</p>
            ) : (
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {filteredCourses.map((course) => (
                  <div key={course.id} className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-5 transition hover:shadow-md">
                    <div className="flex items-start justify-between gap-2">
                      <span className="rounded-full bg-[var(--brand-primary)]/10 px-2.5 py-1 text-xs font-medium text-[var(--brand-primary)]">{course.difficulty}</span>
                      <button onClick={() => handleBookmarkToggle(course)} className="text-[var(--text-muted)] hover:text-[var(--brand-primary)]">{bookmarkIds.has(course.id) ? '★' : '☆'}</button>
                    </div>
                    <h3 className="mt-3 font-semibold text-[var(--text-primary)]">{course.title}</h3>
                    <p className="mt-2 text-sm text-[var(--text-secondary)] line-clamp-2">{course.description}</p>
                    <div className="mt-3 flex flex-wrap gap-2">
                      <span className="text-xs text-[var(--text-muted)]">{course.category}</span>
                      {course.duration_hours && <span className="text-xs text-[var(--text-muted)]">{course.duration_hours}h</span>}
                    </div>
                    <button onClick={() => handleEnroll(course.id)} disabled={enrolledIds.has(course.id)} className="mt-4 w-full rounded-2xl bg-[var(--brand-primary)] px-4 py-2 text-sm font-semibold text-white disabled:opacity-50">
                      {enrolledIds.has(course.id) ? 'Enrolled' : 'Enroll'}
                    </button>
                  </div>
                ))}
              </div>
            )}
          </section>
        )}

        {activeTab === 'My Learning' && (
          <section className="panel p-6">
            <h3 className="section-title">Your Enrolled Courses</h3>
            {loading ? (
              <div className="mt-4 space-y-3">{[1, 2].map((i) => <div key={i} className="h-20 animate-pulse rounded-[24px] bg-[var(--surface-elevated)]" />)}</div>
            ) : enrollments.length === 0 ? (
              <p className="mt-4 body-copy">You haven't enrolled in any courses yet. Browse the Courses tab to get started.</p>
            ) : (
              <div className="mt-4 space-y-3">
                {enrollments.map((enrollment) => {
                  const course = courses.find((c) => c.id === enrollment.course_id);
                  return (
                    <div key={enrollment.id} className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-4">
                      <div className="flex items-center justify-between gap-3">
                        <div>
                          <p className="font-semibold text-[var(--text-primary)]">{course?.title || 'Course'}</p>
                          <p className="mt-1 text-sm text-[var(--text-secondary)]">{enrollment.completed ? '✓ Completed' : `${Math.round(enrollment.progress_pct)}% complete`}</p>
                        </div>
                        <div className="h-2 w-32 overflow-hidden rounded-full bg-[var(--surface-interactive)]">
                          <div className="h-full rounded-full bg-[var(--brand-primary)] transition-all" style={{ width: `${enrollment.progress_pct}%` }} />
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </section>
        )}

        {activeTab === 'Bookmarks' && (
          <section className="panel p-6">
            <h3 className="section-title">Bookmarked Resources</h3>
            {loading ? (
              <p className="mt-4 body-copy">Loading...</p>
            ) : bookmarks.length === 0 ? (
              <p className="mt-4 body-copy">No bookmarks yet. Click the star icon on any course to bookmark it.</p>
            ) : (
              <div className="mt-4 space-y-3">
                {bookmarks.map((bookmark) => (
                  <div key={bookmark.id} className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-4">
                    <div className="flex items-center justify-between gap-3">
                      <div>
                        <p className="font-semibold text-[var(--text-primary)]">{bookmark.resource_title || `${bookmark.resource_type} #${bookmark.resource_id}`}</p>
                        <p className="mt-1 text-sm text-[var(--text-muted)]">{bookmark.resource_type}</p>
                      </div>
                      <button onClick={() => handleBookmarkToggle({ id: bookmark.resource_id })} className="text-rose-500 hover:text-rose-600">Remove</button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>
        )}

        {activeTab === 'Notes' && (
          <section className="panel p-6">
            <h3 className="section-title">Your Notes</h3>
            <form onSubmit={handleSaveNote} className="mt-4 space-y-3 rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-4">
              <input value={noteForm.title} onChange={(e) => setNoteForm({ ...noteForm, title: e.target.value })} placeholder="Note title" className="w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] px-4 py-2.5 text-sm outline-none focus:border-[var(--brand-primary)]" required />
              <textarea value={noteForm.content} onChange={(e) => setNoteForm({ ...noteForm, content: e.target.value })} placeholder="Write your notes..." rows={3} className="w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] px-4 py-2.5 text-sm outline-none focus:border-[var(--brand-primary)]" required />
              <div className="flex gap-2">
                <input value={tagInput} onChange={(e) => setTagInput(e.target.value)} placeholder="Add tag" className="flex-1 rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] px-4 py-2 text-sm outline-none focus:border-[var(--brand-primary)]" />
                <button type="button" onClick={() => { if (tagInput.trim()) { setNoteForm({ ...noteForm, tags: [...noteForm.tags, tagInput.trim()] }); setTagInput(''); } }} className="rounded-2xl bg-[var(--brand-primary)] px-4 py-2 text-sm text-white">Add</button>
              </div>
              {noteForm.tags.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {noteForm.tags.map((tag) => (
                    <span key={tag} className="rounded-full bg-[var(--brand-primary)]/10 px-3 py-1 text-xs text-[var(--brand-primary)]">{tag}</span>
                  ))}
                </div>
              )}
              <button type="submit" className="rounded-2xl bg-[var(--brand-primary)] px-6 py-2.5 text-sm font-semibold text-white">{editingNote ? 'Update Note' : 'Save Note'}</button>
            </form>
            <div className="mt-4 space-y-3">
              {notes.map((note) => (
                <div key={note.id} className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-4">
                  <div className="flex items-center justify-between gap-3">
                    <p className="font-semibold text-[var(--text-primary)]">{note.title}</p>
                    <div className="flex gap-2">
                      <button onClick={() => { setEditingNote(note); setNoteForm({ title: note.title, content: note.content, tags: note.tags }); }} className="text-sm text-[var(--brand-primary)]">Edit</button>
                      <button onClick={async () => { await deleteNote(note.id); const refreshed = await listNotes(); setNotes(refreshed); }} className="text-sm text-rose-500">Delete</button>
                    </div>
                  </div>
                  <p className="mt-2 text-sm text-[var(--text-secondary)]">{note.content}</p>
                  {note.tags?.length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-1">
                      {note.tags.map((tag) => <span key={tag} className="rounded-full bg-[var(--surface-interactive)] px-2 py-0.5 text-xs text-[var(--text-muted)]">{tag}</span>)}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </section>
        )}

        {activeTab === 'Certificates' && (
          <section className="panel p-6">
            <h3 className="section-title">Your Certificates</h3>
            {loading ? (
              <p className="mt-4 body-copy">Loading...</p>
            ) : certificates.length === 0 ? (
              <p className="mt-4 body-copy">Complete a course to earn a certificate.</p>
            ) : (
              <div className="mt-4 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {certificates.map((cert) => (
                  <div key={cert.id} className="rounded-[24px] border border-emerald-200 bg-gradient-to-br from-emerald-50 to-white p-5 text-center">
                    <p className="text-2xl">🎓</p>
                    <p className="mt-2 font-semibold text-emerald-800">Certificate of Completion</p>
                    <p className="mt-2 text-sm text-emerald-600">Issued: {new Date(cert.issued_at).toLocaleDateString()}</p>
                    {cert.is_verified && <span className="mt-2 inline-block rounded-full bg-emerald-100 px-3 py-1 text-xs text-emerald-700">✓ Verified</span>}
                  </div>
                ))}
              </div>
            )}
          </section>
        )}

        {activeTab === 'History' && (
          <section className="panel p-6">
            <h3 className="section-title">Learning History</h3>
            {loading ? (
              <p className="mt-4 body-copy">Loading...</p>
            ) : history.length === 0 ? (
              <p className="mt-4 body-copy">No learning history yet.</p>
            ) : (
              <div className="mt-4 space-y-2">
                {history.map((item, i) => (
                  <div key={i} className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-3 text-sm">
                    <div className="flex items-center justify-between gap-3">
                      <span className="font-medium text-[var(--text-primary)]">{item.course_title}</span>
                      <span className="text-[var(--text-muted)]">{item.action}</span>
                    </div>
                    <p className="mt-1 text-xs text-[var(--text-muted)]">{new Date(item.timestamp).toLocaleDateString()}</p>
                  </div>
                ))}
              </div>
            )}
          </section>
        )}
      </div>
    </DashboardLayout>
  );
}

