import { useEffect, useState } from 'react';
import DashboardLayout from '../../layouts/DashboardLayout';
import { listMentorAssignments, createMentorAssignment, listMentorStudents } from '../../api/mentor';

export default function MentorAssignmentsPage() {
  const [assignments, setAssignments] = useState([]);
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ title: '', description: '', assignment_type: 'CODING', student_ids: [], due_date: '', max_score: 100, passing_score: 60 });

  const load = async () => {
    setLoading(true);
    try {
      const [assignData, studentData] = await Promise.all([listMentorAssignments(), listMentorStudents()]);
      setAssignments(assignData || []);
      setStudents(studentData || []);
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to load assignments');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      await createMentorAssignment(form);
      setShowForm(false);
      setForm({ title: '', description: '', assignment_type: 'CODING', student_ids: [], due_date: '', max_score: 100, passing_score: 60 });
      await load();
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to create assignment');
    }
  };

  return (
    <DashboardLayout title="Assignments" role="MENTOR">
      <div className="space-y-6">
        {error && <div className="rounded-[24px] border border-red-200 bg-red-50 p-4 text-sm text-red-600">{error}</div>}

        <section className="panel p-6">
          <div className="flex items-center justify-between gap-3">
            <div>
              <p className="kicker">Assignments</p>
              <h2 className="section-title">Manage Assignments</h2>
              <p className="mt-1 body-copy">Create and track student assignments, projects, and quizzes.</p>
            </div>
            <button onClick={() => setShowForm(!showForm)} className="btn-primary">{showForm ? 'Cancel' : 'New Assignment'}</button>
          </div>

          {showForm && (
            <form onSubmit={handleCreate} className="mt-6 space-y-4 rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-6">
              <div className="grid gap-4 md:grid-cols-2">
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-[var(--text-secondary)]">Title *</label>
                  <input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} className="mt-1 w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] px-4 py-2.5 text-sm outline-none" required />
                </div>
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-[var(--text-secondary)]">Description</label>
                  <textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} rows={3} className="mt-1 w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] px-4 py-2.5 text-sm outline-none" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-[var(--text-secondary)]">Type</label>
                  <select value={form.assignment_type} onChange={(e) => setForm({ ...form, assignment_type: e.target.value })} className="mt-1 w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] px-4 py-2.5 text-sm outline-none">
                    <option value="CODING">Coding</option>
                    <option value="READING">Reading</option>
                    <option value="PROJECT">Project</option>
                    <option value="QUIZ">Quiz</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-[var(--text-secondary)]">Due Date</label>
                  <input type="date" value={form.due_date} onChange={(e) => setForm({ ...form, due_date: e.target.value })} className="mt-1 w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] px-4 py-2.5 text-sm outline-none" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-[var(--text-secondary)]">Max Score</label>
                  <input type="number" value={form.max_score} onChange={(e) => setForm({ ...form, max_score: parseInt(e.target.value) || 100 })} className="mt-1 w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] px-4 py-2.5 text-sm outline-none" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-[var(--text-secondary)]">Passing Score</label>
                  <input type="number" value={form.passing_score} onChange={(e) => setForm({ ...form, passing_score: parseInt(e.target.value) || 60 })} className="mt-1 w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] px-4 py-2.5 text-sm outline-none" />
                </div>
              </div>
              <button type="submit" className="btn-primary">Create Assignment</button>
            </form>
          )}

          {loading ? (
            <div className="mt-4 space-y-3">{[1, 2].map((i) => <div key={i} className="h-20 animate-pulse rounded-[24px] bg-[var(--surface-elevated)]" />)}</div>
          ) : assignments.length === 0 ? (
            <div className="mt-6 rounded-[24px] border border-dashed border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-6 text-center text-sm text-[var(--text-secondary)]">No assignments created yet.</div>
          ) : (
            <div className="mt-4 space-y-3">
              {assignments.map((a) => (
                <div key={a.id} className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-4">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <div className="flex items-center gap-2">
                        <p className="font-semibold text-[var(--text-primary)]">{a.title}</p>
                        <span className="rounded-full bg-[var(--surface-interactive)] px-2.5 py-0.5 text-xs text-[var(--text-muted)]">{a.assignment_type}</span>
                      </div>
                      {a.description && <p className="mt-1 text-sm text-[var(--text-secondary)]">{a.description}</p>}
                      <div className="mt-2 flex flex-wrap gap-2 text-xs text-[var(--text-muted)]">
                        <span>Max: {a.max_score}</span>
                        <span>Pass: {a.passing_score}</span>
                        <span>{a.is_active ? 'Active' : 'Inactive'}</span>
                      </div>
                    </div>
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

