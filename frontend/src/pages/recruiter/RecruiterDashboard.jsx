import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import DashboardLayout from '../../layouts/DashboardLayout';
import ActivityFeed from '../../components/ActivityFeed';
import RoleOnboardingChecklist from '../../components/RoleOnboardingChecklist';
import { getRecruiterDashboard, listRecruiterJobs, createRecruiterJob, listRecruiterCandidates } from '../../api/recruiter';
import { useRecruiterWorkflow } from '../../context/RecruiterWorkflowContext';

function MetricCard({ label, value, caption, tone = 'default' }) {
  const toneClass = {
    default: 'border-[var(--border-subtle)] bg-[var(--surface-elevated)]',
    success: 'border-emerald-200 bg-emerald-50',
    info: 'border-sky-200 bg-sky-50',
    warning: 'border-amber-200 bg-amber-50',
  }[tone];

  return (
    <div className={`rounded-[24px] border p-4 ${toneClass}`}>
      <p className="text-sm text-[var(--text-muted)]">{label}</p>
      <p className="mt-2 text-2xl font-semibold text-[var(--text-primary)]">{value}</p>
      <p className="mt-1 text-sm text-[var(--text-secondary)]">{caption}</p>
    </div>
  );
}

export default function RecruiterDashboard() {
  const navigate = useNavigate();
  const [dashboard, setDashboard] = useState(null);
  const [jobs, setJobs] = useState([]);
  const [candidates, setCandidates] = useState([]);
  const [form, setForm] = useState({ title: '', company: '', location: '', seniority_level: 'ENTRY', description: '', requirements: '' });
  const [filters, setFilters] = useState({ query: '', seniority_level: '', location: '', company: '', candidate_query: '', active_only: true });
  const [debouncedFilters, setDebouncedFilters] = useState(filters);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [feedback, setFeedback] = useState('');
  const { setSelectedJob, setSelectedCandidate } = useRecruiterWorkflow();

  const loadDashboard = async (activeFilters = debouncedFilters) => {
    setLoading(true);
    try {
      const [dashboardData, jobsData, candidatesData] = await Promise.all([
        getRecruiterDashboard(),
        listRecruiterJobs(activeFilters),
        listRecruiterCandidates({ query: activeFilters.candidate_query }),
      ]);
      setDashboard(dashboardData);
      setJobs(jobsData);
      setCandidates(candidatesData);
      setError(null);
    } catch (err) {
      setError(err?.response?.data?.detail || 'Unable to load recruiter data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedFilters(filters);
    }, 300);
    return () => clearTimeout(timer);
  }, [filters]);

  useEffect(() => {
    loadDashboard(debouncedFilters);
  }, [debouncedFilters]);

  const handleChange = (key, value) => {
    setForm((current) => ({ ...current, [key]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setSaving(true);
    try {
      await createRecruiterJob({
        ...form,
        requirements: form.requirements.split(',').map((item) => item.trim()).filter(Boolean),
      });
      setForm({ title: '', company: '', location: '', seniority_level: 'ENTRY', description: '', requirements: '' });
      await loadDashboard();
      setError(null);
      setFeedback('Job posted successfully. Your hiring pipeline has been updated.');
    } catch (err) {
      setError(err?.response?.data?.detail || 'Unable to save job posting.');
    } finally {
      setSaving(false);
    }
  };

  const updateFilter = (key, value) => {
    setFilters((current) => ({ ...current, [key]: value }));
  };

  const clearFilters = () => {
    setFilters({ query: '', seniority_level: '', location: '', company: '', candidate_query: '', active_only: true });
  };

  const onboardingItems = useMemo(() => [
    {
      label: 'Post a new role',
      description: 'Launch a hiring opening so the pipeline has a clear next move.',
      completed: jobs.length > 0 || Boolean(dashboard?.total_open_jobs),
      href: '/recruiter/dashboard',
    },
    {
      label: 'Review the strongest signal',
      description: 'Inspect the best-fit candidate surfaced by the platform.',
      completed: Boolean(dashboard?.best_fit_candidate) || candidates.length > 0,
      href: '/recruiter/dashboard',
    },
    {
      label: 'Open a candidate view',
      description: 'Dive into a student profile to understand the fit and next step.',
      completed: candidates.length > 0,
      href: '/recruiter/dashboard',
    },
    {
      label: 'Create a follow-up action',
      description: 'Turn the candidate evidence into a clear decision or outreach step.',
      completed: jobs.length > 0,
      href: '/recruiter/dashboard',
    },
  ], [candidates.length, dashboard?.best_fit_candidate, dashboard?.total_open_jobs, jobs.length]);

  const summaryMetrics = useMemo(() => ({
    openJobs: dashboard?.total_open_jobs ?? 0,
    candidates: dashboard?.total_candidates ?? 0,
    bestFit: dashboard?.best_fit_candidate ? 1 : 0,
    highConfidence: candidates.filter((candidate) => candidate.fit_score != null && candidate.fit_score >= 70).length,
  }), [candidates, dashboard]);

  return (
    <DashboardLayout title="Recruiter Dashboard" role="RECRUITER">
      <div className="space-y-6">
        {feedback ? (
          <div className="rounded-[24px] border border-emerald-200 bg-emerald-50 p-4 text-sm font-medium text-emerald-700">
            {feedback}
          </div>
        ) : null}

        <RoleOnboardingChecklist
          title="Your hiring launchpad"
          description="Move from a fresh opening to a confident next action without losing momentum."
          items={onboardingItems}
        />

        <section className="panel p-6">
          <div className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <p className="kicker">Hiring command center</p>
              <h2 className="page-title">Turn hiring needs into confident actions.</h2>
              <p className="page-subtitle">Review the most urgent openings, the strongest candidate signals, and the next decision that matters most.</p>
            </div>
            <div className="metric-pill">Evidence-led hiring</div>
          </div>

          <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <MetricCard label="Active jobs" value={summaryMetrics.openJobs} caption="Open roles currently managed" />
            <MetricCard label="Candidate pool" value={summaryMetrics.candidates} caption="Students available for review" tone="info" />
            <MetricCard label="Best-fit ready" value={summaryMetrics.bestFit} caption="Top recommended candidate surfaced" tone="success" />
            <MetricCard label="High-confidence matches" value={summaryMetrics.highConfidence} caption="Candidates above 70 fit" tone="warning" />
          </div>
        </section>

        <section className="panel p-6">
          <div className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <p className="kicker">Pending hiring actions</p>
              <h2 className="section-title">Your next best action</h2>
              <p className="mt-2 body-copy">Focus on the role or candidate that needs the next decision today.</p>
            </div>
            <div className="metric-pill">Priority: action</div>
          </div>
          <div className="mt-6 grid gap-4 xl:grid-cols-[1.1fr_0.9fr]">
            <div className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-5">
              <p className="text-sm font-semibold text-[var(--text-primary)]">Open role to review</p>
              {dashboard?.top_open_job ? (
                <>
                  <p className="mt-3 text-lg font-semibold text-[var(--text-primary)]">{dashboard.top_open_job.title}</p>
                  <p className="mt-1 text-sm text-[var(--text-secondary)]">{dashboard.top_open_job.company} · {dashboard.top_open_job.location}</p>
                  <p className="mt-3 text-sm text-[var(--text-secondary)]">{dashboard.top_open_job.description}</p>
                  <button type="button" aria-label={`Open role workspace ${dashboard.top_open_job.title}`} onClick={() => {
                    setSelectedJob(dashboard.top_open_job);
                    navigate(`/recruiter/jobs/${dashboard.top_open_job.id}`);
                  }} className="btn-primary mt-4">Open role workspace</button>
                </>
              ) : (
                <p className="mt-3 text-sm text-[var(--text-secondary)]">No open role is available yet. Create one to start shaping the pipeline.</p>
              )}
            </div>
            <div className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-5">
              <p className="text-sm font-semibold text-[var(--text-primary)]">Best-fit candidate</p>
              {dashboard?.best_fit_candidate ? (
                <>
                  <p className="mt-3 text-lg font-semibold text-[var(--text-primary)]">{dashboard.best_fit_candidate.full_name}</p>
                  <p className="mt-1 text-sm text-[var(--text-secondary)]">{dashboard.best_fit_candidate.email}</p>
                  <p className="mt-3 text-sm text-[var(--text-secondary)]">Match confidence: {dashboard.best_fit_candidate.confidence_label || 'Pending'}</p>
                  <button type="button" onClick={() => {
                    setSelectedCandidate(dashboard.best_fit_candidate);
                    navigate(`/recruiter/candidates/${dashboard.best_fit_candidate.id}`);
                  }} className="btn-secondary mt-4">Review candidate</button>
                </>
              ) : (
                <p className="mt-3 text-sm text-[var(--text-secondary)]">No candidate match has been surfaced yet. Keep the pipeline active and revisit later.</p>
              )}
            </div>
          </div>
        </section>

        <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
          <section className="panel p-6">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
              <div>
                <p className="kicker">Jobs needing attention</p>
                <h2 className="section-title">Hiring pipeline at a glance</h2>
                <p className="mt-2 body-copy">Review roles, assess your current demand, and jump directly into the strongest opportunities.</p>
              </div>
            </div>
            {loading ? (
              <div className="mt-6 grid gap-3">
                <div className="h-20 animate-pulse rounded-[24px] bg-[var(--surface-elevated)]" />
                <div className="h-20 animate-pulse rounded-[24px] bg-[var(--surface-elevated)]" />
              </div>
            ) : (
              <div className="mt-6 space-y-4">
                {dashboard?.top_open_job ? (
                  <button className="w-full rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-5 text-left" onClick={() => {
                    setSelectedJob(dashboard.top_open_job);
                    navigate(`/recruiter/jobs/${dashboard.top_open_job.id}`);
                  }}>
                    <div className="flex items-center justify-between gap-3">
                      <div>
                        <p className="text-xs font-semibold uppercase tracking-[0.24em] text-[var(--text-muted)]">Top open role</p>
                        <p className="mt-1 text-lg font-semibold text-[var(--text-primary)]">{dashboard.top_open_job.title}</p>
                        <p className="text-sm text-[var(--text-secondary)]">{dashboard.top_open_job.company} · {dashboard.top_open_job.location}</p>
                      </div>
                      <span className="rounded-full bg-[var(--surface-interactive)] px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-[var(--text-secondary)]">{dashboard.top_open_job.seniority_level}</span>
                    </div>
                    <p className="mt-3 text-sm text-[var(--text-secondary)]">{dashboard.top_open_job.description}</p>
                  </button>
                ) : null}
                {jobs.map((job) => (
                  <button key={job.id} aria-label={`Open role card ${job.title}`} className="w-full rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface)] p-4 text-left" onClick={() => {
                    setSelectedJob(job);
                    navigate(`/recruiter/jobs/${job.id}`);
                  }}>
                    <div className="flex items-center justify-between gap-3">
                      <div>
                        <p className="text-base font-semibold text-[var(--text-primary)]">{job.title}</p>
                        <p className="text-sm text-[var(--text-secondary)]">{job.company} · {job.location}</p>
                      </div>
                      <span className="rounded-full bg-[var(--surface-elevated)] px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-[var(--text-secondary)]">{job.seniority_level}</span>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </section>

          <section className="panel p-6">
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="kicker">Create a role</p>
                <h2 className="section-title">Post a job</h2>
                <p className="mt-2 body-copy">Create a new opportunity for your talent pipeline.</p>
              </div>
            </div>
            <form className="mt-6 space-y-4" onSubmit={handleSubmit}>
              <div>
                <label className="block text-sm font-medium text-slate-700">Title</label>
                <input value={form.title} onChange={(e) => handleChange('title', e.target.value)} className="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm" />
              </div>
              <div className="grid gap-4 sm:grid-cols-2">
                <div><label className="block text-sm font-medium text-slate-700">Company</label><input value={form.company} onChange={(e) => handleChange('company', e.target.value)} className="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm" /></div>
                <div><label className="block text-sm font-medium text-slate-700">Location</label><input value={form.location} onChange={(e) => handleChange('location', e.target.value)} className="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm" /></div>
              </div>
              <div><label className="block text-sm font-medium text-slate-700">Seniority</label><select value={form.seniority_level} onChange={(e) => handleChange('seniority_level', e.target.value)} className="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm"><option value="ENTRY">Entry</option><option value="MID">Mid</option><option value="SENIOR">Senior</option><option value="LEAD">Lead</option></select></div>
              <div><label className="block text-sm font-medium text-slate-700">Description</label><textarea value={form.description} onChange={(e) => handleChange('description', e.target.value)} className="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm" rows={4} /></div>
              <div><label className="block text-sm font-medium text-slate-700">Requirements (comma separated)</label><input value={form.requirements} onChange={(e) => handleChange('requirements', e.target.value)} className="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm" /></div>
              {error ? <p className="text-sm text-rose-600">{error}</p> : null}
              <button type="submit" className="btn-primary w-full" disabled={saving}>{saving ? 'Saving…' : 'Create Job'}</button>
            </form>
          </section>
        </div>

        <section className="panel p-6">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <p className="kicker">Talent discovery</p>
              <h2 className="section-title">Strong candidate matches</h2>
              <p className="mt-2 body-copy">Search candidate profiles and review the evidence behind each recommendation.</p>
            </div>
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
              <input value={filters.candidate_query ?? ''} onChange={(e) => updateFilter('candidate_query', e.target.value)} placeholder="Search candidates" className="rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm" />
              <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-slate-600">{candidates.length} filtered</span>
            </div>
          </div>

          {dashboard?.best_fit_candidate ? (
            <div className="mt-6 rounded-[24px] border border-emerald-200 bg-emerald-50 p-5">
              <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                <div>
                  <p className="text-xs uppercase tracking-[0.24em] text-emerald-700">Top recommendation</p>
                  <p className="mt-2 text-lg font-semibold text-slate-900">{dashboard.best_fit_candidate.full_name}</p>
                  <p className="text-sm text-slate-700">{dashboard.best_fit_candidate.email}</p>
                </div>
                <div className="flex flex-wrap gap-2">
                  <span className="rounded-full bg-emerald-100 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-emerald-700">Best fit</span>
                  <span className="rounded-full bg-white px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-slate-700">Match {dashboard.best_fit_candidate.fit_score?.toFixed?.(0) ?? 'N/A'}</span>
                  <span className="rounded-full bg-white px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-slate-700">Confidence {dashboard.best_fit_candidate.confidence_label || 'Pending'}</span>
                </div>
              </div>
              <div className="mt-4 grid gap-3 sm:grid-cols-3">
                <div className="rounded-2xl bg-white p-3 text-sm text-slate-700"><p className="font-semibold text-slate-900">Readiness</p><p className="mt-1">{dashboard.best_fit_candidate.readiness_label}</p></div>
                <div className="rounded-2xl bg-white p-3 text-sm text-slate-700"><p className="font-semibold text-slate-900">Resume strength</p><p className="mt-1">{dashboard.best_fit_candidate.resume_strength}</p></div>
                <div className="rounded-2xl bg-white p-3 text-sm text-slate-700"><p className="font-semibold text-slate-900">Interview readiness</p><p className="mt-1">{dashboard.best_fit_candidate.interview_readiness}</p></div>
              </div>
              <div className="mt-4 flex flex-wrap gap-2">
                <button type="button" onClick={() => navigate(`/recruiter/candidates/${dashboard.best_fit_candidate.id}`)} className="btn-primary">View candidate profile</button>
              </div>
            </div>
          ) : null}

          <div className="mt-6 grid gap-4 lg:grid-cols-2">
            {candidates.length === 0 ? (
              <div className="rounded-[24px] border border-dashed border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-6 text-sm text-[var(--text-secondary)] lg:col-span-2">No candidate profiles available yet.</div>
            ) : (
              candidates.map((candidate) => (
                <button key={candidate.id} className="w-full rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-4 text-left" onClick={() => navigate(`/recruiter/candidates/${candidate.id}`)}>
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="text-base font-semibold text-[var(--text-primary)]">{candidate.full_name}</p>
                      <p className="mt-1 text-sm text-[var(--text-secondary)]">{candidate.email}</p>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {candidate.is_best_fit ? <span className="rounded-full bg-emerald-100 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-emerald-700">Best fit</span> : null}
                      <span className="rounded-full bg-[var(--surface-interactive)] px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-[var(--text-secondary)]">Match {candidate.fit_score?.toFixed?.(0) ?? 'N/A'}</span>
                    </div>
                  </div>
                  <div className="mt-4 flex flex-wrap gap-2">
                    <span className="rounded-full bg-[var(--surface)] px-3 py-1 text-xs font-semibold text-[var(--text-secondary)]">Confidence {candidate.confidence_label || 'Pending'}</span>
                    <span className="rounded-full bg-[var(--surface)] px-3 py-1 text-xs font-semibold text-[var(--text-secondary)]">Readiness {candidate.readiness_label || 'Pending'}</span>
                  </div>
                </button>
              ))
            )}
          </div>
        </section>

        <ActivityFeed />
      </div>
    </DashboardLayout>
  );
}
