export default function LoadingState({ lines = 4 }) {
  return (
    <div className="space-y-4">
      {Array.from({ length: lines }).map((_, index) => (
        <div key={index} className="h-20 animate-pulse rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)]" />
      ))}
    </div>
  );
}
