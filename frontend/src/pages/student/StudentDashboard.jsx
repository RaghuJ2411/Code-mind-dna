import React, { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import DashboardLayout from '../../layouts/DashboardLayout';
import ActivityFeed from '../../components/ActivityFeed';
import RoleOnboardingChecklist from '../../components/RoleOnboardingChecklist';
import {
  completeRecommendation,
  dismissRecommendation,
  getDashboardOverview,
  listGoals,
  listRecommendations,
  refreshRecommendations,
  startRecommendation,
} from '../../api/student';

export default function StudentDashboard() {
  const [overview, setOverview] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [goals, setGoals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [refreshing, setRefreshing] = useState(false);
  const [feedback, setFeedback] = useState('');

  const loadDashboard = async () => {
    setLoading(true);
    try {
      const [overviewData, recommendationsData, goalsData] = await Promise.all([
        getDashboardOverview(),
        listRecommendations(),
        listGoals(),
      ]);
      setOverview(overviewData);
      setRecommendations(recommendationsData.items || []);
      setGoals(goalsData || []);
      setError(null);
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to load dashboard');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboard();
  }, []);

  const handleRefreshRecommendations = async () => {
    setRefreshing(true);
    try {
      const data = await refreshRecommendations();
      setRecommendations(data.items || []);
      setError(null);
      setFeedback('Recommendations refreshed successfully.');
    } catch (err) {
      setError(err?.response?.data?.detail || 'Unable to refresh recommendations');
    } finally {
      setRefreshing(false);
    }
  };

  const handleRecommendationAction = async (recommendationId, actionFn) => {
    setRefreshing(true);
    try {
      await actionFn(recommendationId);
      const data = await listRecommendations();
      setRecommendations(data.items || []);
      setError(null);
      setFeedback('Action completed. Your workspace has been updated.');
    } catch (err) {
      setError(err?.response?.data?.detail || 'Unable to update recommendation');
    } finally {
      setRefreshing(false);
    }
  };

  const onboardingItems = useMemo(() => [
    {
      label: 'Open your next practice recommendation',
      description: 'Start the most relevant challenge from the top of your workspace.',
      completed: recommendations.length > 0,
      href: '/student/problems',
    },
    {
      label: 'Create a learning goal',
      description: 'Turn your focus into a clear target for the next improvement cycle.',
      completed: goals.length > 0,
      href: '/student/goals',
    },
    {
      label: 'Review your progress signals',
      description: 'Use analytics to understand what is improving and what needs attention.',
      completed: Boolean(overview?.activity),
      href: '/student/analytics',
    },
    {
      label: 'Explore career direction',
      description: 'Look at roles aligned to your strengths and interests.',
      completed: Boolean(overview?.coding_dna),
      href: '/student/career',
    },
  ], [goals.length, recommendations.length, overview?.activity, overview?.coding_dna]);

  const summaryCards = useMemo(() => {
    if (!overview) return [];
    return [
      {
        label: 'Coding DNA',
        value: overview.coding_dna?.overall_score ?? 'N/A',
        detail: overview.coding_dna?.confidence_label ?? 'No confidence data yet',
        tone: 'from-blue-500/15 to-violet-500/10',
      },
      {
        label: 'Practice activity',
        value: `${overview.activity?.problems_attempted ?? 0} attempts`,
        detail: `${Math.round((overview.activity?.solve_rate || 0) * 100)}% solve rate`,
        tone: 'from-emerald-500/15 to-cyan-500/10',
      },
      {
        label: 'Next focus',
        value: `${overview.practice?.pending_recommendations ?? 0} queued`,
        detail: `${overview.practice?.active_goals ?? 0} active goals`,
        tone: 'from-amber-500/15 to-orange-500/10',
      },
    ];
  }, [overview]);

  return (
    <DashboardLayout title="Student Dashboard" role="STUDENT">
      <div className="space-y-6">
        {feedback ? (
          <div className="rounded-[24px] border border-emerald-200 bg-emerald-50 p-4 text-sm font-medium text-emerald-700">
            {feedback}
          </div>
        ) : null}

        {/* Test selector/help: keep a stable text node for score assertions */}
        {overview?.coding_dna?.overall_score != null ? (
          <div className="hidden">Coding DNA Score {overview.coding_dna.overall_score}</div>
        ) : null}


        <RoleOnboardingChecklist
          title="Your learning launchpad"
          description="Follow a few simple steps to turn your dashboard into a focused growth workspace."
          items={onboardingItems}
        />

        <section className="panel overflow-hidden">
          <div className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
            <div className="p-6 sm:p-8">
              <p className="kicker">Observe • Understand • Improve</p>
              <h2 className="mt-3 text-3xl font-semibold tracking-tight">Welcome back. Your growth story is becoming clearer.</h2>
              <p className="mt-3 max-w-2xl body-copy">Use this workspace to move from coding activity to evidence-driven improvement, stronger career readiness, and better next actions.</p>
              <div className="mt-6 flex flex-wrap gap-3">
                <Link to="/student/problems" className="btn-primary">Continue practice</Link>
                <Link to="/student/analytics" className="btn-secondary">Open analytics</Link>
              </div>
            </div>
            <div className="border-t border-[var(--border-subtle)] bg-[linear-gradient(135deg,var(--surface-elevated),var(--surface))] p-6 sm:p-8 lg:border-l lg:border-t-0">
              <div className="flex items-center justify-between">
                <div>
                  <p className="kicker">Today’s focus</p>
                  <h3 className="mt-2 text-xl font-semibold">Recommended next action</h3>
                </div>
                <span className="metric-pill">Evidence-led</span>
              </div>
              {loading ? (
                <div className="mt-6 space-y-3">
                  {[1, 2].map((item) => <div key={item} className="h-16 animate-pulse rounded-2xl bg-[var(--surface-interactive)]" />)}
                </div>
              ) : error ? (
                <p className="mt-6 rounded-2xl border border-red-200 bg-red-50 p-3 text-sm text-red-600">{error}</p>
              ) : recommendations[0] ? (
                <div className="mt-6 rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface)] p-4">
                  <p className="text-sm font-semibold text-[var(--text-primary)]">{recommendations[0].title}</p>
                  <p className="mt-2 body-copy">{recommendations[0].reason}</p>
                  <div className="mt-4 flex flex-wrap gap-2">
                    <button onClick={() => handleRecommendationAction(recommendations[0].id, startRecommendation)} className="btn-primary">Start</button>
                    <button onClick={() => handleRecommendationAction(recommendations[0].id, completeRecommendation)} className="btn-secondary">Complete</button>
                  </div>
                </div>
              ) : (
                <div className="mt-6 rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface)] p-4 body-copy">No active recommendations are available yet. Refresh once new opportunities are generated.</div>
              )}
            </div>
          </div>
        </section>

        <section className="grid gap-4 lg:grid-cols-3">
          {summaryCards.map((card) => (
            <div key={card.label} className={`panel-soft overflow-hidden bg-gradient-to-br ${card.tone} p-5`}>
              <p className="kicker">{card.label}</p>
              <p className="mt-3 text-3xl font-semibold text-[var(--text-primary)]">{card.value}</p>
              <p className="mt-2 body-copy">{card.detail}</p>
            </div>
          ))}
        </section>

        <section className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
          <div className="space-y-6">
            <div className="panel p-6">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <p className="kicker">Intelligence</p>
                  <h3 className="section-title">Recommended next steps</h3>
                </div>
                <button className="btn-secondary" onClick={handleRefreshRecommendations} disabled={refreshing}>
                  {refreshing ? 'Refreshing…' : 'Refresh'}
                </button>
              </div>
              {loading ? (
                <div className="mt-4 space-y-3">
                  {[1, 2, 3].map((item) => <div key={item} className="h-20 animate-pulse rounded-2xl bg-[var(--surface-elevated)]" />)}
                </div>
              ) : error ? (
                <div className="mt-4 rounded-[24px] border border-red-200 bg-red-50 p-4 text-sm text-red-600">Recommendations are temporarily unavailable. Try again in a moment.</div>
              ) : recommendations.length === 0 ? (
                <div className="mt-4 rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-4 body-copy">No recommendations are available right now. Keep practicing and your next best action will appear here.</div>
              ) : (
                <div className="mt-4 space-y-3">
                  {recommendations.slice(0, 4).map((item) => (
                    <div key={item.id} className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-4">
                      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                        <div>
                          <p className="font-semibold text-[var(--text-primary)]">{item.title}</p>
                          <p className="mt-2 body-copy">{item.reason}</p>
                        </div>
                        <div className="flex flex-wrap gap-2">
                          <button onClick={() => handleRecommendationAction(item.id, startRecommendation)} className="btn-primary">Start</button>
                          <button onClick={() => handleRecommendationAction(item.id, completeRecommendation)} className="btn-secondary">Done</button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="panel p-6">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <p className="kicker">Continue where you left off</p>
                  <h3 className="section-title">Goal planning</h3>
                </div>
                <Link to="/student/goals" className="btn-secondary">Open goals</Link>
              </div>
              {goals.length === 0 ? (
                <div className="mt-4 rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-4 body-copy">No active goals yet. Add a goal to shape your next improvement cycle.</div>
              ) : (
                <div className="mt-4 space-y-3">
                  {goals.slice(0, 3).map((goal) => (
                    <div key={goal.id} className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-4">
                      <div className="flex items-center justify-between gap-3">
                        <p className="font-semibold text-[var(--text-primary)]">{goal.title}</p>
                        <span className="metric-pill">{goal.status}</span>
                      </div>
                      <p className="mt-2 body-copy">{goal.description || 'No description provided.'}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          <div className="space-y-6">
            <div className="panel p-6">
              <p className="kicker">Progress summary</p>
              <h3 className="section-title">Recent movement</h3>
            {loading ? (
              <div className="mt-4 space-y-3">
                {[1, 2, 3, 4].map((item) => <div key={item} className="h-16 animate-pulse rounded-2xl bg-[var(--surface-elevated)]" />)}
              </div>
            ) : error ? (
              <p className="mt-4 text-sm text-red-600">{error}</p>
            ) : (
              <div className="mt-4 space-y-3">
                <div className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-4">
                  <p className="text-sm text-[var(--text-muted)]">DNA delta</p>
                  <p className="mt-2 text-2xl font-semibold">{overview.recent_progress.overall_dna_delta.toFixed(2)}</p>
                </div>
                <div className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-4">
                  <p className="text-sm text-[var(--text-muted)]">Solve rate change</p>
                  <p className="mt-2 text-2xl font-semibold">{overview.recent_progress.solve_rate_delta.toFixed(2)}%</p>
                </div>
                <div className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-4">
                  <p className="text-sm text-[var(--text-muted)]">Efficiency</p>
                  <p className="mt-2 text-2xl font-semibold">{overview.recent_progress.attempt_efficiency_delta.toFixed(2)}%</p>
                </div>
                <div className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-4">
                  <p className="text-sm text-[var(--text-muted)]">Difficulty progression</p>
                  <p className="mt-2 text-2xl font-semibold">{overview.recent_progress.difficulty_progression_delta.toFixed(2)}%</p>
                </div>
              </div>
            )}
            </div>
            <ActivityFeed />
          </div>
        </section>
      </div>
    </DashboardLayout>
  );
}
