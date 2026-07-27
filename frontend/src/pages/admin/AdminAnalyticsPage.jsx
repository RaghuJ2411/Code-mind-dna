import { useEffect, useState } from 'react';
import DashboardLayout from '../../layouts/DashboardLayout';
import {
  getPlatformAnalyticsOverview,
  getPlatformEngagement,
  getPlatformUsage,
} from '../../api/admin';

export default function AdminAnalyticsPage() {
  const [overview, setOverview] = useState(null);
  const [engagement, setEngagement] = useState(null);
  const [usage, setUsage] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let active = true;
    setLoading(true);
    Promise.all([
      getPlatformAnalyticsOverview(),
      getPlatformEngagement({ days: 30 }),
      getPlatformUsage(),
    ])
      .then(([overviewData, engagementData, usageData]) => {
        if (active) {
          setOverview(overviewData);
          setEngagement(engagementData);
          setUsage(usageData);
        }
      })
      .catch(() => {
        if (active) setError('Unable to load platform analytics.');
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => { active = false; };
  }, []);

  return (
    <DashboardLayout title="Platform Analytics" role="ADMIN">
      <div className="space-y-6">
        {error && <div className="rounded-[24px] border border-red-200 bg-red-50 p-4 text-sm text-red-700">{error}</div>}

        <section className="panel p-6">
          <p className="kicker">Metrics</p>
          <h2 className="section-title">Platform overview</h2>
          <div className="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <div className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-4">
              <p className="text-sm text-[var(--text-muted)]">Total users</p>
              <p className="mt-2 text-2xl font-semibold">{overview?.total_users ?? 0}</p>
            </div>
            <div className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-4">
              <p className="text-sm text-[var(--text-muted)]">Total problems</p>
              <p className="mt-2 text-2xl font-semibold">{overview?.total_problems ?? 0}</p>
            </div>
            <div className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-4">
              <p className="text-sm text-[var(--text-muted)]">New users (7d)</p>
              <p className="mt-2 text-2xl font-semibold">{overview?.new_users_last_7d ?? 0}</p>
            </div>
            <div className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-4">
              <p className="text-sm text-[var(--text-muted)]">Active users (30d)</p>
              <p className="mt-2 text-2xl font-semibold">{overview?.active_users_last_30d ?? 0}</p>
            </div>
          </div>
        </section>

        <div className="grid gap-6 lg:grid-cols-2">
          <section className="panel p-6">
            <p className="kicker">Users by role</p>
            <h2 className="section-title">Role distribution</h2>
            {loading ? (
              <div className="mt-4 h-32 animate-pulse rounded-[24px] bg-[var(--surface-elevated)]" />
            ) : usage?.users_by_role ? (
              <div className="mt-4 space-y-3">
                {Object.entries(usage.users_by_role).map(([role, count]) => (
                  <div key={role} className="flex items-center justify-between rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] px-4 py-3">
                    <span className="text-sm text-[var(--text-primary)]">{role}</span>
                    <span className="text-sm font-semibold text-[var(--text-secondary)]">{count}</span>
                  </div>
                ))}
              </div>
            ) : null}
          </section>

          <section className="panel p-6">
            <p className="kicker">Problems by difficulty</p>
            <h2 className="section-title">Difficulty breakdown</h2>
            {loading ? (
              <div className="mt-4 h-32 animate-pulse rounded-[24px] bg-[var(--surface-elevated)]" />
            ) : usage?.problems_by_difficulty ? (
              <div className="mt-4 space-y-3">
                {Object.entries(usage.problems_by_difficulty).map(([difficulty, count]) => (
                  <div key={difficulty} className="flex items-center justify-between rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] px-4 py-3">
                    <span className="text-sm text-[var(--text-primary)]">{difficulty}</span>
                    <span className="text-sm font-semibold text-[var(--text-secondary)]">{count}</span>
                  </div>
                ))}
              </div>
            ) : null}
          </section>
        </div>

        <section className="panel p-6">
          <p className="kicker">Engagement</p>
          <h2 className="section-title">Daily activity (30 days)</h2>
          <div className="mt-4 overflow-x-auto">
            <table className="min-w-full divide-y divide-[var(--border-subtle)] text-sm">
              <thead className="bg-[var(--surface-elevated)] text-left text-[var(--text-muted)]">
                <tr>
                  <th className="px-4 py-3">Date</th>
                  <th className="px-4 py-3">Active users</th>
                  <th className="px-4 py-3">Requests</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--border-subtle)] bg-[var(--surface)]">
                {loading ? (
                  <tr><td colSpan="3" className="px-4 py-6 text-center text-[var(--text-muted)]">Loading...</td></tr>
                ) : engagement?.daily_active_users?.length === 0 ? (
                  <tr><td colSpan="3" className="px-4 py-6 text-center text-[var(--text-muted)]">No engagement data.</td></tr>
                ) : engagement?.daily_active_users?.map((day, idx) => (
                  <tr key={idx} className="hover:bg-[var(--surface-elevated)]">
                    <td className="px-4 py-3 text-[var(--text-secondary)]">{day.date}</td>
                    <td className="px-4 py-3 text-[var(--text-secondary)]">{day.active_users}</td>
                    <td className="px-4 py-3 text-[var(--text-secondary)]">{day.requests}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </DashboardLayout>
  );
}

