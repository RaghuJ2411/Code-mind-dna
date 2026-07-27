import React, { useEffect, useState } from 'react';
import DashboardLayout from '../../layouts/DashboardLayout';
import { getAnalyticsDaily, getAnalyticsProfile, getAnalyticsWeekly } from '../../api/student';

export default function AnalyticsPage() {
  const [profile, setProfile] = useState(null);
  const [daily, setDaily] = useState([]);
  const [weekly, setWeekly] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        const [profileData, dailyData, weeklyData] = await Promise.all([
          getAnalyticsProfile(),
          getAnalyticsDaily(),
          getAnalyticsWeekly(),
        ]);
        setProfile(profileData);
        setDaily(dailyData.data || []);
        setWeekly(weeklyData.data || []);
      } catch (err) {
        setError(err?.response?.data?.detail || 'Unable to load analytics.');
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  return (
    <DashboardLayout title="Analytics Overview" role="STUDENT" headingLevel={2}>
      <div className="space-y-6">
        <section className="panel p-6">
          <div className="flex flex-col gap-2 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <p className="kicker">Performance intelligence</p>
              <h2 className="section-title">Evidence-backed performance trends</h2>
              <p className="mt-1 body-copy">Review your recent patterns in a way that highlights progress, consistency, and next opportunities.</p>
            </div>
            <div className="metric-pill">Updated from live activity</div>
          </div>
          {loading ? (
            <div className="mt-6 grid gap-4 md:grid-cols-3">
              {[1, 2, 3].map((item) => <div key={item} className="h-24 animate-pulse rounded-[24px] bg-[var(--surface-elevated)]" />)}
            </div>
          ) : error ? (
            <p className="mt-6 rounded-[24px] border border-red-200 bg-red-50 p-3 text-sm text-red-600">{error}</p>
          ) : (
            <div className="mt-6 grid gap-4 md:grid-cols-3">
              <div className="panel-soft p-4">
                <p className="text-sm text-[var(--text-muted)]">Evidence status</p>
                <p className="mt-2 text-xl font-semibold uppercase">{profile?.evidence_status}</p>
              </div>
              <div className="panel-soft p-4">
                <p className="text-sm text-[var(--text-muted)]">Solve rate</p>
                <p className="mt-2 text-xl font-semibold">{(profile?.success?.solve_rate ?? 0).toFixed(2)}</p>
              </div>
              <div className="panel-soft p-4">
                <p className="text-sm text-[var(--text-muted)]">Active days</p>
                <p className="mt-2 text-xl font-semibold">{profile?.consistency?.active_days_last_7 ?? 0}</p>
              </div>
            </div>
          )}
        </section>

        <section className="grid gap-6 lg:grid-cols-2">
          <div className="panel p-6">
            <h3 className="section-title">Recent daily analytics</h3>
            {daily.length === 0 ? (
              <p className="mt-4 body-copy">No daily analytics yet.</p>
            ) : (
              <div className="mt-4 space-y-2">
                {daily.slice(0, 5).map((item, index) => (
                  <div key={`${item.analytics_date || index}`} className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-3 text-sm text-[var(--text-secondary)]">
                    <div className="flex items-center justify-between gap-3">
                      <span>{item.analytics_date}</span>
                      <span>{item.problems_solved}/{item.problems_attempted} solved</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
          <div className="panel p-6">
            <h3 className="section-title">Recent weekly analytics</h3>
            {weekly.length === 0 ? (
              <p className="mt-4 body-copy">No weekly analytics yet.</p>
            ) : (
              <div className="mt-4 space-y-2">
                {weekly.slice(0, 5).map((item, index) => (
                  <div key={`${item.week_start || index}`} className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-3 text-sm text-[var(--text-secondary)]">
                    <div className="flex items-center justify-between gap-3">
                      <span>{item.week_start}</span>
                      <span>{(item.solve_rate ?? 0).toFixed(2)} solve rate</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </section>
      </div>
    </DashboardLayout>
  );
}
