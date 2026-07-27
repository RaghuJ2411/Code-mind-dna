import { useEffect, useState } from 'react';
import DashboardLayout from '../../layouts/DashboardLayout';
import { getStudentApplications, getStudentJobs } from '../../api/student';
import { useNavigate } from 'react-router-dom';

const STATUS_ORDER = ['APPLIED', 'UNDER_REVIEW', 'SHORTLISTED', 'INTERVIEW', 'OFFER', 'REJECTED'];
const STATUS_COLORS = {
  APPLIED: 'bg-blue-100 text-blue-700',
  UNDER_REVIEW: 'bg-amber-100 text-amber-700',
  SHORTLISTED: 'bg-emerald-100 text-emerald-700',
  INTERVIEW: 'bg-purple-100 text-purple-700',
  OFFER: 'bg-green-100 text-green-700',
  REJECTED: 'bg-red-100 text-red-700',
};

export default function ApplicationsPage() {
  const [applications, setApplications] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [statusFilter, setStatusFilter] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const loadData = async () => {
      try {
        const [appsData, jobsData] = await Promise.all([getStudentApplications(), getStudentJobs()]);
        setApplications(appsData);
        setJobs(jobsData);
      } catch (err) {
        setError(err?.response?.data?.detail || 'Failed to load applications');
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  const filtered = applications.filter((a) => !statusFilter || a.status === statusFilter);

  return (
    <DashboardLayout title="Applications" role="STUDENT">
      <div className="space-y-6">
        {error && <div className="rounded-[24px] border border-red-200 bg-red-50 p-4 text-sm text-red-600">{error}</div>}

        <section className="panel p-6">
          <div className="flex items-center justify-between gap-3">
            <div>
              <p className="kicker">Track</p>
              <h2 className="section-title">Your Applications</h2>
              <p className="mt-1 body-copy">Monitor the status of all your job applications in one place.</p>
            </div>
            <span className="metric-pill">{applications.length} total</span>
          </div>

          <div className="mt-4 flex flex-wrap gap-2">
            <button onClick={() => setStatusFilter('')} className={`rounded-full px-3 py-1.5 text-xs font-medium transition ${!statusFilter ? 'bg-[var(--brand-primary)] text-white' : 'bg-[var(--surface-elevated)] text-[var(--text-secondary)]'}`}>All</button>
            {STATUS_ORDER.map((s) => (
              <button key={s} onClick={() => setStatusFilter(s)} className={`rounded-full px-3 py-1.5 text-xs font-medium transition ${statusFilter === s ? 'bg-[var(--brand-primary)] text-white' : 'bg-[var(--surface-elevated)] text-[var(--text-secondary)]'}`}>{s.replace(/_/g, ' ')}</button>
            ))}
          </div>

          {loading ? (
            <div className="mt-6 space-y-3">{[1, 2, 3].map((i) => <div key={i} className="h-24 animate-pulse rounded-[24px] bg-[var(--surface-elevated)]" />)}</div>
          ) : filtered.length === 0 ? (
            <div className="mt-6 rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-8 text-center">
              <p className="text-3xl">📋</p>
              <p className="mt-3 font-semibold text-[var(--text-primary)]">No applications yet</p>
              <p className="mt-2 body-copy">Browse available jobs and submit your first application.</p>
              <button onClick={() => navigate('/student/jobs')} className="btn-primary mt-4">Browse Jobs</button>
            </div>
          ) : (
            <div className="mt-6 space-y-3">
              {filtered.map((app) => {
                const job = jobs.find((j) => j.id === app.job_id);
                return (
                  <div key={app.id} className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-4">
                    <div className="flex items-center justify-between gap-3">
                      <div>
                        <p className="font-semibold text-[var(--text-primary)]">{job?.title || `Job #${app.job_id}`}</p>
                        <p className="text-sm text-[var(--text-secondary)]">{job?.company || 'Unknown'} · Applied {new Date(app.applied_at).toLocaleDateString()}</p>
                      </div>
                      <span className={`rounded-full px-3 py-1.5 text-xs font-semibold ${STATUS_COLORS[app.status] || 'bg-slate-100 text-slate-700'}`}>{app.status.replace(/_/g, ' ')}</span>
                    </div>
                    <div className="mt-3 flex items-center gap-2">
                      {STATUS_ORDER.map((s, i) => {
                        const currentIdx = STATUS_ORDER.indexOf(app.status);
                        const isPast = i <= currentIdx;
                        return (
                          <div key={s} className="flex items-center gap-1">
                            <div className={`h-2 w-2 rounded-full ${isPast ? 'bg-[var(--brand-primary)]' : 'bg-[var(--surface-interactive)]'}`} />
                            {i < STATUS_ORDER.length - 1 && <div className={`h-0.5 w-8 ${i < currentIdx ? 'bg-[var(--brand-primary)]' : 'bg-[var(--surface-interactive)]'}`} />}
                          </div>
                        );
                      })}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </section>
      </div>
    </DashboardLayout>
  );
}

