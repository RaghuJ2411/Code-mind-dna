import React, { useEffect, useState } from 'react';
import DashboardLayout from '../../layouts/DashboardLayout';
import LoadingState from '../../components/LoadingState';
import RecruiterEmptyState from '../../components/RecruiterEmptyState';
import { listRecruiterApplications, updateRecruiterApplication } from '../../api/recruiter';
import { useRecruiterWorkflow } from '../../context/RecruiterWorkflowContext';

export default function RecruiterApplicationsPage() {
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filter, setFilter] = useState('All');
  const [savingId, setSavingId] = useState(null);
  const { selectedJob, selectedCandidate } = useRecruiterWorkflow();

  const loadApplications = async (statusFilter) => {
    setLoading(true);
    try {
      const params = statusFilter && statusFilter !== 'All' ? { status: statusFilter.toUpperCase() } : {};
      const data = await listRecruiterApplications(params);
      setApplications(data);
      setError('');
    } catch (err) {
      setError(err?.response?.data?.detail || 'Unable to load applications.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadApplications(filter);
  }, []);

  const handleStatusChange = async (appId, newStatus) => {
    setSavingId(appId);
    try {
      await updateRecruiterApplication(appId, { status: newStatus });
      await loadApplications(filter);
    } catch (err) {
      setError(err?.response?.data?.detail || 'Unable to update application.');
    } finally {
      setSavingId(null);
    }
  };

  const visibleApplications = applications;

  return (
    <DashboardLayout title="Applications" role="RECRUITER">
      <div className="space-y-6">
        {error ? <div className="rounded-[24px] border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">{error}</div> : null}
        <section className="panel p-6">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
            {(selectedJob || selectedCandidate) ? (
              <div className="rounded-[20px] border border-sky-200 bg-sky-50 px-3 py-2 text-sm text-sky-700">
                Active context: {selectedJob ? `Job • ${selectedJob.title}` : ''}{selectedCandidate ? `Candidate • ${selectedCandidate.full_name}` : ''}
              </div>
            ) : null}
            <div>
              <p className="kicker">Pipeline tracking</p>
              <h2 className="section-title">Application workflow</h2>
            </div>
            <select className="rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm" value={filter} onChange={(e) => { setFilter(e.target.value); loadApplications(e.target.value); }}>
              <option value="All">All stages</option><option value="APPLIED">Applied</option><option value="UNDER_REVIEW">Under Review</option><option value="SHORTLISTED">Shortlisted</option><option value="INTERVIEW">Interview</option><option value="OFFERED">Offered</option><option value="REJECTED">Rejected</option><option value="ACCEPTED">Accepted</option>
            </select>
          </div>

          {loading ? <LoadingState /> : visibleApplications.length === 0 ? <div className="mt-6"><RecruiterEmptyState title="No applications in this stage" description="Move candidates through the pipeline to keep the workflow active." /></div> : <div className="mt-6 space-y-4">{visibleApplications.map((app) => (
            <div key={app.id} className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-5">
              <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
                <div>
                  <p className="text-lg font-semibold text-[var(--text-primary)]">{app.student_name}</p>
                  <p className="mt-1 text-sm text-[var(--text-secondary)]">{app.job_title} at {app.job_company}</p>
                </div>
                <div className="flex flex-wrap items-center gap-2">
                  {app.fit_score != null && <span className="rounded-full bg-[var(--surface)] px-3 py-1 text-xs font-semibold text-[var(--text-secondary)]">Fit {app.fit_score?.toFixed?.(0)}</span>}
                  <select
                    className="rounded-xl border border-slate-200 bg-slate-50 px-3 py-1 text-xs"
                    value={app.status}
                    onChange={(e) => handleStatusChange(app.id, e.target.value)}
                    disabled={savingId === app.id}
                  >
                    <option value="APPLIED">Applied</option>
                    <option value="UNDER_REVIEW">Under Review</option>
                    <option value="SHORTLISTED">Shortlisted</option>
                    <option value="INTERVIEW">Interview</option>
                    <option value="OFFERED">Offered</option>
                    <option value="REJECTED">Rejected</option>
                    <option value="ACCEPTED">Accepted</option>
                  </select>
                </div>
              </div>
              <p className="mt-3 text-sm text-[var(--text-secondary)]">Applied: {new Date(app.applied_at).toLocaleDateString()}</p>
            </div>
          ))}</div>}
        </section>
      </div>
    </DashboardLayout>
  );
}

