import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import DashboardLayout from '../../layouts/DashboardLayout';
import WhyThisCandidateMatches from '../../components/WhyThisCandidateMatches';
import { getRecruiterCandidate } from '../../api/recruiter';
import { useRecruiterWorkflow } from '../../context/RecruiterWorkflowContext';

export default function CandidateDetailPage() {
  const { studentId } = useParams();
  const navigate = useNavigate();
  const [candidate, setCandidate] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { selectedCandidate, setSelectedCandidate } = useRecruiterWorkflow();

  useEffect(() => {
    const loadCandidate = async () => {
      try {
        const data = await getRecruiterCandidate(studentId);
        setCandidate(data);
        setSelectedCandidate(data);
        setError(null);
      } catch (err) {
        setError(err?.response?.data?.detail || 'Unable to load candidate.');
      } finally {
        setLoading(false);
      }
    };

    loadCandidate();
  }, [studentId]);

  return (
    <DashboardLayout title="Candidate Intelligence" role="RECRUITER">
      <div className="space-y-6">
        <button className="rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] px-4 py-2 text-sm font-semibold text-[var(--text-primary)]" onClick={() => navigate('/recruiter/dashboard')}>
          Back to dashboard
        </button>

        {loading ? (
          <div className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface)] p-6 text-sm text-[var(--text-secondary)]">Loading candidate profile...</div>
        ) : error ? (
          <div className="rounded-[24px] border border-rose-200 bg-rose-50 p-6 text-sm text-rose-700">{error}</div>
        ) : (
          <>
            <section className="panel p-6">
              <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                <div>
                  <p className="kicker">Candidate intelligence</p>
                  <h2 className="page-title">{candidate.full_name}</h2>
                  <p className="page-subtitle">{candidate.email}</p>
                  {selectedCandidate ? <p className="mt-3 text-sm text-sky-700">Active workflow context: {selectedCandidate.full_name}</p> : null}
                </div>
                <div className="flex flex-wrap gap-2">
                  {candidate.is_best_fit ? <span className="rounded-full bg-emerald-100 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-emerald-700">Best-fit candidate</span> : null}
                  <span className="rounded-full bg-[var(--surface-elevated)] px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-[var(--text-secondary)]">Match {candidate.fit_score?.toFixed?.(0) ?? 'N/A'}</span>
                </div>
              </div>

              <div className="mt-6 grid gap-4 md:grid-cols-4">
                <div className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-4"><p className="text-sm text-[var(--text-muted)]">Readiness</p><p className="mt-2 text-2xl font-semibold text-[var(--text-primary)]">{candidate.readiness_score}</p><p className="mt-1 text-sm text-[var(--text-secondary)]">{candidate.readiness_label}</p></div>
                <div className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-4"><p className="text-sm text-[var(--text-muted)]">Resume strength</p><p className="mt-2 text-2xl font-semibold text-[var(--text-primary)]">{candidate.resume_strength}</p><p className="mt-1 text-sm text-[var(--text-secondary)]">{candidate.project_count} projects • {candidate.resume_entry_count} entries</p></div>
                <div className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-4"><p className="text-sm text-[var(--text-muted)]">Interview readiness</p><p className="mt-2 text-2xl font-semibold text-[var(--text-primary)]">{candidate.interview_readiness}</p><p className="mt-1 text-sm text-[var(--text-secondary)]">Practice sessions: {candidate.interview_session_count}</p></div>
                <div className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-4"><p className="text-sm text-[var(--text-muted)]">Confidence</p><p className="mt-2 text-2xl font-semibold text-[var(--text-primary)]">{candidate.confidence_label}</p><p className="mt-1 text-sm text-[var(--text-secondary)]">Profile status: {candidate.profile_status}</p></div>
              </div>
            </section>

            <div className="grid gap-6 xl:grid-cols-[1.25fr_0.75fr]">
              <section className="panel p-6">
                <p className="kicker">Match overview</p>
                <h3 className="section-title">Evidence-backed match summary</h3>
                <WhyThisCandidateMatches candidate={candidate} />
              </section>

              <section className="panel p-6">
                <p className="kicker">Role relevance</p>
                <h3 className="section-title">Top role matches</h3>
                <div className="mt-4 space-y-3">
                  {candidate.top_roles.length === 0 ? <div className="rounded-[24px] border border-dashed border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-4 text-sm text-[var(--text-secondary)]">No role matches available yet.</div> : candidate.top_roles.map((role) => <div key={role.id} className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-4"><p className="text-sm font-semibold text-[var(--text-primary)]">{role.name}</p><p className="mt-1 text-xs uppercase tracking-[0.2em] text-[var(--text-muted)]">{role.seniority_level}</p><p className="mt-2 text-sm text-[var(--text-secondary)]">{role.description}</p><p className="mt-3 text-sm font-semibold text-[var(--text-primary)]">Fit score: {role.match_score}</p></div>)}
                </div>
              </section>
            </div>

            <section className="panel p-6">
              <p className="kicker">Skills</p>
              <h3 className="section-title">Skill evidence</h3>
              <div className="mt-4 flex flex-wrap gap-2">
                {candidate.skills.length === 0 ? <span className="rounded-full bg-[var(--surface-elevated)] px-3 py-1 text-sm text-[var(--text-secondary)]">No skills captured</span> : candidate.skills.map((skill) => <span key={skill} className="rounded-full bg-[var(--surface-elevated)] px-3 py-1 text-sm text-[var(--text-secondary)]">{skill}</span>)}
              </div>
            </section>
          </>
        )}
      </div>
    </DashboardLayout>
  );
}
