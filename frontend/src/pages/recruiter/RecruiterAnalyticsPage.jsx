import React, { useEffect, useState } from 'react';
import DashboardLayout from '../../layouts/DashboardLayout';
import LoadingState from '../../components/LoadingState';
import { getRecruiterHiringAnalytics } from '../../api/recruiter';

export default function RecruiterAnalyticsPage() {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const load = async () => {
      try {
        const data = await getRecruiterHiringAnalytics();
        setAnalytics(data);
        setError('');
      } catch (err) {
        setError(err?.response?.data?.detail || 'Unable to load analytics.');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  return (
    <DashboardLayout title="Hiring Analytics" role="RECRUITER">
      <div className="space-y-6">
        {error ? <div className="rounded-[24px] border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">{error}</div> : null}
        <section className="panel p-6">
          <div>
            <p className="kicker">Performance intelligence</p>
            <h2 className="section-title">Analytics and recruitment KPIs</h2>
          </div>
          {loading ? <LoadingState /> : analytics ? (
            <>
              <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                <div className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-5">
                  <p className="text-sm text-[var(--text-muted)]">Active jobs</p>
                  <p className="mt-3 text-2xl font-semibold text-[var(--text-primary)]">{analytics.active_jobs}</p>
                  <p className="mt-1 text-sm text-[var(--text-secondary)]">{analytics.total_jobs} total</p>
                </div>
                <div className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-5">
                  <p className="text-sm text-[var(--text-muted)]">Applications</p>
                  <p className="mt-3 text-2xl font-semibold text-[var(--text-primary)]">{analytics.total_applications}</p>
                  <p className="mt-1 text-sm text-[var(--text-secondary)]">Total received</p>
                </div>
                <div className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-5">
                  <p className="text-sm text-[var(--text-muted)]">Offer conversion</p>
                  <p className="mt-3 text-2xl font-semibold text-[var(--text-primary)]">{analytics.offer_conversion_rate}%</p>
                  <p className="mt-1 text-sm text-[var(--text-secondary)]">Offers to hires</p>
                </div>
                <div className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-5">
                  <p className="text-sm text-[var(--text-muted)]">Shortlisted</p>
                  <p className="mt-3 text-2xl font-semibold text-[var(--text-primary)]">{analytics.total_shortlisted}</p>
                  <p className="mt-1 text-sm text-[var(--text-secondary)]">{analytics.total_interviews} interviews</p>
                </div>
              </div>

              <div className="mt-6 grid gap-4 lg:grid-cols-2">
                <div className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-5">
                  <p className="text-lg font-semibold text-[var(--text-primary)]">Hiring funnel</p>
                  <div className="mt-4 space-y-3 text-sm text-[var(--text-secondary)]">
                    {Object.entries(analytics.hiring_funnel || {}).map(([stage, count]) => (
                      <div key={stage} className="flex items-center justify-between">
                        <span className="capitalize">{stage.replace(/_/g, ' ')}</span>
                        <span className="font-semibold text-[var(--text-primary)]">{count}</span>
                      </div>
                    ))}
                  </div>
                </div>
                <div className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-5">
                  <p className="text-lg font-semibold text-[var(--text-primary)]">Top skills demand</p>
                  <div className="mt-4 flex flex-wrap gap-2">
                    {(analytics.top_skills_demand || []).length === 0 ? (
                      <span className="text-sm text-[var(--text-secondary)]">No skills data yet</span>
                    ) : (
                      analytics.top_skills_demand.map((item) => (
                        <span key={item.skill} className="rounded-full bg-[var(--surface)] px-3 py-1 text-sm">
                          {item.skill} ({item.count})
                        </span>
                      ))
                    )}
                  </div>
                </div>
              </div>
            </>
          ) : null}
        </section>
      </div>
    </DashboardLayout>
  );
}

