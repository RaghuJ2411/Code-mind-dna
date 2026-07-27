import { useEffect, useState } from 'react';
import DashboardLayout from '../../layouts/DashboardLayout';
import { getSystemOverview, getSystemServices, getSystemLogs } from '../../api/admin';

export default function SystemHealthPage() {
  const [overview, setOverview] = useState(null);
  const [services, setServices] = useState([]);
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let active = true;
    setLoading(true);
    Promise.all([
      getSystemOverview(),
      getSystemServices(),
      getSystemLogs({ page: 1, page_size: 20 }),
    ])
      .then(([overviewData, servicesData, logsData]) => {
        if (active) {
          setOverview(overviewData);
          setServices(servicesData.services || []);
          setLogs(logsData.items || []);
        }
      })
      .catch(() => {
        if (active) setError('Unable to load system health data.');
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => { active = false; };
  }, []);

  return (
    <DashboardLayout title="System Monitoring" role="ADMIN">
      <div className="space-y-6">
        {error && <div className="rounded-[24px] border border-red-200 bg-red-50 p-4 text-sm text-red-700">{error}</div>}

        <section className="panel p-6">
          <div className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <p className="kicker">Infrastructure</p>
              <h2 className="section-title">System health</h2>
              <p className="mt-2 body-copy">Real-time platform infrastructure metrics.</p>
            </div>
          </div>

          <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <div className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-4">
              <p className="text-sm text-[var(--text-muted)]">Uptime</p>
              <p className="mt-2 text-2xl font-semibold">{overview?.uptime_seconds ?? '—'}s</p>
            </div>
            <div className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-4">
              <p className="text-sm text-[var(--text-muted)]">CPU</p>
              <p className="mt-2 text-2xl font-semibold">{overview?.cpu_percent ?? 0}%</p>
            </div>
            <div className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-4">
              <p className="text-sm text-[var(--text-muted)]">Memory</p>
              <p className="mt-2 text-2xl font-semibold">{overview?.memory_percent ?? 0}%</p>
            </div>
            <div className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-4">
              <p className="text-sm text-[var(--text-muted)]">Disk</p>
              <p className="mt-2 text-2xl font-semibold">{overview?.disk_percent ?? 0}%</p>
            </div>
          </div>
        </section>

        <section className="panel p-6">
          <p className="kicker">Services</p>
          <h2 className="section-title">Service status</h2>
          <div className="mt-4 space-y-2">
            {loading
              ? <div className="h-20 animate-pulse rounded-[24px] bg-[var(--surface-elevated)]" />
              : services.map((svc) => (
                  <div key={svc.name} className="flex items-center justify-between rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] px-4 py-3">
                    <span className="font-medium text-[var(--text-primary)]">{svc.name}</span>
                    <span className={`rounded-full px-3 py-1 text-xs font-semibold ${
                      svc.status === 'healthy' ? 'bg-green-100 text-green-700' :
                      svc.status === 'degraded' ? 'bg-yellow-100 text-yellow-700' :
                      'bg-red-100 text-red-700'
                    }`}>{svc.status}</span>
                  </div>
                ))}
          </div>
        </section>

        <section className="panel p-6">
          <p className="kicker">Activity</p>
          <h2 className="section-title">Recent system logs</h2>
          <div className="mt-4 overflow-x-auto">
            <table className="min-w-full divide-y divide-[var(--border-subtle)] text-sm">
              <thead className="bg-[var(--surface-elevated)] text-left text-[var(--text-muted)]">
                <tr>
                  <th className="px-4 py-3">Level</th>
                  <th className="px-4 py-3">Message</th>
                  <th className="px-4 py-3">Source</th>
                  <th className="px-4 py-3">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--border-subtle)] bg-[var(--surface)]">
                {loading ? (
                  <tr><td colSpan="4" className="px-4 py-6 text-center text-[var(--text-muted)]">Loading logs...</td></tr>
                ) : logs.length === 0 ? (
                  <tr><td colSpan="4" className="px-4 py-6 text-center text-[var(--text-muted)]">No logs available.</td></tr>
                ) : logs.map((log) => (
                  <tr key={log.id} className="hover:bg-[var(--surface-elevated)]">
                    <td className="px-4 py-3">
                      <span className={`rounded-full px-2 py-0.5 text-xs font-semibold ${
                        log.level === 'ERROR' ? 'bg-red-100 text-red-700' :
                        log.level === 'WARN' ? 'bg-yellow-100 text-yellow-700' :
                        'bg-blue-100 text-blue-700'
                      }`}>{log.level}</span>
                    </td>
                    <td className="px-4 py-3 text-[var(--text-secondary)]">{log.message}</td>
                    <td className="px-4 py-3 text-[var(--text-secondary)]">{log.source}</td>
                    <td className="px-4 py-3 text-[var(--text-muted)]">{log.created_at ? new Date(log.created_at).toLocaleString() : '—'}</td>
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

