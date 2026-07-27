import React, { useEffect, useState } from 'react';
import DashboardLayout from '../../layouts/DashboardLayout';
import LoadingState from '../../components/LoadingState';
import RecruiterEmptyState from '../../components/RecruiterEmptyState';
import { listRecruiterShortlisted, addRecruiterShortlist, removeRecruiterShortlist, listRecruiterJobs, listRecruiterCandidates } from '../../api/recruiter';

export default function RecruiterShortlistedPage() {
  const [shortlisted, setShortlisted] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [form, setForm] = useState({ candidate_id: '', job_id: '', rating: '', notes: '' });

  const loadData = async () => {
    setLoading(true);
    try {
      const [shortData, jobsData, candidatesData] = await Promise.all([
        listRecruiterShortlisted(),
        listRecruiterJobs({ active_only: true }),
        listRecruiterCandidates(),
      ]);
      setShortlisted(shortData);
      setJobs(jobsData);
      setCandidates(candidatesData);
      setError('');
    } catch (err) {
      setError(err?.response?.data?.detail || 'Unable to load shortlist.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleAdd = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await addRecruiterShortlist({
        ...form,
        rating: form.rating ? Number(form.rating) : null,
      });
      setForm({ candidate_id: '', job_id: '', rating: '', notes: '' });
      await loadData();
    } catch (err) {
      setError(err?.response?.data?.detail || 'Unable to add to shortlist.');
    } finally {
      setSaving(false);
    }
  };

  const handleRemove = async (id) => {
    try {
      await removeRecruiterShortlist(id);
      await loadData();
    } catch (err) {
      setError(err?.response?.data?.detail || 'Unable to remove from shortlist.');
    }
  };

  return (
    <DashboardLayout title="Shortlisted" role="RECRUITER">
      <div className="space-y-6">
        {error ? <div className="rounded-[24px] border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">{error}</div> : null}
        <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
          <section className="panel p-6">
            <div>
              <p className="kicker">Shortlist workflow</p>
              <h2 className="section-title">Candidate shortlist</h2>
            </div>
            {loading ? <LoadingState /> : shortlisted.length === 0 ? <div className="mt-6"><RecruiterEmptyState title="No candidates shortlisted" description="Add candidates from the talent database to start building your shortlist." /></div> : <div className="mt-6 space-y-4">{shortlisted.map((candidate) => (
              <div key={candidate.id} className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-5">
                <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
                  <div>
                    <p className="text-lg font-semibold text-[var(--text-primary)]">{candidate.candidate_name}</p>
                    <p className="mt-1 text-sm text-[var(--text-secondary)]">{candidate.job_title}</p>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {candidate.rating != null && <span className="rounded-full bg-[var(--surface)] px-3 py-1 text-xs font-semibold text-[var(--text-secondary)]">Rating {candidate.rating}</span>}
                    <button className="btn-secondary" onClick={() => handleRemove(candidate.id)}>Remove</button>
                  </div>
                </div>
                {candidate.notes && <p className="mt-3 text-sm text-[var(--text-secondary)]">{candidate.notes}</p>}
              </div>
            ))}</div>}
          </section>

          <section className="panel p-6">
            <div>
              <p className="kicker">Add candidate</p>
              <h2 className="section-title">Shortlist a candidate</h2>
            </div>
            <form className="mt-6 space-y-4" onSubmit={handleAdd}>
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
              <div><label className="block text-sm font-medium">Rating (0-5)</label><input type="number" step="0.1" min="0" max="5" className="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm" value={form.rating} onChange={(e) => setForm({ ...form, rating: e.target.value })} /></div>
              <div><label className="block text-sm font-medium">Notes</label><textarea className="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm" rows={3} value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} /></div>
              <button type="submit" className="btn-primary w-full" disabled={saving}>{saving ? 'Adding...' : 'Add to Shortlist'}</button>
            </form>
          </section>
        </div>
      </div>
    </DashboardLayout>
  );
}

