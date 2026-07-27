export default function RecruiterEmptyState({ title, description, action }) {
  return (
    <div className="rounded-[24px] border border-dashed border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-8 text-center">
      <p className="text-lg font-semibold text-[var(--text-primary)]">{title}</p>
      <p className="mt-2 text-sm text-[var(--text-secondary)]">{description}</p>
      {action ? <div className="mt-4">{action}</div> : null}
    </div>
  );
}
