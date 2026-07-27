import { useEffect, useState } from 'react';
import DashboardLayout from '../../layouts/DashboardLayout';
import { listMentorStudents } from '../../api/mentor';

export default function MentorStudentsPage() {
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState('');

  useEffect(() => {
    const load = async () => {
      try {
        const data = await listMentorStudents();
        setStudents(data || []);
      } catch (err) {
        setError(err?.response?.data?.detail || 'Failed to load students');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const filtered = students.filter((s) =>
    !search || s.full_name?.toLowerCase().includes(search.toLowerCase()) ||
    s.email?.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <DashboardLayout title="Students" role="MENTOR">
      <div className="space-y-6">
        {error && <div className="rounded-[24px] border border-red-200 bg-red-50 p-4 text-sm text-red-600">{error}</div>}

        <section className="panel p-6">
          <div className="flex items-center justify-between gap-3">
            <div>
              <p className="kicker">Student Roster</p>
              <h2 className="section-title">Your Students</h2>
              <p className="mt-1 body-copy">View and manage all students assigned to you.</p>
            </div>
            <span className="metric-pill">{students.length} total</span>
          </div>
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search students by name or email..."
            className="mt-4 w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface-elevated)] px-4 py-2.5 text-sm outline-none focus:border-[var(--brand-primary)]"
          />
          {loading ? (
            <div className="mt-4 space-y-3">{[1, 2, 3].map((i) => <div key={i} className="h-16 animate-pulse rounded-[24px] bg-[var(--surface-elevated)]" />)}</div>
          ) : filtered.length === 0 ? (
            <div className="mt-6 rounded-[24px] border border-dashed border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-6 text-center text-sm text-[var(--text-secondary)]">No students found.</div>
          ) : (
            <div className="mt-4 space-y-3">
              {filtered.map((student) => (
                <div key={student.id} className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-4">
                  <div className="flex items-center justify-between gap-3">
                    <div className="flex items-center gap-3">
                      <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[var(--brand-primary)]/10 text-sm font-bold text-[var(--brand-primary)]">
                        {student.full_name?.charAt(0) || '?'}
                      </div>
                      <div>
                        <p className="font-semibold text-[var(--text-primary)]">{student.full_name}</p>
                        <p className="text-sm text-[var(--text-muted)]">{student.email}</p>
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

