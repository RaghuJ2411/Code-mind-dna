import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import DashboardLayout from '../../layouts/DashboardLayout';
import { getRecruiterJob } from '../../api/recruiter';
import { useRecruiterWorkflow } from '../../context/RecruiterWorkflowContext';

export default function JobDetailPage() {
  const { jobId } = useParams();
  const navigate = useNavigate();
  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { selectedJob, setSelectedJob } = useRecruiterWorkflow();

  useEffect(() => {
    const loadJob = async () => {
      try {
        const response = await getRecruiterJob(jobId);
        setJob(response);
        setSelectedJob(response);
        setError(null);
      } catch (err) {
        setError(err?.response?.data?.detail || 'Unable to load job posting.');
      } finally {
        setLoading(false);
      }
    };

    loadJob();
  }, [jobId]);

  return (
    <DashboardLayout title="Job Intelligence" role="RECRUITER">
      <div className="space-y-6">
        <button className="rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] px-4 py-2 text-sm font-semibold text-[var(--text-primary)]" onClick={() => navigate('/recruiter/dashboard')}>
          Back to dashboard
        </button>
        {loading ? (
          <div className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface)] p-6 text-sm text-[var(--text-secondary)]">Loading job details...</div>
        ) : error ? (
          <div className="rounded-[24px] border border-rose-200 bg-rose-50 p-6 text-sm text-rose-700">{error}</div>
        ) : (
          <>
            <section className="panel p-6">
              <p className="kicker">Role workspace</p>
              <h2 className="page-title">{job.title}</h2>
              <p className="page-subtitle">{job.company} · {job.location}</p>
              {selectedJob ? <p className="mt-3 text-sm text-sky-700">Active workflow context: {selectedJob.title}</p> : null}
              <div className="mt-4 flex flex-wrap gap-2">
                <span className="rounded-full bg-[var(--surface-elevated)] px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-[var(--text-secondary)]">{job.seniority_level}</span>
                <span className="rounded-full bg-[var(--surface-elevated)] px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-[var(--text-secondary)]">{job.is_active ? 'Active' : 'Inactive'}</span>
              </div>
              <p className="mt-5 text-sm leading-7 text-[var(--text-secondary)]">{job.description}</p>
            </section>
            <section className="panel p-6">
              <p className="kicker">Requirements</p>
              <h3 className="section-title">What this role needs</h3>
              <ul className="mt-4 list-disc space-y-2 pl-5 text-sm text-[var(--text-secondary)]">
                {job.requirements.map((req, index) => <li key={index}>{req}</li>)}
              </ul>
            </section>
          </>
        )}
      </div>
    </DashboardLayout>
  );
}
