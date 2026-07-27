import React from 'react';

function InfoChip({ label, value }) {
  return (
    <div className="rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] p-3">
      <p className="text-[10px] font-semibold uppercase tracking-[0.24em] text-[var(--text-muted)]">{label}</p>
      <p className="mt-1 text-sm font-semibold text-[var(--text-primary)]">{value}</p>
    </div>
  );
}

export default function WhyThisCandidateMatches({ candidate }) {
  const evidence = [];
  const gaps = [];

  if (candidate?.readiness_score != null) {
    evidence.push({
      title: 'Readiness signal',
      detail: `Readiness is ${candidate.readiness_label || 'being evaluated'} with a score of ${candidate.readiness_score}.`,
    });
  }

  if (candidate?.resume_strength != null) {
    evidence.push({
      title: 'Resume strength',
      detail: `Resume strength is ${candidate.resume_strength}, supported by ${candidate.resume_entry_count ?? 0} resume entries.`,
    });
  }

  if (candidate?.project_alignment != null) {
    evidence.push({
      title: 'Project alignment',
      detail: `Project alignment is ${candidate.project_alignment} with ${candidate.project_count ?? 0} project entries.`,
    });
  }

  if (candidate?.interview_readiness != null) {
    evidence.push({
      title: 'Interview readiness',
      detail: `Interview readiness is ${candidate.interview_readiness} and ${candidate.interview_session_count ?? 0} practice sessions are on record.`,
    });
  }

  if ((candidate?.top_roles || []).length) {
    evidence.push({
      title: 'Role fit',
      detail: `The strongest role match is ${candidate.top_roles[0].name}.`,
    });
  }

  if (!candidate?.skills?.length) {
    gaps.push('Skill evidence is still limited.');
  }

  if (!candidate?.top_roles?.length) {
    gaps.push('Role-specific match evidence is not yet populated.');
  }

  if ((candidate?.skills || []).length < 3) {
    gaps.push('More evidence is needed to confirm strong role coverage.');
  }

  return (
    <div className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-5">
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="kicker">Explainable match</p>
          <h3 className="section-title">Why this candidate matches</h3>
        </div>
        <span className="metric-pill">Evidence-backed</span>
      </div>

      <div className="mt-4 grid gap-3 md:grid-cols-2">
        {evidence.map((item) => (
          <div key={item.title} className="rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] p-4">
            <p className="text-sm font-semibold text-[var(--text-primary)]">{item.title}</p>
            <p className="mt-2 text-sm text-[var(--text-secondary)]">{item.detail}</p>
          </div>
        ))}
      </div>

      <div className="mt-5 rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] p-4">
        <p className="text-sm font-semibold text-[var(--text-primary)]">Signal summary</p>
        <p className="mt-2 text-sm text-[var(--text-secondary)]">{candidate?.signal_summary || 'Signal summary is being generated from the current evidence set.'}</p>
      </div>

      <div className="mt-5 grid gap-3 md:grid-cols-2">
        <div className="rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] p-4">
          <p className="text-sm font-semibold text-[var(--text-primary)]">Strong evidence</p>
          <ul className="mt-3 space-y-2 text-sm text-[var(--text-secondary)]">
            {evidence.length ? evidence.map((item) => <li key={item.title}>• {item.detail}</li>) : <li>• No evidence summary is available yet.</li>}
          </ul>
        </div>
        <div className="rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] p-4">
          <p className="text-sm font-semibold text-[var(--text-primary)]">Potential gap</p>
          <ul className="mt-3 space-y-2 text-sm text-[var(--text-secondary)]">
            {gaps.length ? gaps.map((item) => <li key={item}>△ {item}</li>) : <li>△ No gaps identified from the current evidence set.</li>}
          </ul>
        </div>
      </div>

      <div className="mt-5 grid gap-3 sm:grid-cols-3">
        <InfoChip label="Match" value={candidate?.fit_score != null ? `${candidate.fit_score.toFixed(0)}%` : 'N/A'} />
        <InfoChip label="Confidence" value={candidate?.confidence_label || 'Pending'} />
        <InfoChip label="Readiness" value={candidate?.readiness_label || 'Pending'} />
      </div>
    </div>
  );
}
