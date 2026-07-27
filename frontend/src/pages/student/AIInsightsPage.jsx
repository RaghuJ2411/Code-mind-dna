import React, { useEffect, useState } from 'react';
import DashboardLayout from '../../layouts/DashboardLayout';
import { getAIUsageHistory } from '../../api/student';

function formatDateTime(value) {
  if (!value) return 'Unknown';
  return new Date(value).toLocaleString();
}

export default function AIInsightsPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const result = await getAIUsageHistory();
        setData(result);
      } catch (err) {
        setError(err?.response?.data?.detail || 'Failed to load AI insights.');
      } finally {
        setLoading(false);
      }
    };

    load();
  }, []);

  return (
    <DashboardLayout title="AI Insights" role="STUDENT">
      <div className="space-y-6">
        <section className="panel p-6">
          <div className="flex items-center justify-between gap-4">
            <div>
              <p className="kicker">AI intelligence</p>
              <h2 className="section-title">AI usage summary</h2>
              <p className="mt-1 body-copy">Track how often assistance is used and where the strongest signals appear across your workflow.</p>
            </div>
          </div>

          {loading ? (
            <div className="mt-6 grid gap-4 lg:grid-cols-4">
              {[1, 2, 3, 4].map((item) => <div key={item} className="h-24 animate-pulse rounded-[24px] bg-[var(--surface-elevated)]" />)}
            </div>
          ) : error ? (
            <p className="mt-6 rounded-[24px] border border-red-200 bg-red-50 p-3 text-sm text-red-600">{error}</p>
          ) : (
            <div className="mt-6 grid gap-4 lg:grid-cols-4">
              {['CODE_REVIEW', 'ERROR_EXPLANATION', 'SKILL_GAP', 'ROADMAP'].map((task) => {
                const taskSummary = data.daily_summary.tasks[task];
                const limit = data.daily_summary.limits[task];
                return (
                  <div key={task} className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-5">
                    <p className="text-sm uppercase tracking-[0.18em] text-[var(--text-muted)]">{task.replace('_', ' ')}</p>
                    <p className="mt-3 text-3xl font-semibold text-[var(--text-primary)]">{taskSummary.total}/{limit}</p>
                    <p className="mt-2 text-sm text-[var(--text-secondary)]">Success {taskSummary.success}</p>
                    <p className="mt-1 text-sm text-[var(--text-secondary)]">Failed {taskSummary.failed}</p>
                  </div>
                );
              })}
            </div>
          )}
        </section>

        <section className="panel p-6">
          <div className="flex items-center justify-between gap-4">
            <div>
              <p className="kicker">History</p>
              <h2 className="section-title">Recent AI requests</h2>
              <p className="mt-1 body-copy">Review recent activity and understand the system’s current guidance state.</p>
            </div>
          </div>

          {loading ? (
            <p className="mt-4 body-copy">Loading request history...</p>
          ) : error ? (
            <p className="mt-4 text-sm text-rose-600">{error}</p>
          ) : !data.recent_requests.length ? (
            <p className="mt-4 body-copy">No AI requests yet. Try asking for assistance on a code submission.</p>
          ) : (
            <div className="mt-6 space-y-4">
              {data.recent_requests.map((item) => (
                <div key={item.id} className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-4">
                  <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                    <div>
                      <p className="text-sm font-semibold text-[var(--text-primary)]">{item.task_type.replace('_', ' ')}</p>
                      <p className="mt-1 text-sm text-[var(--text-secondary)]">Status: {item.status}</p>
                    </div>
                    <div className="text-xs text-[var(--text-muted)]">{formatDateTime(item.created_at)}</div>
                  </div>
                  <div className="mt-3 grid gap-3 sm:grid-cols-2">
                    <div className="rounded-[20px] bg-[var(--surface)] p-3">
                      <p className="text-xs uppercase tracking-[0.18em] text-[var(--text-muted)]">Provider</p>
                      <p className="mt-1 text-sm text-[var(--text-secondary)]">{item.provider || 'unknown'}</p>
                      <p className="mt-1 text-xs text-[var(--text-muted)]">Model: {item.model_name || 'unknown'}</p>
                    </div>
                    <div className="rounded-[20px] bg-[var(--surface)] p-3">
                      <p className="text-xs uppercase tracking-[0.18em] text-[var(--text-muted)]">Tokens</p>
                      <p className="mt-1 text-sm text-[var(--text-secondary)]">In: {item.input_token_count ?? '–'} • Out: {item.output_token_count ?? '–'}</p>
                      <p className="mt-1 text-xs text-[var(--text-muted)]">Latency: {item.latency_ms ? `${item.latency_ms}ms` : '–'}</p>
                    </div>
                  </div>
                  {item.error_category && (
                    <div className="mt-3 rounded-[20px] border border-red-200 bg-red-50 p-3 text-sm text-red-700">Error category: {item.error_category}</div>
                  )}
                </div>
              ))}
            </div>
          )}
        </section>
      </div>
    </DashboardLayout>
  );
}
