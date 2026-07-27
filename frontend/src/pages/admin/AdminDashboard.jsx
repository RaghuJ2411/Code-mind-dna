import { useEffect, useMemo, useState } from 'react';
import DashboardLayout from '../../layouts/DashboardLayout';
import RoleOnboardingChecklist from '../../components/RoleOnboardingChecklist';
import { getAdminDashboard } from '../../api/admin';

export default function AdminDashboard() {
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const onboardingItems = useMemo(() => [
    {
      label: 'Review platform health',
      description: 'Confirm the current operational picture and any active warnings.',
      completed: Boolean(dashboard),
      href: '/admin/dashboard',
    },
    {
      label: 'Inspect user mix',
      description: 'Verify governance coverage and account health across roles.',
      completed: Boolean(dashboard?.role_counts),
      href: '/admin/users',
    },
    {
      label: 'Check problem health',
      description: 'Keep the practice catalog healthy and active for learners.',
      completed: Boolean(dashboard?.total_problems),
      href: '/admin/problems',
    },
    {
      label: 'Open audit evidence',
      description: 'Review the latest operational activity and request history.',
      completed: Boolean(dashboard?.total_audit_events),
      href: '/admin/audit-logs',
    },
  ], [dashboard]);

  useEffect(() => {
    let active = true;
    setLoading(true);
    getAdminDashboard()
      .then((data) => {
        if (active) {
          setDashboard(data);
          setError('');
        }
      })
      .catch(() => {
        if (active) {
          setError('Unable to load admin metrics right now.');
        }
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, []);

  return (
    <DashboardLayout title="Admin Dashboard" role="ADMIN">
      <div className="space-y-6">
        {error ? <div className="rounded-[24px] border border-red-200 bg-red-50 p-4 text-sm text-red-700">{error}</div> : null}

        <RoleOnboardingChecklist
          title="Your operations launchpad"
          description="Use a short checklist to keep platform health, governance, and learner experience moving forward."
          items={onboardingItems}
        />

        <section className="panel p-6">
          <div className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <p className="kicker">Critical platform warnings</p>
              <h2 className="section-title">Platform health at a glance</h2>
              <p className="mt-2 body-copy">Keep infrastructure healthy and guide operations toward the next safest action.</p>
            </div>
            <div className="metric-pill">Operational mission</div>
          </div>

          <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <div className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-4">
              <p className="text-sm text-[var(--text-muted)]">Users</p>
              <p className="mt-2 text-2xl font-semibold">{dashboard?.total_users ?? 0}</p>
              <p className="mt-1 text-sm text-[var(--text-secondary)]">Total accounts</p>
            </div>
            <div className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-4">
              <p className="text-sm text-[var(--text-muted)]">Active users</p>
              <p className="mt-2 text-2xl font-semibold">{dashboard?.active_users ?? 0}</p>
              <p className="mt-1 text-sm text-[var(--text-secondary)]">Healthy active accounts</p>
            </div>
            <div className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-4">
              <p className="text-sm text-[var(--text-muted)]">Problems</p>
              <p className="mt-2 text-2xl font-semibold">{dashboard?.active_problems ?? 0}</p>
              <p className="mt-1 text-sm text-[var(--text-secondary)]">Active learning items</p>
            </div>
            <div className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-4">
              <p className="text-sm text-[var(--text-muted)]">Audit events</p>
              <p className="mt-2 text-2xl font-semibold">{dashboard?.total_audit_events ?? 0}</p>
              <p className="mt-1 text-sm text-[var(--text-secondary)]">Captured platform activity</p>
            </div>
          </div>
        </section>

        <div className="grid gap-6 lg:grid-cols-3">
          <section className="panel p-6">
            <p className="kicker">Governance</p>
            <h2 className="section-title">Users</h2>
            <p className="mt-2 body-copy">Monitor role distribution and account health.</p>
            {loading ? (
              <div className="mt-4 h-20 animate-pulse rounded-[24px] bg-[var(--surface-elevated)]" />
            ) : dashboard ? (
              <div className="mt-4 space-y-2 text-sm text-[var(--text-secondary)]">
                <div>Admin users: <strong className="text-[var(--text-primary)]">{dashboard.role_counts?.ADMIN ?? 0}</strong></div>
                <div>Mentor users: <strong className="text-[var(--text-primary)]">{dashboard.role_counts?.MENTOR ?? 0}</strong></div>
                <div>Recruiter users: <strong className="text-[var(--text-primary)]">{dashboard.role_counts?.RECRUITER ?? 0}</strong></div>
                <div>Student users: <strong className="text-[var(--text-primary)]">{dashboard.role_counts?.STUDENT ?? 0}</strong></div>
              </div>
            ) : null}
          </section>
          <section className="panel p-6">
            <p className="kicker">Curriculum</p>
            <h2 className="section-title">Problems</h2>
            <p className="mt-2 body-copy">Keep the practice catalog healthy and active.</p>
            {loading ? (
              <div className="mt-4 h-20 animate-pulse rounded-[24px] bg-[var(--surface-elevated)]" />
            ) : dashboard ? (
              <div className="mt-4 space-y-2 text-sm text-[var(--text-secondary)]">
                <div>Total problems: <strong className="text-[var(--text-primary)]">{dashboard.total_problems}</strong></div>
                <div>Active problems: <strong className="text-[var(--text-primary)]">{dashboard.active_problems}</strong></div>
              </div>
            ) : null}
          </section>
          <section className="panel p-6">
            <p className="kicker">Audit</p>
            <h2 className="section-title">Operational evidence</h2>
            <p className="mt-2 body-copy">Review the most recent governance and request activity.</p>
            {loading ? (
              <div className="mt-4 h-20 animate-pulse rounded-[24px] bg-[var(--surface-elevated)]" />
            ) : dashboard ? (
              <div className="mt-4 text-sm text-[var(--text-secondary)]">Total audited requests: <strong className="text-[var(--text-primary)]">{dashboard.total_audit_events}</strong></div>
            ) : null}
          </section>
        </div>
      </div>
    </DashboardLayout>
  );
}
