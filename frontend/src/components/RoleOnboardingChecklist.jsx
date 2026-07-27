import React from 'react';

function RouterAwareLink({ to, children }) {
  return (
    <a href={to} className="text-sm font-semibold text-[var(--brand-primary)]">
      {children}
    </a>
  );
}

export default function RoleOnboardingChecklist({ title, description, items = [] }) {
  const completedCount = items.filter((item) => item.completed).length;

  return (
    <section className="panel p-6">
      <div className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p className="kicker">First steps</p>
          <h3 className="section-title">{title}</h3>
          <p className="mt-2 body-copy">{description}</p>
        </div>
        <span className="metric-pill">{completedCount}/{items.length} ready</span>
      </div>

      <div className="mt-5 space-y-3">
        {items.map((item) => (
          <div key={item.label} className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-4">
            <div className="flex items-start gap-3">
              <span className={`mt-1 h-2.5 w-2.5 rounded-full ${item.completed ? 'bg-emerald-500' : 'bg-[var(--brand-primary)]'}`} />
              <div className="flex-1">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <p className="text-sm font-semibold text-[var(--text-primary)]">{item.label}</p>
                  {item.href ? (
                    <RouterAwareLink to={item.href}>Go</RouterAwareLink>
                  ) : null}
                </div>
                <p className="mt-1 text-sm text-[var(--text-secondary)]">{item.description}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
