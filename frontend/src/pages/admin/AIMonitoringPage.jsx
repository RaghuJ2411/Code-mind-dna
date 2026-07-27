import { useEffect, useState } from 'react';
import DashboardLayout from '../../layouts/DashboardLayout';
import { getAIUsageOverview, listAIRequests, getAILimits, updateAILimits } from '../../api/admin';

export default function AIMonitoringPage() {
  const [usage, setUsage] = useState(null);
  const [requests, setRequests] = useState([]);
  const [limits, setLimits] = useState(null);
  const [editLimits, setEditLimits] = useState({});
  const [editing, setEditing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');

  const fetchData = async () => {
    setLoading(true);
    try {
      const [usageData, requestsData, limitsData] = await Promise.all([
        getAIUsageOverview(),
        listAIRequests({ page: 1, page_size: 20 }),
        getAILimits(),
      ]);
      setUsage(usageData);
      setRequests(requestsData.items || []);
      setLimits(limitsData);
      setEditLimits({
        code_review: limitsData.code_review,
        error_explanation: limitsData.error_explanation,
        skill_gap: limitsData.skill_gap,
        roadmap: limitsData.roadmap,
      });
    } catch {
      setMessage('Unable to load AI monitoring data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

  const handleSaveLimits = async () => {
    try {
      const updated = await updateAILimits(editLimits);
      setLimits(updated);
      setEditing(false);
      setMessage('AI limits updated.');
    } catch {
      setMessage('Unable to update AI limits.');
    }
  };

  return (
    <DashboardLayout title="AI Monitoring" role="ADMIN">
      <div className="space-y-6">
        {message && <div className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface)] p-3 text-sm text-[var(--text-secondary)]">{message}</div>}

        <section className="panel p-6">
          <p className="kicker">Artificial intelligence</p>
          <h2 className="section-title">AI usage overview</h2>
          <div className="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <div className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-4">
              <p className="text-sm text-[var(--text-muted)]">Total requests</p>
              <p className="mt-2 text-2xl font-semibold">{usage?.total_requests ?? 0}</p>
            </div>
            <div className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-4">
              <p className="text-sm text-[var(--text-muted)]">Success rate</p>
              <p className="mt-2 text-2xl font-semibold">
                {usage?.total_requests ? ((usage.success_count / usage.total_requests) * 100).toFixed(1) : 0}%
              </p>
            </div>
            <div className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-4">
              <p className="text-sm text-[var(--text-muted)]">Requests today</p>
              <p className="mt-2 text-2xl font-semibold">{usage?.requests_today ?? 0}</p>
            </div>
            <div className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-4">
              <p className="text-sm text-[var(--text-muted)]">Avg latency</p>
              <p className="mt-2 text-2xl font-semibold">{usage?.avg_latency_ms?.toFixed(0) ?? 0}ms</p>
            </div>
          </div>
        </section>

        <section className="panel p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="kicker">Rate limiting</p>
              <h2 className="section-title">Daily AI limits</h2>
            </div>
            <button onClick={() => editing ? handleSaveLimits() : setEditing(true)} className={editing ? 'btn-primary' : 'btn-secondary'}>
              {editing ? 'Save limits' : 'Edit limits'}
            </button>
          </div>
          <div className="mt-4 space-y-3">
            {['code_review', 'error_explanation', 'skill_gap', 'roadmap'].map((key) => (
              <div key={key} className="flex items-center justify-between rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] px-4 py-3">
                <span className="text-sm capitalize text-[var(--text-primary)]">{key.replace('_', ' ')}</span>
                {editing ? (
                  <input
                    type="number"
                    value={editLimits[key] ?? 0}
                    onChange={(e) => setEditLimits((prev) => ({ ...prev, [key]: Number(e.target.value) }))}
                    className="w-20 rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] px-3 py-1 text-sm text-right outline-none"
                  />
                ) : (
                  <span className="text-sm font-semibold text-[var(--text-secondary)]">{limits?.[key] ?? 0}</span>
                )}
              </div>
            ))}
          </div>
        </section>

        <section className="panel p-6">
          <p className="kicker">History</p>
          <h2 className="section-title">Recent AI requests</h2>
          <div className="mt-4 overflow-x-auto">
            <table className="min-w-full divide-y divide-[var(--border-subtle)] text-sm">
              <thead className="bg-[var(--surface-elevated)] text-left text-[var(--text-muted)]">
                <tr>
                  <th className="px-4 py-3">Task type</th>
                  <th className="px-4 py-3">Provider</th>
                  <th className="px-4 py-3">Model</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Latency</th>
                  <th className="px-4 py-3">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--border-subtle)] bg-[var(--surface)]">
                {loading ? (
                  <tr><td colSpan="6" className="px-4 py-6 text-center text-[var(--text-muted)]">Loading...</td></tr>
                ) : requests.length === 0 ? (
                  <tr><td colSpan="6" className="px-4 py-6 text-center text-[var(--text-muted)]">No AI requests yet.</td></tr>
                ) : requests.map((req) => (
                  <tr key={req.id} className="hover:bg-[var(--surface-elevated)]">
                    <td className="px-4 py-3 text-[var(--text-secondary)]">{req.task_type}</td>
                    <td className="px-4 py-3 text-[var(--text-secondary)]">{req.provider || '—'}</td>
                    <td className="px-4 py-3 text-[var(--text-secondary)]">{req.model || '—'}</td>
                    <td className="px-4 py-3">
                      <span className={`rounded-full px-2 py-0.5 text-xs font-semibold ${
                        req.status === 'success' ? 'bg-green-100 text-green-700' :
                        req.status === 'failed' ? 'bg-red-100 text-red-700' :
                        'bg-yellow-100 text-yellow-700'
                      }`}>{req.status}</span>
                    </td>
                    <td className="px-4 py-3 text-[var(--text-secondary)]">{req.latency_ms ? `${req.latency_ms}ms` : '—'}</td>
                    <td className="px-4 py-3 text-[var(--text-muted)]">{req.created_at ? new Date(req.created_at).toLocaleString() : '—'}</td>
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

