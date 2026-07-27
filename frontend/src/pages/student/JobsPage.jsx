import React, { useEffect, useState } from 'react';
import DashboardLayout from '../../layouts/DashboardLayout';
import { getStudentJobs, applyToStudentJob, getStudentApplications } from '../../api/student';

export default function JobsPage() {
  const [jobs, setJobs] = useState([]);
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [busyJobId, setBusyJobId] = useState(null);

  const loadData = async () => {
    try {
      const [jobsData, applicationsData] = await Promise.all([getStudentJobs(), getStudentApplications()]);
      setJobs(jobsData);
      setApplications(applicationsData);
    } catch (err) {
      setError(err?.response?.data?.detail || 'Unable to load jobs.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleApply = async (jobId) => {
    setBusyJobId(jobId);
    try {
      await applyToStudentJob(jobId);
      await loadData();
    } catch (err) {
      setError(err?.response?.data?.detail || 'Unable to submit application.');
    } finally {
      setBusyJobId(null);
    }
  };

  const appliedJobIds = new Set(applications.map((application) => application.job_id));

  return (
    <DashboardLayout title="Jobs" role="STUDENT" headingLevel={2}>
      <div className="space-y-6">
        <section className="panel p-6">
          <div className="flex flex-col gap-2 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <p className="kicker">Opportunities</p>
              <h2 className="section-title">Explore active roles and apply in one step</h2>
              <p className="mt-1 body-copy">Browse live openings from recruiting partners and submit applications directly from your workspace.</p>
            </div>
            <div className="metric-pill">{applications.length} applications</div>
          </div>

          {loading ? (
            <div className="mt-6 space-y-3">
              {[1, 2, 3].map((item) => <div key={item} className="h-24 animate-pulse rounded-[24px] bg-[var(--surface-elevated)]" />)}
            </div>
          ) : error ? (
            <p className="mt-6 rounded-[24px] border border-red-200 bg-red-50 p-3 text-sm text-red-600">{error}</p>
          ) : jobs.length === 0 ? (
            <p className="mt-6 body-copy">No active jobs are available right now.</p>
          ) : (
            <div className="mt-6 grid gap-4">
              {jobs.map((job) => {
                const applied = appliedJobIds.has(job.id);
                return (
                  <div key={job.id} className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-5">
                    <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                      <div>
                        <p className="text-sm font-semibold text-[var(--brand-primary)]">{job.company}</p>
                        <h3 className="mt-1 text-lg font-semibold text-[var(--text-primary)]">{job.title}</h3>
                        <p className="mt-1 text-sm text-[var(--text-secondary)]">{job.location} • {job.seniority_level}</p>
                        <p className="mt-3 body-copy">{job.description}</p>
                        {job.requirements?.length > 0 && (
                          <ul className="mt-3 list-disc space-y-1 pl-5 text-sm text-[var(--text-secondary)]">
                            {job.requirements.map((requirement) => <li key={requirement}>{requirement}</li>)}
                          </ul>
                        )}
                      </div>
                      <button className="btn-primary" disabled={busyJobId === job.id || applied} onClick={() => handleApply(job.id)}>
                        {busyJobId === job.id ? 'Applying…' : applied ? 'Applied' : 'Apply now'}
                      </button>
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
