import React, { useEffect, useMemo, useState } from 'react';
import DashboardLayout from '../../layouts/DashboardLayout';
import LoadingState from '../../components/LoadingState';
import RecruiterEmptyState from '../../components/RecruiterEmptyState';
import { rankRecruiterCandidates } from '../../api/recruiter';

export default function RecruiterMatchingPage() {
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const load = async () => {
      try {
        const data = await rankRecruiterCandidates(20);
        setCandidates(data);
        setError('');
      } catch (err) {
        setError(err?.response?.data?.detail || 'Unable to compute matches.');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const rankedCandidates = useMemo(() => [...candidates].sort((a, b) => (b.fit_score || 0) - (a.fit_score || 0)), [candidates]);

  return (
    <DashboardLayout title="AI Matching" role="RECRUITER">
      <div className="space-y-6">
        {error ? <div className="rounded-[24px] border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">{error}</div> : null}
        <section className="panel p-6">
          <div>
            <p className="kicker">Matching engine</p>
            <h2 className="section-title">AI candidate recommendations</h2>
            <p className="mt-2 body-copy">Candidates are ranked from available talent signals such as readiness, profile strength, project alignment, and fit score.</p>
          </div>

          {loading ? <LoadingState /> : rankedCandidates.length === 0 ? <div className="mt-6"><RecruiterEmptyState title="No matching data available" description="Populate candidate profiles to generate recommendations." /></div> : <div className="mt-6 space-y-4">{rankedCandidates.map((candidate, index) => (
            <div key={candidate.id} className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-5">
              <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="rounded-full bg-[var(--surface)] px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-[var(--text-secondary)]">Rank #{candidate.rank || index + 1}</span>
                    {candidate.is_best_fit ? <span className="rounded-full bg-emerald-100 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-emerald-700">Top match</span> : null}
                  </div>
                  <p className="mt-3 text-lg font-semibold text-[var(--text-primary)]">{candidate.full_name}</p>
                  <p className="mt-1 text-sm text-[var(--text-secondary)]">{candidate.email}</p>
                  <p className="mt-2 text-sm text-[var(--text-secondary)]">Best role: {candidate.top_role_match}</p>
                </div>
                <div className="rounded-2xl bg-[var(--surface)] p-4">
                  <p className="text-sm font-semibold text-[var(--text-primary)]">Matching %</p>
                  <p className="text-3xl font-semibold text-[var(--text-primary)]">{candidate.fit_score?.toFixed?.(0) ?? 'N/A'}%</p>
                </div>
              </div>
              <div className="mt-4 flex flex-wrap gap-2">
                {candidate.skills?.map((skill) => (
                  <span key={skill} className="rounded-full bg-[var(--surface)] px-3 py-1 text-xs text-[var(--text-secondary)]">{skill}</span>
                ))}
              </div>
              <div className="mt-4 grid gap-3 md:grid-cols-3">
                <div className="rounded-2xl bg-[var(--surface)] p-3 text-sm text-[var(--text-secondary)]">
                  <p className="font-semibold text-[var(--text-primary)]">Readiness</p>
                  <p className="mt-1">{candidate.readiness_label}</p>
                </div>
                <div className="rounded-2xl bg-[var(--surface)] p-3 text-sm text-[var(--text-secondary)]">
                  <p className="font-semibold text-[var(--text-primary)]">Resume</p>
                  <p className="mt-1">{candidate.resume_strength}</p>
                </div>
                <div className="rounded-2xl bg-[var(--surface)] p-3 text-sm text-[var(--text-secondary)]">
                  <p className="font-semibold text-[var(--text-primary)]">Interview</p>
                  <p className="mt-1">{candidate.interview_readiness}</p>
                </div>
              </div>
            </div>
          ))}</div>}
        </section>
      </div>
    </DashboardLayout>
  );
}

