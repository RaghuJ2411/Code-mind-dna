import { useEffect, useState } from 'react';
import DashboardLayout from '../../layouts/DashboardLayout';
import { listStudentIntelligence } from '../../api/mentor';

export default function MentorIntelligencePage() {
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const load = async () => {
      try {
        const data = await listStudentIntelligence();
        setStudents(data || []);
      } catch (err) {
        setError(err?.response?.data?.detail || 'Failed to load intelligence');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  return (
    <DashboardLayout title="Student Intelligence" role="MENTOR">
      <div className="space-y-6">
        {error && <div className="rounded-[24px] border border-red-200 bg-red-50 p-4 text-sm text-red-600">{error}</div>}

        <section className="panel p-6">
          <p className="kicker">Intelligence Dashboard</p>
          <h2 className="section-title">Student Insights & Analytics</h2>
          <p className="mt-2 body-copy">AI-powered insights into each student's performance, engagement, and risk factors.</p>

          {loading ? (
            <div className="mt-6 space-y-4">{[1, 2, 3].map((i) => <div key={i} className="h-24 animate-pulse rounded-[24px] bg-[var(--surface-elevated)]" />)}</div>
          ) : students.length === 0 ? (
            <div className="mt-6 rounded-[24px] border border-dashed border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-6 text-center text-sm text-[var(--text-secondary)]">No student data available.</div>
          ) : (
            <div className="mt-6 space-y-4">
              {students.map((s) => (
                <div key={s.student_id} className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-5">
                  <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3">
                        <p className="text-lg font-semibold text-[var(--text-primary)]">{s.student_name}</p>
                        <span className={`rounded-full px-3 py-1 text-xs font-semibold ${
                          s.engagement_level === 'HIGH' ? 'bg-emerald-100 text-emerald-700' :
                          s.engagement_level === 'MODERATE' ? 'bg-amber-100 text-amber-700' :
                          'bg-red-100 text-red-700'
                        }`}>{s.engagement_level}</span>
                      </div>
                      <div className="mt-3 grid gap-3 md:grid-cols-4">
                        <div className="rounded-2xl bg-[var(--surface)] p-3">
                          <p className="text-xs text-[var(--text-muted)]">DNA Score</p>
                          <p className="mt-1 text-lg font-semibold">{s.coding_dna_score?.toFixed(1) || 'N/A'}</p>
                        </div>
                        <div className="rounded-2xl bg-[var(--surface)] p-3">
                          <p className="text-xs text-[var(--text-muted)]">Solve Rate</p>
                          <p className="mt-1 text-lg font-semibold">{s.solve_rate?.toFixed(1)}%</p>
                        </div>
                        <div className="rounded-2xl bg-[var(--surface)] p-3">
                          <p className="text-xs text-[var(--text-muted)]">Risk Score</p>
                          <p className={`mt-1 text-lg font-semibold ${s.risk_score > 50 ? 'text-red-600' : 'text-emerald-600'}`}>{s.risk_score?.toFixed(0) || 0}</p>
                        </div>
                        <div className="rounded-2xl bg-[var(--surface)] p-3">
                          <p className="text-xs text-[var(--text-muted)]">Last Active</p>
                          <p className="mt-1 text-sm font-semibold">{s.last_active ? new Date(s.last_active).toLocaleDateString() : 'Never'}</p>
                        </div>
                      </div>
                      {s.weak_topics?.length > 0 && (
                        <div className="mt-3">
                          <p className="text-xs font-semibold text-amber-600">Weak Topics:</p>
                          <div className="mt-1 flex flex-wrap gap-1">
                            {s.weak_topics.map((t) => <span key={t} className="rounded-full bg-red-50 px-2.5 py-1 text-xs text-red-700">{t}</span>)}
                          </div>
                        </div>
                      )}
                      {s.strong_topics?.length > 0 && (
                        <div className="mt-2">
                          <p className="text-xs font-semibold text-emerald-600">Strong Topics:</p>
                          <div className="mt-1 flex flex-wrap gap-1">
                            {s.strong_topics.map((t) => <span key={t} className="rounded-full bg-emerald-50 px-2.5 py-1 text-xs text-emerald-700">{t}</span>)}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                  {s.recommended_actions?.length > 0 && (
                    <div className="mt-4 rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] p-3">
                      <p className="text-xs font-semibold text-[var(--text-primary)]">Recommended Actions</p>
                      <ul className="mt-2 list-disc space-y-1 pl-4 text-sm text-[var(--text-secondary)]">
                        {s.recommended_actions.map((a, i) => <li key={i}>{a}</li>)}
                      </ul>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </section>
      </div>
    </DashboardLayout>
  );
}

