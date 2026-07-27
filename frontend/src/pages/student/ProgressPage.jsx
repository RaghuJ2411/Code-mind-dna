import { useEffect, useState } from 'react';
import DashboardLayout from '../../layouts/DashboardLayout';
import { getDailyProgress, getWeeklyProgress, getMonthlyProgress, getCodingHeatmap, getSkillGrowth, getGoalProgress, getProgressOverview } from '../../api/progress';

export default function ProgressPage() {
  const [overview, setOverview] = useState(null);
  const [daily, setDaily] = useState([]);
  const [weekly, setWeekly] = useState([]);
  const [monthly, setMonthly] = useState([]);
  const [heatmap, setHeatmap] = useState({});
  const [skillGrowth, setSkillGrowth] = useState([]);
  const [goals, setGoals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeChart, setActiveChart] = useState('daily');

  useEffect(() => {
    const loadData = async () => {
      try {
        const [overviewData, dailyData, weeklyData, monthlyData, heatmapData, skillData, goalData] = await Promise.all([
          getProgressOverview(),
          getDailyProgress(30),
          getWeeklyProgress(12),
          getMonthlyProgress(12),
          getCodingHeatmap(),
          getSkillGrowth(90),
          getGoalProgress(),
        ]);
        setOverview(overviewData);
        setDaily(dailyData.data || []);
        setWeekly(weeklyData.data || []);
        setMonthly(monthlyData.data || []);
        setHeatmap(heatmapData.data || {});
        setSkillGrowth(skillData.data || []);
        setGoals(goalData.data || []);
      } catch (err) {
        setError(err?.response?.data?.detail || 'Failed to load progress data');
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  const maxDailyValue = Math.max(...daily.map((d) => d.problems_solved), 1);
  const maxWeeklyValue = Math.max(...weekly.map((w) => w.problems_solved), 1);

  return (
    <DashboardLayout title="Progress Analytics" role="STUDENT">
      <div className="space-y-6">
        {error && <div className="rounded-[24px] border border-red-200 bg-red-50 p-4 text-sm text-red-600">{error}</div>}

        {loading ? (
          <div className="grid gap-4 md:grid-cols-4">{[1, 2, 3, 4].map((i) => <div key={i} className="h-24 animate-pulse rounded-[24px] bg-[var(--surface-elevated)]" />)}</div>
        ) : overview && (
          <section className="grid gap-4 md:grid-cols-4">
            <div className="panel-soft p-4">
              <p className="text-sm text-[var(--text-muted)]">Today</p>
              <p className="mt-2 text-2xl font-semibold">{overview.daily.problems_solved} solved</p>
              <p className="mt-1 text-xs text-[var(--text-muted)]">{overview.daily.active_minutes} min active</p>
            </div>
            <div className="panel-soft p-4">
              <p className="text-sm text-[var(--text-muted)]">This Week</p>
              <p className="mt-2 text-2xl font-semibold">{overview.weekly.problems_solved} solved</p>
              <p className="mt-1 text-xs text-[var(--text-muted)]">{(overview.weekly.solve_rate * 100).toFixed(0)}% solve rate</p>
            </div>
            <div className="panel-soft p-4">
              <p className="text-sm text-[var(--text-muted)]">Total</p>
              <p className="mt-2 text-2xl font-semibold">{overview.total.problems_solved}</p>
              <p className="mt-1 text-xs text-[var(--text-muted)]">{overview.total.solve_rate}% overall</p>
            </div>
            <div className="panel-soft p-4">
              <p className="text-sm text-[var(--text-muted)]">Current Streak</p>
              <p className="mt-2 text-2xl font-semibold">🔥 {overview.current_streak} days</p>
            </div>
          </section>
        )}

        <section className="panel p-6">
          <div className="flex flex-wrap gap-2">
            {['daily', 'weekly', 'monthly', 'heatmap', 'skills', 'goals'].map((tab) => (
              <button key={tab} onClick={() => setActiveChart(tab)} className={`rounded-full px-4 py-2 text-sm font-medium capitalize transition ${activeChart === tab ? 'bg-[var(--brand-primary)] text-white' : 'bg-[var(--surface-elevated)] text-[var(--text-secondary)]'}`}>{tab.replace('_', ' ')}</button>
            ))}
          </div>

          {activeChart === 'daily' && (
            <div className="mt-4">
              <h3 className="section-title">Daily Progress (Last 30 Days)</h3>
              <div className="mt-4 flex items-end gap-1 overflow-x-auto pb-2" style={{ minHeight: 120 }}>
                {daily.map((d) => (
                  <div key={d.date} className="flex flex-col items-center gap-1" title={`${d.date}: ${d.problems_solved} solved`}>
                    <div className="w-4 rounded-t bg-[var(--brand-primary)] transition-all" style={{ height: `${(d.problems_solved / maxDailyValue) * 80}px`, minHeight: d.problems_solved > 0 ? 4 : 0 }} />
                    <span className="text-xs text-[var(--text-muted)]">{new Date(d.date).getDate()}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeChart === 'weekly' && (
            <div className="mt-4">
              <h3 className="section-title">Weekly Progress</h3>
              <div className="mt-4 flex items-end gap-2 overflow-x-auto pb-2" style={{ minHeight: 120 }}>
                {weekly.map((w) => (
                  <div key={w.week_start} className="flex flex-col items-center gap-1" title={`Week ${w.week_start}: ${w.problems_solved} solved`}>
                    <div className="w-8 rounded-t bg-emerald-500 transition-all" style={{ height: `${(w.problems_solved / maxWeeklyValue) * 80}px`, minHeight: w.problems_solved > 0 ? 4 : 0 }} />
                    <span className="text-xs text-[var(--text-muted)]">{new Date(w.week_start).getDate()}/{new Date(w.week_start).getMonth() + 1}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeChart === 'monthly' && (
            <div className="mt-4">
              <h3 className="section-title">Monthly Progress</h3>
              <div className="mt-4 space-y-3">
                {monthly.map((m) => (
                  <div key={m.month} className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-4">
                    <div className="flex items-center justify-between gap-3">
                      <span className="font-medium text-[var(--text-primary)]">{m.month}</span>
                      <span className="text-sm text-[var(--text-secondary)]">{m.accepted}/{m.total_submissions} accepted ({m.solve_rate}%)</span>
                    </div>
                    <div className="mt-2 h-2 overflow-hidden rounded-full bg-[var(--surface-interactive)]">
                      <div className="h-full rounded-full bg-emerald-500 transition-all" style={{ width: `${m.solve_rate}%` }} />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeChart === 'heatmap' && (
            <div className="mt-4">
              <h3 className="section-title">Coding Heatmap</h3>
              <p className="mt-2 text-sm text-[var(--text-secondary)]">Activity overview for the year. Darker squares mean more activity.</p>
              <div className="mt-4 grid grid-cols-7 gap-1">
                {Object.entries(heatmap).map(([dateStr, data]) => {
                  const intensity = Math.min(data.active_minutes / 60, 1);
                  const bgColor = intensity === 0 ? 'var(--surface-interactive)' : `rgba(16, 185, 129, ${0.2 + intensity * 0.8})`;
                  return (
                    <div key={dateStr} className="aspect-square rounded" style={{ backgroundColor: bgColor }} title={`${dateStr}: ${data.active_minutes} min, ${data.problems_solved} solved`} />
                  );
                })}
              </div>
            </div>
          )}

          {activeChart === 'skills' && (
            <div className="mt-4">
              <h3 className="section-title">Skill Growth</h3>
              <div className="mt-4 space-y-3">
                {skillGrowth.map((s) => (
                  <div key={s.week_start} className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-4">
                    <p className="text-sm font-medium text-[var(--text-primary)]">Week of {s.week_start}</p>
                    <div className="mt-2 grid grid-cols-2 gap-3 text-sm">
                      <div><span className="text-[var(--text-muted)]">Solve Rate:</span> <span className="font-medium">{(s.solve_rate * 100).toFixed(0)}%</span></div>
                      <div><span className="text-[var(--text-muted)]">Easy:</span> <span className="font-medium">{(s.easy_solve_rate * 100).toFixed(0)}%</span></div>
                      <div><span className="text-[var(--text-muted)]">Medium:</span> <span className="font-medium">{(s.medium_solve_rate * 100).toFixed(0)}%</span></div>
                      <div><span className="text-[var(--text-muted)]">Hard:</span> <span className="font-medium">{(s.hard_solve_rate * 100).toFixed(0)}%</span></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeChart === 'goals' && (
            <div className="mt-4">
              <h3 className="section-title">Goal Progress</h3>
              {goals.length === 0 ? (
                <p className="mt-4 body-copy">No goals set. Create goals to track your progress.</p>
              ) : (
                <div className="mt-4 space-y-3">
                  {goals.map((goal) => (
                    <div key={goal.id} className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-4">
                      <div className="flex items-center justify-between gap-3">
                        <div>
                          <p className="font-semibold text-[var(--text-primary)]">{goal.title}</p>
                          <p className="text-sm text-[var(--text-secondary)]">{goal.current_value}/{goal.target_value}</p>
                        </div>
                        <span className="metric-pill">{goal.status}</span>
                      </div>
                      <div className="mt-2 h-2 overflow-hidden rounded-full bg-[var(--surface-interactive)]">
                        <div className="h-full rounded-full bg-[var(--brand-primary)] transition-all" style={{ width: `${goal.progress_pct}%` }} />
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </section>
      </div>
    </DashboardLayout>
  );
}

