import { useEffect, useState } from 'react';
import DashboardLayout from '../../layouts/DashboardLayout';
import { getMentorAnalyticsOverview } from '../../api/mentor';

export default function MentorAnalyticsPage() {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const load = async () => {
      try {
        const data = await getMentorAnalyticsOverview();
        setAnalytics(data);
      } catch (err) {
        setError(err?.response?.data?.detail || 'Failed to load analytics');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  if (loading) {
    return (
      <DashboardLayout title="Analytics" role="MENTOR">
        <div className="grid gap-4 md:grid-cols-4">{[1, 2, 3, 4].map((i) => <div key={i} className="h-24 animate-pulse rounded-[24px] bg-[var(--surface-elevated)]" />)}</div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout title="Performance Analytics" role="MENTOR">
      <div className="space-y-6">
        {error && <div className="rounded-[24px] border border-red-200 bg-red-50 p-4 text-sm text-red-600">{error}</div>}

        <section className="panel p-6">
          <p className="kicker">Analytics Overview</p>
          <h2 className="section-title">Mentor Performance Dashboard</h2>
          <p className="mt-2 body-copy">Track student performance, engagement, and intervention effectiveness.</p>

          <div className="mt-6 grid gap-4 md:grid-cols-4">
            <div className="panel-soft p-4">
              <p className="text-sm text-[var(--text-muted)]">Total Students</p>
              <p className="mt-2 text-2xl font-semibold">{analytics?.total_students || 0}</p>
              <p className="mt-1 text-xs text-[var(--text-secondary)]">{analytics?.active_students || 0} active</p>
            </div>
            <div className="panel-soft p-4">
              <p className="text-sm text-[var(--text-muted)]">Avg Solve Rate</p>
              <p className="mt-2 text-2xl font-semibold">{analytics?.avg_solve_rate?.toFixed(1) || 0}%</p>
            </div>
            <div className="panel-soft p-4">
              <p className="text-sm text-[var(--text-muted)]">Alerts Generated</p>
              <p className="mt-2 text-2xl font-semibold">{analytics?.alerts_generated || 0}</p>
              <p className="mt-1 text-xs text-[var(--text-secondary)]">{analytics?.alerts_resolved || 0} resolved</p>
            </div>
            <div className="panel-soft p-4">
              <p className="text-sm text-[var(--text-muted)]">Avg DNA Score</p>
              <p className="mt-2 text-2xl font-semibold">{analytics?.avg_dna_score?.toFixed(1) || 'N/A'}</p>
            </div>
          </div>
        </section>

        {analytics?.student_breakdown?.length > 0 && (
          <section className="panel p-6">
            <h3 className="section-title">Student Breakdown</h3>
            <div className="mt-4 space-y-3">
              {analytics.student_breakdown.map((s) => (
                <div key={s.student_id} className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-4">
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <p className="font-semibold text-[var(--text-primary)]">{s.student_name}</p>
                      <p className="text-sm text-[var(--text-secondary)]">{s.problems_solved} solved · {s.solve_rate}% rate</p>
                    </div>
                    <span className={`rounded-full px-3 py-1 text-xs font-semibold ${s.open_alerts > 0 ? 'bg-amber-100 text-amber-700' : 'bg-emerald-100 text-emerald-700'}`}>
                      {s.open_alerts > 0 ? `${s.open_alerts} alerts` : 'OK'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {analytics?.weekly_trends?.length > 0 && (
          <section className="panel p-6">
            <h3 className="section-title">Weekly Trends</h3>
            <div className="mt-4 space-y-2">
              {analytics.weekly_trends.map((w) => (
                <div key={w.week_start} className="flex items-center justify-between rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface-elevated)] px-4 py-3 text-sm">
                  <span className="text-[var(--text-muted)]">Week of {w.week_start}</span>
                  <span className="font-medium">{w.active_students} active · {w.total_solved} solved</span>
                </div>
              ))}
            </div>
          </section>
        )}
      </div>
    </DashboardLayout>
  );
}

