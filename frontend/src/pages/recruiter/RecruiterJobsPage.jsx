import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import DashboardLayout from '../../layouts/DashboardLayout';
import LoadingState from '../../components/LoadingState';
import RecruiterEmptyState from '../../components/RecruiterEmptyState';
import { listRecruiterJobs, createRecruiterJob } from '../../api/recruiter';
import { useRecruiterWorkflow } from '../../context/RecruiterWorkflowContext';

const initialForm = {
  title: '',
  company: '',
  location: '',
  seniority_level: 'ENTRY',
  description: '',
  requirements: '',
  is_active: true,
};

export default function RecruiterJobsPage() {
  const navigate = useNavigate();
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [filters, setFilters] = useState({ query: '', seniority_level: '', location: '', company: '', active_only: true });
  const [form, setForm] = useState(initialForm);
  const { selectedJob, setSelectedJob } = useRecruiterWorkflow();

  const loadJobs = async (activeFilters = filters) => {
    setLoading(true);
    try {
      const data = await listRecruiterJobs(activeFilters);
      setJobs(data);
      setError('');
    } catch (err) {
      setError(err?.response?.data?.detail || 'Unable to load jobs.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadJobs();
  }, []);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setSaving(true);
    try {
      await createRecruiterJob({
        ...form,
        requirements: form.requirements.split(',').map((item) => item.trim()).filter(Boolean),
      });
      setForm(initialForm);
      setSuccess('Job created successfully.');
      await loadJobs(filters);
    } catch (err) {
      setError(err?.response?.data?.detail || 'Unable to create job.');
    } finally {
      setSaving(false);
    }
  };

  const handleFilterChange = (key, value) => {
    const next = { ...filters, [key]: value };
    setFilters(next);
    loadJobs(next);
  };

  const stats = useMemo(() => ({
    total: jobs.length,
    active: jobs.filter((job) => job.is_active).length,
    archived: jobs.filter((job) => !job.is_active).length,
  }), [jobs]);

  return (
    <DashboardLayout title="Jobs" role="RECRUITER">
      <div className="space-y-6">
        {success ? <div className="rounded-[24px] border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-700">{success}</div> : null}
        {error ? <div className="rounded-[24px] border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">{error}</div> : null}

        <section className="panel p-6">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <p className="kicker">Job operations</p>
              <h2 className="section-title">Create and manage job postings</h2>
            </div>
            <div className="flex gap-2">
              <span className="metric-pill">{stats.total} total</span>
              <span className="metric-pill">{stats.active} active</span>
              <span className="metric-pill">{stats.archived} archived</span>
            </div>
          </div>

          <form className="mt-6 grid gap-4 md:grid-cols-2" onSubmit={handleSubmit}>
            <div><label className="block text-sm font-medium">Title</label><input className="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} required /></div>
            <div><label className="block text-sm font-medium">Company</label><input className="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm" value={form.company} onChange={(e) => setForm({ ...form, company: e.target.value })} required /></div>
            <div><label className="block text-sm font-medium">Location</label><input className="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm" value={form.location} onChange={(e) => setForm({ ...form, location: e.target.value })} required /></div>
            <div><label className="block text-sm font-medium">Seniority</label><select className="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm" value={form.seniority_level} onChange={(e) => setForm({ ...form, seniority_level: e.target.value })}><option value="ENTRY">Entry</option><option value="MID">Mid</option><option value="SENIOR">Senior</option><option value="LEAD">Lead</option></select></div>
            <div className="md:col-span-2"><label className="block text-sm font-medium">Description</label><textarea className="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm" rows={4} value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} required /></div>
            <div className="md:col-span-2"><label className="block text-sm font-medium">Requirements</label><input className="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm" value={form.requirements} onChange={(e) => setForm({ ...form, requirements: e.target.value })} placeholder="Python, SQL, APIs" /></div>
            <div className="md:col-span-2 flex items-center gap-2"><input type="checkbox" checked={form.is_active} onChange={(e) => setForm({ ...form, is_active: e.target.checked })} /><span className="text-sm">Active posting</span></div>
            <div className="md:col-span-2"><button type="submit" className="btn-primary" disabled={saving}>{saving ? 'Saving…' : 'Create Job'}</button></div>
          </form>
        </section>

        <section className="panel p-6">
          <div className="grid gap-3 md:grid-cols-4">
            <input className="rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm" placeholder="Search jobs" value={filters.query} onChange={(e) => handleFilterChange('query', e.target.value)} />
            <input className="rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm" placeholder="Company" value={filters.company} onChange={(e) => handleFilterChange('company', e.target.value)} />
            <input className="rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm" placeholder="Location" value={filters.location} onChange={(e) => handleFilterChange('location', e.target.value)} />
            <select className="rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm" value={filters.seniority_level} onChange={(e) => handleFilterChange('seniority_level', e.target.value)}>
              <option value="">Seniority</option><option value="ENTRY">Entry</option><option value="MID">Mid</option><option value="SENIOR">Senior</option><option value="LEAD">Lead</option>
            </select>
          </div>
          <div className="mt-3 flex items-center gap-2">
            <input type="checkbox" checked={filters.active_only} onChange={(e) => handleFilterChange('active_only', e.target.checked)} />
            <span className="text-sm">Active only</span>
          </div>

          {loading ? <LoadingState /> : jobs.length === 0 ? <div className="mt-6"><RecruiterEmptyState title="No jobs found" description="Create a role to start building your hiring pipeline." /></div> : <div className="mt-6 space-y-4">{jobs.map((job) => (
            <button key={job.id} className="w-full rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-5 text-left" onClick={() => {
              setSelectedJob(job);
              navigate(`/recruiter/jobs/${job.id}`);
            }}>
              <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
                <div>
                  <p className="text-lg font-semibold text-[var(--text-primary)]">{job.title}</p>
                  <p className="text-sm text-[var(--text-secondary)]">{job.company} · {job.location}</p>
                </div>
                <div className="flex flex-wrap gap-2">
                  <span className="rounded-full bg-[var(--surface)] px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-[var(--text-secondary)]">{job.seniority_level}</span>
                  <span className="rounded-full bg-[var(--surface)] px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-[var(--text-secondary)]">{job.is_active ? 'Active' : 'Archived'}</span>
                </div>
              </div>
              <p className="mt-3 text-sm text-[var(--text-secondary)]">{job.description}</p>
            </button>
          ))}</div>}
        </section>
      </div>
    </DashboardLayout>
  );
}
