import React from 'react';

const sampleActivities = [
  { id: 1, title: 'Practice session completed', detail: 'You finished the latest challenge with measurable progress.', time: '2m ago' },
  { id: 2, title: 'Mentor guidance added', detail: 'A new recommendation was shared for your next learning sprint.', time: '12m ago' },
  { id: 3, title: 'Recruiter review updated', detail: 'A candidate moved forward in the hiring pipeline.', time: '1h ago' },
];

export default function ActivityFeed({ items = sampleActivities }) {
  return (
    <div className="panel p-6">
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="kicker">Recent activity</p>
          <h3 className="section-title">What changed recently</h3>
        </div>
        <span className="metric-pill">Live feed</span>
      </div>

      <div className="mt-5 space-y-3">
        {items.map((item) => (
          <div key={item.id} className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-4">
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="text-sm font-semibold text-[var(--text-primary)]">{item.title}</p>
                <p className="mt-1 text-sm text-[var(--text-secondary)]">{item.detail}</p>
              </div>
              <span className="text-xs font-medium text-[var(--text-muted)]">{item.time}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
