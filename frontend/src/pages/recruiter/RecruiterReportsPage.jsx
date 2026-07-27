import React, { useEffect, useState } from 'react';
import DashboardLayout from '../../layouts/DashboardLayout';
import LoadingState from '../../components/LoadingState';
import RecruiterEmptyState from '../../components/RecruiterEmptyState';
import { generateRecruiterReport, listRecruiterReports } from '../../api/recruiter';

export default function RecruiterReportsPage() {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState('');
  const reportTypes = [
    { type: 'recruitment', title: 'Recruitment report', description: 'Monthly hiring activity and pipeline movement.' },
    { type: 'hiring', title: 'Hiring report', description: 'Overview of offers, conversions, and interviews.' },
    { type: 'candidate', title: 'Candidate report', description: 'Talent profile health and readiness indicators.' },
  ];

  const loadReports = async () => {
    setLoading(true);
    try {
      const data = await listRecruiterReports();
      setReports(data);
      setError('');
    } catch (err) {
      setError(err?.response?.data?.detail || 'Unable to load reports.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadReports();
  }, []);

  const handleGenerate = async (reportType) => {
    setGenerating(true);
    try {
      await generateRecruiterReport(reportType);
      await loadReports();
    } catch (err) {
      setError(err?.response?.data?.detail || 'Unable to generate report.');
    } finally {
      setGenerating(false);
    }
  };

  return (
    <DashboardLayout title="Reports" role="RECRUITER">
      <div className="space-y-6">
        {error ? <div className="rounded-[24px] border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">{error}</div> : null}
        <section className="panel p-6">
          <div>
            <p className="kicker">Reporting</p>
            <h2 className="section-title">Generate reports</h2>
          </div>
          <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {reportTypes.map((rt) => (
              <div key={rt.type} className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-5">
                <p className="text-lg font-semibold text-[var(--text-primary)]">{rt.title}</p>
                <p className="mt-2 text-sm text-[var(--text-secondary)]">{rt.description}</p>
                <div className="mt-4">
                  <button className="btn-primary" onClick={() => handleGenerate(rt.type)} disabled={generating}>
                    {generating ? 'Generating...' : 'Generate'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className="panel p-6">
          <p className="kicker">Generated reports</p>
          <h2 className="section-title">Report history</h2>
          {loading ? <LoadingState /> : reports.length === 0 ? <div className="mt-6"><RecruiterEmptyState title="No reports generated yet" description="Generate a report to see it here." /></div> : <div className="mt-6 space-y-4">{reports.map((report) => (
            <div key={report.id} className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-5">
              <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
                <div>
                  <p className="text-lg font-semibold text-[var(--text-primary)]">{report.title}</p>
                  <p className="mt-1 text-sm text-[var(--text-secondary)]">{report.description}</p>
                </div>
                <span className="rounded-full bg-[var(--surface)] px-3 py-1 text-xs font-semibold text-[var(--text-secondary)]">{new Date(report.generated_at).toLocaleString()}</span>
              </div>
            </div>
          ))}</div>}
        </section>
      </div>
    </DashboardLayout>
  );
}

