import { useEffect, useState } from 'react';
import DashboardLayout from '../../layouts/DashboardLayout';
import { listAchievements, listEarnedAchievements, listMilestones, getLeaderboard } from '../../api/achievements';

const TABS = ['Badges', 'Milestones', 'Leaderboard'];

export default function AchievementsPage() {
  const [activeTab, setActiveTab] = useState('Badges');
  const [achievements, setAchievements] = useState([]);
  const [earned, setEarned] = useState([]);
  const [milestones, setMilestones] = useState([]);
  const [leaderboard, setLeaderboard] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('');

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        const [achievementsData, earnedData, milestonesData, leaderboardData] = await Promise.all([
          listAchievements(),
          listEarnedAchievements(),
          listMilestones(),
          getLeaderboard(),
        ]);
        setAchievements(achievementsData);
        setEarned(earnedData);
        setMilestones(milestonesData);
        setLeaderboard(leaderboardData.entries || []);
      } catch (err) {
        setError(err?.response?.data?.detail || 'Failed to load achievements');
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  const filteredAchievements = achievements.filter((a) => !filter || a.category === filter);
  const earnedIds = new Set(earned.map((e) => e.achievement_id));

  return (
    <DashboardLayout title="Achievements" role="STUDENT">
      <div className="space-y-6">
        {error && <div className="rounded-[24px] border border-red-200 bg-red-50 p-4 text-sm text-red-600">{error}</div>}

        <section className="panel p-4 sm:p-6">
          <div className="flex flex-wrap gap-2">
            {TABS.map((tab) => (
              <button key={tab} onClick={() => setActiveTab(tab)} className={`rounded-full px-4 py-2 text-sm font-medium transition ${activeTab === tab ? 'bg-[var(--brand-primary)] text-white' : 'bg-[var(--surface-elevated)] text-[var(--text-secondary)]'}`}>{tab}</button>
            ))}
          </div>
        </section>

        {activeTab === 'Badges' && (
          <section className="panel p-6">
            <div className="flex items-center justify-between gap-3">
              <div>
                <p className="kicker">Achievements</p>
                <h2 className="section-title">Badges & Rewards</h2>
              </div>
              <span className="metric-pill">{earned.length} earned</span>
            </div>
            <div className="mt-4 flex flex-wrap gap-2">
              {['', 'CODING', 'LEARNING', 'CAREER', 'COMMUNITY'].map((cat) => (
                <button key={cat} onClick={() => setFilter(cat)} className={`rounded-full px-3 py-1.5 text-xs font-medium transition ${filter === cat ? 'bg-[var(--brand-primary)] text-white' : 'bg-[var(--surface-elevated)] text-[var(--text-secondary)]'}`}>{cat || 'All'}</button>
              ))}
            </div>
            {loading ? (
              <div className="mt-4 grid gap-4 md:grid-cols-3">{[1, 2, 3].map((i) => <div key={i} className="h-32 animate-pulse rounded-[24px] bg-[var(--surface-elevated)]" />)}</div>
            ) : filteredAchievements.length === 0 ? (
              <p className="mt-4 body-copy">No achievements found.</p>
            ) : (
              <div className="mt-4 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {filteredAchievements.map((a) => {
                  const isEarned = earnedIds.has(a.id);
                  return (
                    <div key={a.id} className={`rounded-[24px] border p-5 transition ${isEarned ? 'border-emerald-200 bg-gradient-to-br from-emerald-50 to-white' : 'border-[var(--border-subtle)] bg-[var(--surface-elevated)] opacity-60'}`}>
                      <div className="flex items-center justify-between">
                        <p className="text-2xl">{a.badge_icon || '🏆'}</p>
                        {isEarned && <span className="rounded-full bg-emerald-100 px-2.5 py-1 text-xs font-semibold text-emerald-700">✓ Earned</span>}
                      </div>
                      <p className="mt-3 font-semibold text-[var(--text-primary)]">{a.name}</p>
                      <p className="mt-1 text-sm text-[var(--text-secondary)]">{a.description}</p>
                      <div className="mt-3 flex items-center justify-between text-xs text-[var(--text-muted)]">
                        <span>{a.category}</span>
                        <span>+{a.xp_reward} XP</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </section>
        )}

        {activeTab === 'Milestones' && (
          <section className="panel p-6">
            <h2 className="section-title">Coding Milestones</h2>
            {loading ? (
              <p className="mt-4 body-copy">Loading...</p>
            ) : milestones.length === 0 ? (
              <p className="mt-4 body-copy">No milestones tracked yet. Start coding to track your progress.</p>
            ) : (
              <div className="mt-4 space-y-3">
                {milestones.map((m) => (
                  <div key={m.id} className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-4">
                    <div className="flex items-center justify-between gap-3">
                      <div>
                        <p className="font-semibold text-[var(--text-primary)]">{m.milestone_type.replace(/_/g, ' ')}</p>
                        <p className="text-sm text-[var(--text-secondary)]">{m.current_value} / {m.target_value}</p>
                      </div>
                      {m.achieved ? (
                        <span className="metric-pill bg-emerald-100 text-emerald-700">✓ Achieved</span>
                      ) : (
                        <span className="text-sm text-[var(--text-muted)]">{Math.round((m.current_value / m.target_value) * 100)}%</span>
                      )}
                    </div>
                    <div className="mt-2 h-2 overflow-hidden rounded-full bg-[var(--surface-interactive)]">
                      <div className={`h-full rounded-full transition-all ${m.achieved ? 'bg-emerald-500' : 'bg-[var(--brand-primary)]'}`} style={{ width: `${Math.min((m.current_value / m.target_value) * 100, 100)}%` }} />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>
        )}

        {activeTab === 'Leaderboard' && (
          <section className="panel p-6">
            <div className="flex items-center justify-between gap-3">
              <div>
                <p className="kicker">Competition</p>
                <h2 className="section-title">Student Leaderboard</h2>
              </div>
            </div>
            {loading ? (
              <p className="mt-4 body-copy">Loading...</p>
            ) : leaderboard.length === 0 ? (
              <p className="mt-4 body-copy">Leaderboard data not available yet.</p>
            ) : (
              <div className="mt-4 space-y-2">
                {leaderboard.map((entry) => (
                  <div key={entry.student_id} className={`rounded-[24px] border p-4 transition ${entry.rank <= 3 ? 'border-amber-200 bg-gradient-to-r from-amber-50 to-white' : 'border-[var(--border-subtle)] bg-[var(--surface-elevated)]'}`}>
                    <div className="flex items-center justify-between gap-3">
                      <div className="flex items-center gap-3">
                        <span className={`flex h-8 w-8 items-center justify-center rounded-full text-sm font-bold ${entry.rank === 1 ? 'bg-amber-100 text-amber-700' : entry.rank === 2 ? 'bg-slate-100 text-slate-700' : entry.rank === 3 ? 'bg-orange-100 text-orange-700' : 'bg-[var(--surface-interactive)] text-[var(--text-secondary)]'}`}>#{entry.rank}</span>
                        <div>
                          <p className="font-semibold text-[var(--text-primary)]">{entry.student_name}</p>
                          <p className="text-xs text-[var(--text-muted)]">{entry.problems_solved} solved · {entry.achievements_count} badges</p>
                        </div>
                      </div>
                      <p className="text-lg font-bold text-[var(--brand-primary)]">{entry.score.toLocaleString()}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>
        )}
      </div>
    </DashboardLayout>
  );
}

