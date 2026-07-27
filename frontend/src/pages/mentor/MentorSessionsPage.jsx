import { useEffect, useState } from 'react';
import DashboardLayout from '../../layouts/DashboardLayout';
import { listMentorSessions, createMentorSession, updateMentorSession, listMentorStudents } from '../../api/mentor';

export default function MentorSessionsPage() {
  const [sessions, setSessions] = useState([]);
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ title: '', description: '', session_type: 'ONE_ON_ONE', student_ids: [], scheduled_at: '', duration_minutes: 60, meeting_link: '' });
  const [selectedStudent, setSelectedStudent] = useState('');

  const load = async () => {
    setLoading(true);
    try {
      const [sessionData, studentData] = await Promise.all([listMentorSessions(), listMentorStudents()]);
      setSessions(sessionData || []);
      setStudents(studentData || []);
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to load sessions');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      await createMentorSession({
        ...form,
        student_ids: selectedStudent ? [parseInt(selectedStudent)] : [],
        scheduled_at: form.scheduled_at ? new Date(form.scheduled_at).toISOString() : new Date().toISOString(),
      });
      setShowForm(false);
      setForm({ title: '', description: '', session_type: 'ONE_ON_ONE', student_ids: [], scheduled_at: '', duration_minutes: 60, meeting_link: '' });
      setSelectedStudent('');
      await load();
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to create session');
    }
  };

  const handleComplete = async (sessionId) => {
    try {
      await updateMentorSession(sessionId, { status: 'COMPLETED' });
      await load();
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to update session');
    }
  };

  return (
    <DashboardLayout title="Sessions" role="MENTOR">
      <div className="space-y-6">
        {error && <div className="rounded-[24px] border border-red-200 bg-red-50 p-4 text-sm text-red-600">{error}</div>}

        <section className="panel p-6">
          <div className="flex items-center justify-between gap-3">
            <div>
              <p className="kicker">Mentoring Sessions</p>
              <h2 className="section-title">Schedule & Manage Sessions</h2>
              <p className="mt-1 body-copy">Plan and track your one-on-one and group mentoring sessions.</p>
            </div>
            <button onClick={() => setShowForm(!showForm)} className="btn-primary">{showForm ? 'Cancel' : 'New Session'}</button>
          </div>

          {showForm && (
            <form onSubmit={handleCreate} className="mt-6 grid gap-4 rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-6 md:grid-cols-2">
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-[var(--text-secondary)]">Title *</label>
                <input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} className="mt-1 w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] px-4 py-2.5 text-sm outline-none" required />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-[var(--text-secondary)]">Description</label>
                <textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} rows={3} className="mt-1 w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] px-4 py-2.5 text-sm outline-none" />
              </div>
              <div>
                <label className="block text-sm font-medium text-[var(--text-secondary)]">Student</label>
                <select value={selectedStudent} onChange={(e) => setSelectedStudent(e.target.value)} className="mt-1 w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] px-4 py-2.5 text-sm outline-none">
                  <option value="">Select Student</option>
                  {students.map((s) => <option key={s.id} value={s.id}>{s.full_name}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-[var(--text-secondary)]">Type</label>
                <select value={form.session_type} onChange={(e) => setForm({ ...form, session_type: e.target.value })} className="mt-1 w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] px-4 py-2.5 text-sm outline-none">
                  <option value="ONE_ON_ONE">One on One</option>
                  <option value="GROUP">Group</option>
                  <option value="WORKSHOP">Workshop</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-[var(--text-secondary)]">Date & Time</label>
                <input type="datetime-local" value={form.scheduled_at} onChange={(e) => setForm({ ...form, scheduled_at: e.target.value })} className="mt-1 w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] px-4 py-2.5 text-sm outline-none" />
              </div>
              <div>
                <label className="block text-sm font-medium text-[var(--text-secondary)]">Duration (min)</label>
                <input type="number" value={form.duration_minutes} onChange={(e) => setForm({ ...form, duration_minutes: parseInt(e.target.value) || 60 })} className="mt-1 w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] px-4 py-2.5 text-sm outline-none" />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-[var(--text-secondary)]">Meeting Link</label>
                <input value={form.meeting_link} onChange={(e) => setForm({ ...form, meeting_link: e.target.value })} className="mt-1 w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] px-4 py-2.5 text-sm outline-none" />
              </div>
              <div className="md:col-span-2">
                <button type="submit" className="btn-primary">Schedule Session</button>
              </div>
            </form>
          )}

          {loading ? (
            <div className="mt-4 space-y-3">{[1, 2].map((i) => <div key={i} className="h-20 animate-pulse rounded-[24px] bg-[var(--surface-elevated)]" />)}</div>
          ) : sessions.length === 0 ? (
            <div className="mt-6 rounded-[24px] border border-dashed border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-6 text-center text-sm text-[var(--text-secondary)]">No sessions scheduled.</div>
          ) : (
            <div className="mt-4 space-y-3">
              {sessions.map((session) => (
                <div key={session.id} className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-4">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-semibold text-[var(--text-primary)]">{session.title}</span>
                        <span className={`rounded-full px-2.5 py-0.5 text-xs ${
                          session.status === 'SCHEDULED' ? 'bg-blue-100 text-blue-700' : 'bg-emerald-100 text-emerald-700'
                        }`}>{session.status}</span>
                      </div>
                      {session.description && <p className="mt-1 text-sm text-[var(--text-secondary)]">{session.description}</p>}
                      <div className="mt-2 flex flex-wrap gap-2 text-xs text-[var(--text-muted)]">
                        <span>{session.session_type}</span>
                        <span>{session.duration_minutes} min</span>
                        <span>Scheduled: {new Date(session.scheduled_at).toLocaleString()}</span>
                      </div>
                    </div>
                    {session.status === 'SCHEDULED' && (
                      <button onClick={() => handleComplete(session.id)} className="rounded-2xl bg-emerald-600 px-3 py-1.5 text-xs text-white">Complete</button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>
    </DashboardLayout>
  );
}

