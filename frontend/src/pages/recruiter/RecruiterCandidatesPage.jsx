import React, { useEffect, useMemo, useState } from 'react';
import DashboardLayout from '../../layouts/DashboardLayout';
import LoadingState from '../../components/LoadingState';
import RecruiterEmptyState from '../../components/RecruiterEmptyState';
import { listRecruiterCandidates } from '../../api/recruiter';
import { useRecruiterWorkflow } from '../../context/RecruiterWorkflowContext';

export default function RecruiterCandidatesPage() {
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filters, setFilters] = useState({ query: '', readiness: '', fit: '' });
  const { setSelectedCandidate } = useRecruiterWorkflow();

  const loadCandidates = async (activeFilters = filters) => {
    setLoading(true);
    try {
      const data = await listRecruiterCandidates({ query: activeFilters.query });
      let filtered = data;
      if (activeFilters.readiness) {
        filtered = filtered.filter((candidate) => candidate.readiness_label?.toLowerCase() === activeFilters.readiness.toLowerCase());
      }
      if (activeFilters.fit) {
        filtered = filtered.filter((candidate) => {
          const score = candidate.fit_score ?? 0;
          if (activeFilters.fit === 'high') return score >= 70;
          if (activeFilters.fit === 'medium') return score >= 40 && score < 70;
          return score < 40;
        });
      }
      setCandidates(filtered);
      setError('');
    } catch (err) {
      setError(err?.response?.data?.detail || 'Unable to load candidates.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCandidates();
  }, []);

  const stats = useMemo(() => ({
    total: candidates.length,
    bestFit: candidates.filter((candidate) => candidate.is_best_fit).length,
  }), [candidates]);

  return (
    <DashboardLayout title="Candidates" role="RECRUITER">
      <div className="space-y-6">
        {error ? <div className="rounded-[24px] border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">{error}</div> : null}
        <section className="panel p-6">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <p className="kicker">Talent database</p>
              <h2 className="section-title">Professional candidate profiles</h2>
            </div>
            <div className="flex gap-2">
              <span className="metric-pill">{stats.total} visible</span>
              <span className="metric-pill">{stats.bestFit} best fit</span>
            </div>
          </div>

          <div className="mt-6 grid gap-3 md:grid-cols-3">
            <input className="rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm" placeholder="Search by name or email" value={filters.query} onChange={(e) => { const next = { ...filters, query: e.target.value }; setFilters(next); loadCandidates(next); }} />
            <select className="rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm" value={filters.readiness} onChange={(e) => { const next = { ...filters, readiness: e.target.value }; setFilters(next); loadCandidates(next); }}>
              <option value="">Readiness</option><option value="ready">Ready</option><option value="developing">Developing</option><option value="emerging">Emerging</option>
            </select>
            <select className="rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm" value={filters.fit} onChange={(e) => { const next = { ...filters, fit: e.target.value }; setFilters(next); loadCandidates(next); }}>
              <option value="">Fit level</option><option value="high">High</option><option value="medium">Medium</option><option value="low">Low</option>
            </select>
          </div>

          {loading ? <LoadingState /> : candidates.length === 0 ? <div className="mt-6"><RecruiterEmptyState title="No candidates matched your filters" description="Adjust the search or invite more talent into the pipeline." /></div> : <div className="mt-6 grid gap-4 xl:grid-cols-2">{candidates.map((candidate) => (
            <div key={candidate.id} className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-5">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="text-lg font-semibold text-[var(--text-primary)]">{candidate.full_name}</p>
                  <p className="mt-1 text-sm text-[var(--text-secondary)]">{candidate.email}</p>
                </div>
                {candidate.is_best_fit ? <span className="rounded-full bg-emerald-100 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-emerald-700">Best fit</span> : null}
              </div>
              <div className="mt-4 flex flex-wrap gap-2">
                <span className="rounded-full bg-[var(--surface)] px-3 py-1 text-xs font-semibold text-[var(--text-secondary)]">Fit {candidate.fit_score?.toFixed?.(0) ?? 'N/A'}</span>
                <span className="rounded-full bg-[var(--surface)] px-3 py-1 text-xs font-semibold text-[var(--text-secondary)]">Readiness {candidate.readiness_label || 'Pending'}</span>
              </div>
              <div className="mt-4 flex flex-wrap gap-2">
                <button className="btn-primary" onClick={() => setSelectedCandidate(candidate)}>Shortlist</button>
                <button className="btn-secondary" onClick={() => setSelectedCandidate(candidate)}>Invite</button>
              </div>
            </div>
          ))}</div>}
        </section>
      </div>
    </DashboardLayout>
  );
}
