import { useEffect, useState } from 'react';
import DashboardLayout from '../../layouts/DashboardLayout';
import { listAdminReports, generateAdminReport } from '../../api/admin';

const REPORT_TYPES = [
  { value: 'user_summary', label: 'User Summary' },
  { value: 'problem_stats', label: 'Problem Statistics' },
  { value: 'platform_overview', label: 'Platform Overview' },
  { value: 'ai_usage', label: 'AI Usage Report' },
];

export default function AdminReportsPage() {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [selectedType, setSelectedType] = useState('user_summary');
  const [message, setMessage] = useState('');

  const fetchReports = async () => {
    try {
      const data = await listAdminReports();
      setReports(data.items || []);
    } catch {
      setMessage('Unable to load reports.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchReports(); }, []);

  const handleGenerate = async () => {
    setGenerating(true);
    setMessage('');
    try {
      const report = await generateAdminReport({ report_type: selectedType });
      setReports((prev) => [...prev, report]);
      setMessage(`Report "${report.title}" generated successfully.`);
    } catch (err) {
      setMessage(err?.response?.data?.detail || 'Unable to generate report.');
    } finally {
      setGenerating(false);
    }
  };

  return (
    <DashboardLayout title="Reports" role="ADMIN">
      <div className="space-y-6">
        {message && <div className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface)] p-3 text-sm text-[var(--text-secondary)]">{message}</div>}

        <section className="panel p-6">
          <p className="kicker">Reporting</p>
          <h2 className="section-title">Generate report</h2>
          <p className="mt-2 body-copy">Create a new platform report with current data.</p>
          <div className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-end">
            <div className="flex-1">
              <label className="mb-1 block text-sm text-[var(--text-secondary)]">Report type</label>
              <select
                value={selectedType}
                onChange={(e) => setSelectedType(e.target.value)}
                className="w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] px-3 py-2 text-sm outline-none"
              >
                {REPORT_TYPES.map((type) => (
                  <option key={type.value} value={type.value}>{type.label}</option>
                ))}
              </select>
            </div>
            <button onClick={handleGenerate} disabled={generating} className="btn-primary">
              {generating ? 'Generating...' : 'Generate report'}
            </button>
          </div>
        </section>

        <section className="panel p-6">
          <p className="kicker">History</p>
          <h2 className="section-title">Generated reports</h2>
          <div className="mt-4 overflow-x-auto">
            <table className="min-w-full divide-y divide-[var(--border-subtle)] text-sm">
              <thead className="bg-[var(--surface-elevated)] text-left text-[var(--text-muted)]">
                <tr>
                  <th className="px-4 py-3">Title</th>
                  <th className="px-4 py-3">Type</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Created</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--border-subtle)] bg-[var(--surface)]">
                {loading ? (
                  <tr><td colSpan="4" className="px-4 py-6 text-center text-[var(--text-muted)]">Loading reports...</td></tr>
                ) : reports.length === 0 ? (
                  <tr><td colSpan="4" className="px-4 py-6 text-center text-[var(--text-muted)]">No reports generated yet.</td></tr>
                ) : reports.map((report) => (
                  <tr key={report.id} className="hover:bg-[var(--surface-elevated)]">
                    <td className="px-4 py-3 font-medium text-[var(--text-primary)]">{report.title}</td>
                    <td className="px-4 py-3 text-[var(--text-secondary)]">{report.report_type}</td>
                    <td className="px-4 py-3">
                      <span className="rounded-full bg-green-100 px-2 py-0.5 text-xs font-semibold text-green-700">{report.status}</span>
                    </td>
                    <td className="px-4 py-3 text-[var(--text-muted)]">{report.created_at ? new Date(report.created_at).toLocaleString() : '—'}</td>
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

