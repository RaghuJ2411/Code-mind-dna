import { useEffect, useState } from 'react';
import DashboardLayout from '../../layouts/DashboardLayout';
import { generateStudentProgressReport, generateAlertsSummaryReport, generateEngagementReport, listMentorStudents } from '../../api/mentor';

export default function MentorReportsPage() {
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [report, setReport] = useState(null);
  const [reportType, setReportType] = useState('progress');
  const [selectedStudent, setSelectedStudent] = useState('');
  const [days, setDays] = useState(30);

  const generateReport = async () => {
    setLoading(true);
    setReport(null);
    try {
      let data;
      if (reportType === 'progress') {
        data = await generateStudentProgressReport(selectedStudent || null, days);
      } else if (reportType === 'alerts') {
        data = await generateAlertsSummaryReport(days);
      } else {
        data = await generateEngagementReport(days);
      }
      setReport(data);
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to generate report');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const loadStudents = async () => {
      try {
        const data = await listMentorStudents();
        setStudents(data || []);
      } catch {}
    };
    loadStudents();
  }, []);

  return (
    <DashboardLayout title="Reports" role="MENTOR">
      <div className="space-y-6">
        {error && <div className="rounded-[24px] border border-red-200 bg-red-50 p-4 text-sm text-red-600">{error}</div>}

        <section className="panel p-6">
          <p className="kicker">Reporting</p>
          <h2 className="section-title">Generate Reports</h2>
          <p className="mt-2 body-copy">Create detailed reports on student progress, risk alerts, and engagement metrics.</p>

          <div className="mt-6 grid gap-4 rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-6 md:grid-cols-3">
            <div>
              <label className="block text-sm font-medium text-[var(--text-secondary)]">Report Type</label>
              <select value={reportType} onChange={(e) => setReportType(e.target.value)} className="mt-1 w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] px-4 py-2.5 text-sm outline-none">
                <option value="progress">Student Progress</option>
                <option value="alerts">Alerts Summary</option>
                <option value="engagement">Engagement</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-[var(--text-secondary)]">Student (optional)</label>
              <select value={selectedStudent} onChange={(e) => setSelectedStudent(e.target.value)} className="mt-1 w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] px-4 py-2.5 text-sm outline-none">
                <option value="">All Students</option>
                {students.map((s) => <option key={s.id} value={s.id}>{s.full_name}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-[var(--text-secondary)]">Days</label>
              <input type="number" value={days} onChange={(e) => setDays(parseInt(e.target.value) || 30)} min={1} max={365} className="mt-1 w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] px-4 py-2.5 text-sm outline-none" />
            </div>
          </div>
          <button onClick={generateReport} disabled={loading} className="btn-primary mt-4">{loading ? 'Generating...' : 'Generate Report'}</button>
        </section>

        {report && (
          <section className="panel p-6">
            <h3 className="section-title">Report Results</h3>
            <div className="mt-4 space-y-4">
              {report.students?.length > 0 && (
                <div className="space-y-3">
                  {report.students.map((s) => (
                    <div key={s.student_id} className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-4">
                      <p className="font-semibold text-[var(--text-primary)]">{s.student_name}</p>
                      <div className="mt-2 grid grid-cols-2 gap-3 text-sm md:grid-cols-4">
                        <div><span className="text-[var(--text-muted)]">Solved:</span> {s.problems_solved}</div>
                        <div><span className="text-[var(--text-muted)]">Rate:</span> {s.solve_rate}%</div>
                        <div><span className="text-[var(--text-muted)]">DNA:</span> {s.dna_score?.toFixed(1) || 'N/A'}</div>
                        <div><span className="text-[var(--text-muted)]">Active:</span> {s.active_days > 0 ? `${s.active_days}d` : 'Inactive'}</div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
              {report.alerts?.length > 0 && (
                <div className="space-y-2">
                  {report.alerts.map((a) => (
                    <div key={a.id} className="rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-3 text-sm">
                      <div className="flex items-center justify-between">
                        <span className="font-medium">{a.category}</span>
                        <span className={`rounded-full px-2 py-0.5 text-xs ${a.severity === 'HIGH' ? 'bg-red-100 text-red-700' : 'bg-amber-100 text-amber-700'}`}>{a.severity}</span>
                      </div>
                      <p className="mt-1 text-[var(--text-secondary)]">{a.message}</p>
                    </div>
                  ))}
                </div>
              )}
              {report.summary && (
                <div className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-4">
                  <p className="font-semibold text-[var(--text-primary)]">Summary</p>
                  <pre className="mt-2 whitespace-pre-wrap text-sm text-[var(--text-secondary)]">{typeof report.summary === 'object' ? JSON.stringify(report.summary, null, 2) : report.summary}</pre>
                </div>
              )}
              {(!report.students && !report.alerts && !report.summary) && (
                <pre className="overflow-x-auto rounded-2xl bg-[var(--surface-elevated)] p-4 text-sm">{JSON.stringify(report, null, 2)}</pre>
              )}
            </div>
          </section>
        )}
      </div>
    </DashboardLayout>
  );
}

