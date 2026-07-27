import React, { useEffect, useState } from 'react';
import DashboardLayout from '../../layouts/DashboardLayout';
import LoadingState from '../../components/LoadingState';
import RecruiterEmptyState from '../../components/RecruiterEmptyState';
import { listRecruiterInterviews, createRecruiterInterview, listRecruiterJobs, listRecruiterCandidates } from '../../api/recruiter';

export default function RecruiterInterviewsPage() {
  const [interviews, setInterviews] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [form, setForm] = useState({ candidate_id: '', job_id: '', interviewer: '', slot: '', mode: 'Zoom', link: '', notes: '' });

  const loadData = async () => {
    setLoading(true);
    try {
      const [interviewsData, jobsData, candidatesData] = await Promise.all([
        listRecruiterInterviews(),
        listRecruiterJobs({ active_only: true }),
        listRecruiterCandidates(),
      ]);
      setInterviews(interviewsData);
      setJobs(jobsData);
      setCandidates(candidatesData);
      setError('');
    } catch (err) {
      setError(err?.response?.data?.detail || 'Unable to load interviews.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await createRecruiterInterview(form);
      setForm({ candidate_id: '', job_id: '', interviewer: '', slot: '', mode: 'Zoom', link: '', notes: '' });
      await loadData();
    } catch (err) {
      setError(err?.response?.data?.detail || 'Unable to create interview.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <DashboardLayout title="Interviews" role="RECRUITER">
      <div className="space-y-6">
        {error ? <div className="rounded-[24px] border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">{error}</div> : null}
        <section className="panel p-6">
          <div>
            <p className="kicker">Interview scheduler</p>
            <h2 className="section-title">Schedule interviews</h2>
          </div>
          <form className="mt-6 grid gap-4 md:grid-cols-2" onSubmit={handleSubmit}>
            <div>
              <label className="block text-sm font-medium">Candidate</label>
              <select className="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm" value={form.candidate_id} onChange={(e) => setForm({ ...form, candidate_id: e.target.value })} required>
                <option value="">Select candidate</option>
                {candidates.map((c) => <option key={c.id} value={c.id}>{c.full_name}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium">Job</label>
              <select className="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm" value={form.job_id} onChange={(e) => setForm({ ...form, job_id: e.target.value })} required>
                <option value="">Select job</option>
                {jobs.map((j) => <option key={j.id} value={j.id}>{j.title}</option>)}
              </select>
            </div>
            <div><label className="block text-sm font-medium">Interviewer</label><input className="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm" value={form.interviewer} onChange={(e) => setForm({ ...form, interviewer: e.target.value })} required /></div>
            <div><label className="block text-sm font-medium">Date/Time</label><input className="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm" value={form.slot} onChange={(e) => setForm({ ...form, slot: e.target.value })} placeholder="2026-07-22 10:00" required /></div>
            <div><label className="block text-sm font-medium">Mode</label><select className="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm" value={form.mode} onChange={(e) => setForm({ ...form, mode: e.target.value })}><option>Zoom</option><option>Teams</option><option>Google Meet</option><option>In-person</option></select></div>
            <div><label className="block text-sm font-medium">Link</label><input className="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm" value={form.link} onChange={(e) => setForm({ ...form, link: e.target.value })} /></div>
            <div className="md:col-span-2"><label className="block text-sm font-medium">Notes</label><textarea className="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm" rows={2} value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} /></div>
            <div className="md:col-span-2"><button type="submit" className="btn-primary" disabled={saving}>{saving ? 'Scheduling...' : 'Schedule Interview'}</button></div>
          </form>
        </section>

        <section className="panel p-6">
          <p className="kicker">Scheduled</p>
          <h2 className="section-title">Upcoming interviews</h2>
          {loading ? <LoadingState /> : interviews.length === 0 ? <div className="mt-6"><RecruiterEmptyState title="No interviews scheduled" description="Schedule an interview to get started." /></div> : <div className="mt-6 space-y-4">{interviews.map((interview) => (
            <div key={interview.id} className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-5">
              <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
                <div>
                  <p className="text-lg font-semibold text-[var(--text-primary)]">{interview.candidate_name}</p>
                  <p className="mt-1 text-sm text-[var(--text-secondary)]">{interview.job_title} • Interviewer: {interview.interviewer}</p>
                </div>
                <div className="flex flex-wrap gap-2">
                  <span className="rounded-full bg-[var(--surface)] px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-[var(--text-secondary)]">{interview.mode}</span>
                  <span className="rounded-full bg-[var(--surface)] px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-[var(--text-secondary)]">{interview.status}</span>
                  {interview.link && <a className="rounded-full bg-[var(--surface)] px-3 py-1 text-xs font-semibold text-[var(--text-secondary)]" href={interview.link} target="_blank" rel="noreferrer">Open link</a>}
                </div>
              </div>
              <p className="mt-3 text-sm text-[var(--text-secondary)]">{interview.slot}</p>
            </div>
          ))}</div>}
        </section>
      </div>
    </DashboardLayout>
  );
}

