import { useEffect, useState } from 'react';
import DashboardLayout from '../../layouts/DashboardLayout';
import {
  listMentorAlerts,
  acknowledgeMentorAlert,
  resolveMentorAlert,
  generateMentorAlerts,
  createMentorAlert,
  listMentorStudents,
} from '../../api/mentor';

export default function MentorRiskAlertsPage() {
  const [alerts, setAlerts] = useState([]);
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [generating, setGenerating] = useState(false);
  const [filter, setFilter] = useState('');
  const [form, setForm] = useState({ student_id: '', severity: 'MEDIUM', message: '' });

  const load = async () => {
    setLoading(true);
    try {
      const [alertData, studentData] = await Promise.all([listMentorAlerts(), listMentorStudents()]);
      setAlerts(alertData.items || []);
      setStudents(studentData || []);
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to load alerts');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      await generateMentorAlerts();
      await load();
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to generate alerts');
    } finally {
      setGenerating(false);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      await createMentorAlert(form);
      setForm({ student_id: '', severity: 'MEDIUM', message: '' });
      await load();
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to create alert');
    }
  };

  const filtered = alerts.filter((a) => !filter || a.status === filter);

  return (
    <DashboardLayout title="Risk Alerts" role="MENTOR">
      <div className="space-y-6">
        {error && <div className="rounded-[24px] border border-red-200 bg-red-50 p-4 text-sm text-red-600">{error}</div>}

        <section className="panel p-6">
          <div className="flex items-center justify-between gap-3">
            <div>
              <p className="kicker">Risk Management</p>
              <h2 className="section-title">Student Risk Alerts</h2>
              <p className="mt-1 body-copy">Monitor and respond to student risk signals.</p>
            </div>
            <button onClick={handleGenerate} disabled={generating} className="btn-primary">
              {generating ? 'Generating...' : 'Generate Alerts'}
            </button>
          </div>

          <div className="mt-4 flex flex-wrap gap-2">
            {['', 'OPEN', 'ACKNOWLEDGED', 'RESOLVED'].map((s) => (
              <button key={s} onClick={() => setFilter(s)} className={`rounded-full px-3 py-1.5 text-xs font-medium ${filter === s ? 'bg-[var(--brand-primary)] text-white' : 'bg-[var(--surface-elevated)] text-[var(--text-secondary)]'}`}>{s || 'All'}</button>
            ))}
          </div>

          {loading ? (
            <div className="mt-4 space-y-3">{[1, 2].map((i) => <div key={i} className="h-20 animate-pulse rounded-[24px] bg-[var(--surface-elevated)]" />)}</div>
          ) : filtered.length === 0 ? (
            <div className="mt-4 rounded-[24px] border border-dashed border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-6 text-center text-sm text-[var(--text-secondary)]">No alerts found.</div>
          ) : (
            <div className="mt-4 space-y-3">
              {filtered.map((alert) => (
                <div key={alert.id} className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-4">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${
                          alert.severity === 'HIGH' ? 'bg-red-100 text-red-700' :
                          alert.severity === 'MEDIUM' ? 'bg-amber-100 text-amber-700' :
                          'bg-blue-100 text-blue-700'
                        }`}>{alert.severity}</span>
                        <span className="text-xs text-[var(--text-muted)]">{alert.category}</span>
                        <span className={`rounded-full px-2.5 py-0.5 text-xs ${
                          alert.status === 'OPEN' ? 'bg-amber-100 text-amber-700' :
                          alert.status === 'ACKNOWLEDGED' ? 'bg-blue-100 text-blue-700' :
                          'bg-emerald-100 text-emerald-700'
                        }`}>{alert.status}</span>
                      </div>
                      <p className="mt-2 text-sm text-[var(--text-primary)]">{alert.message}</p>
                      {alert.student_id && <p className="mt-1 text-xs text-[var(--text-muted)]">Student ID: {alert.student_id}</p>}
                    </div>
                    <div className="flex gap-2">
                      {alert.status === 'OPEN' && (
                        <button onClick={() => acknowledgeMentorAlert(alert.id).then(load)} className="rounded-2xl bg-amber-600 px-3 py-1.5 text-xs text-white">Acknowledge</button>
                      )}
                      {alert.status !== 'RESOLVED' && (
                        <button onClick={() => resolveMentorAlert(alert.id).then(load)} className="rounded-2xl bg-emerald-600 px-3 py-1.5 text-xs text-white">Resolve</button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        <section className="panel p-6">
          <h3 className="section-title">Create Alert</h3>
          <form onSubmit={handleCreate} className="mt-4 space-y-4">
            <select value={form.student_id} onChange={(e) => setForm({ ...form, student_id: e.target.value })} className="w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface-elevated)] px-4 py-2.5 text-sm outline-none" required>
              <option value="">Select Student</option>
              {students.map((s) => <option key={s.id} value={s.id}>{s.full_name}</option>)}
            </select>
            <select value={form.severity} onChange={(e) => setForm({ ...form, severity: e.target.value })} className="w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface-elevated)] px-4 py-2.5 text-sm outline-none">
              <option value="LOW">Low</option>
              <option value="MEDIUM">Medium</option>
              <option value="HIGH">High</option>
              <option value="CRITICAL">Critical</option>
            </select>
            <textarea value={form.message} onChange={(e) => setForm({ ...form, message: e.target.value })} placeholder="Alert message" rows={3} className="w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface-elevated)] px-4 py-2.5 text-sm outline-none" required />
            <button type="submit" className="btn-primary">Create Alert</button>
          </form>
        </section>
      </div>
    </DashboardLayout>
  );
}

