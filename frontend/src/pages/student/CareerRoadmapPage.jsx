import { useEffect, useState } from 'react';
import DashboardLayout from '../../layouts/DashboardLayout';
import { getRoadmap, createRoadmap, updateRoadmap, createMilestone, updateMilestone, getAISuggestions, listWeeklyGoals, listMonthlyGoals } from '../../api/careerRoadmap';

export default function CareerRoadmapPage() {
  const [roadmap, setRoadmap] = useState(null);
  const [suggestions, setSuggestions] = useState(null);
  const [weeklyGoals, setWeeklyGoals] = useState([]);
  const [monthlyGoals, setMonthlyGoals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [formMode, setFormMode] = useState('view');
  const [form, setForm] = useState({ career_goal: '', company_goal: '', target_role: '', target_seniority: '', timeline_months: 12, skills_required: [], current_skills: [] });
  const [skillInput, setSkillInput] = useState('');
  const [currentSkillInput, setCurrentSkillInput] = useState('');
  const [milestoneForm, setMilestoneForm] = useState({ title: '', description: '', milestone_type: 'WEEKLY', target_date: '' });

  const loadData = async () => {
    setLoading(true);
    try {
      const [roadmapData, suggestionsData, weeklyData, monthlyData] = await Promise.all([
        getRoadmap(),
        getAISuggestions(),
        listWeeklyGoals(),
        listMonthlyGoals(),
      ]);
      setRoadmap(roadmapData);
      setSuggestions(suggestionsData);
      setWeeklyGoals(weeklyData);
      setMonthlyGoals(monthlyData);
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to load career roadmap');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleCreateRoadmap = async (e) => {
    e.preventDefault();
    try {
      const created = await createRoadmap(form);
      setRoadmap(created);
      setFormMode('view');
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to create roadmap');
    }
  };

  const handleUpdateRoadmap = async (e) => {
    e.preventDefault();
    if (!roadmap) return;
    try {
      const updated = await updateRoadmap(roadmap.id, form);
      setRoadmap(updated);
      setFormMode('view');
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to update roadmap');
    }
  };

  const handleAddMilestone = async (e) => {
    e.preventDefault();
    if (!roadmap) return;
    try {
      await createMilestone(roadmap.id, milestoneForm);
      setMilestoneForm({ title: '', description: '', milestone_type: 'WEEKLY', target_date: '' });
      const refreshed = await getRoadmap();
      setRoadmap(refreshed);
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to add milestone');
    }
  };

  const startEdit = () => {
    if (!roadmap) return;
    setForm({
      career_goal: roadmap.career_goal,
      company_goal: roadmap.company_goal || '',
      target_role: roadmap.target_role || '',
      target_seniority: roadmap.target_seniority || '',
      timeline_months: roadmap.timeline_months || 12,
      skills_required: roadmap.skills_required || [],
      current_skills: roadmap.current_skills || [],
    });
    setFormMode('edit');
  };

  return (
    <DashboardLayout title="Career Roadmap" role="STUDENT">
      <div className="space-y-6">
        {error && <div className="rounded-[24px] border border-red-200 bg-red-50 p-4 text-sm text-red-600">{error}</div>}

        {loading ? (
          <div className="space-y-4">{[1, 2].map((i) => <div key={i} className="h-32 animate-pulse rounded-[24px] bg-[var(--surface-elevated)]" />)}</div>
        ) : !roadmap && formMode === 'view' ? (
          <section className="panel p-6">
            <p className="kicker">Career Planning</p>
            <h2 className="section-title">Create Your Career Roadmap</h2>
            <p className="mt-2 body-copy">Set your career goals, identify required skills, and track your progress toward your dream role.</p>
            <button onClick={() => setFormMode('create')} className="btn-primary mt-6">Get Started</button>
          </section>
        ) : formMode === 'create' || formMode === 'edit' ? (
          <section className="panel p-6">
            <h2 className="section-title">{formMode === 'create' ? 'Create Roadmap' : 'Edit Roadmap'}</h2>
            <form onSubmit={formMode === 'create' ? handleCreateRoadmap : handleUpdateRoadmap} className="mt-4 space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <label className="block text-sm font-medium text-[var(--text-secondary)]">Career Goal *</label>
                  <input value={form.career_goal} onChange={(e) => setForm({ ...form, career_goal: e.target.value })} className="mt-1 w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface-elevated)] px-4 py-2.5 text-sm outline-none focus:border-[var(--brand-primary)]" required />
                </div>
                <div>
                  <label className="block text-sm font-medium text-[var(--text-secondary)]">Target Company</label>
                  <input value={form.company_goal} onChange={(e) => setForm({ ...form, company_goal: e.target.value })} className="mt-1 w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface-elevated)] px-4 py-2.5 text-sm outline-none focus:border-[var(--brand-primary)]" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-[var(--text-secondary)]">Target Role</label>
                  <input value={form.target_role} onChange={(e) => setForm({ ...form, target_role: e.target.value })} className="mt-1 w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface-elevated)] px-4 py-2.5 text-sm outline-none focus:border-[var(--brand-primary)]" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-[var(--text-secondary)]">Timeline (months)</label>
                  <input type="number" value={form.timeline_months} onChange={(e) => setForm({ ...form, timeline_months: parseInt(e.target.value) || 12 })} className="mt-1 w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface-elevated)] px-4 py-2.5 text-sm outline-none focus:border-[var(--brand-primary)]" />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-[var(--text-secondary)]">Skills Required</label>
                <div className="mt-1 flex gap-2">
                  <input value={skillInput} onChange={(e) => setSkillInput(e.target.value)} className="flex-1 rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface-elevated)] px-4 py-2.5 text-sm outline-none focus:border-[var(--brand-primary)]" />
                  <button type="button" onClick={() => { if (skillInput.trim()) { setForm({ ...form, skills_required: [...form.skills_required, skillInput.trim()] }); setSkillInput(''); } }} className="rounded-2xl bg-[var(--brand-primary)] px-4 py-2 text-sm text-white">Add</button>
                </div>
                <div className="mt-2 flex flex-wrap gap-2">
                  {form.skills_required.map((s) => <span key={s} className="rounded-full bg-[var(--brand-primary)]/10 px-3 py-1 text-xs text-[var(--brand-primary)]">{s} <button type="button" onClick={() => setForm({ ...form, skills_required: form.skills_required.filter((x) => x !== s) })} className="ml-1">×</button></span>)}
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-[var(--text-secondary)]">Current Skills</label>
                <div className="mt-1 flex gap-2">
                  <input value={currentSkillInput} onChange={(e) => setCurrentSkillInput(e.target.value)} className="flex-1 rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface-elevated)] px-4 py-2.5 text-sm outline-none focus:border-[var(--brand-primary)]" />
                  <button type="button" onClick={() => { if (currentSkillInput.trim()) { setForm({ ...form, current_skills: [...form.current_skills, currentSkillInput.trim()] }); setCurrentSkillInput(''); } }} className="rounded-2xl bg-[var(--brand-primary)] px-4 py-2 text-sm text-white">Add</button>
                </div>
                <div className="mt-2 flex flex-wrap gap-2">
                  {form.current_skills.map((s) => <span key={s} className="rounded-full bg-emerald-100 px-3 py-1 text-xs text-emerald-700">{s} <button type="button" onClick={() => setForm({ ...form, current_skills: form.current_skills.filter((x) => x !== s) })} className="ml-1">×</button></span>)}
                </div>
              </div>
              <div className="flex gap-3">
                <button type="submit" className="btn-primary">{formMode === 'create' ? 'Create Roadmap' : 'Save Changes'}</button>
                <button type="button" onClick={() => setFormMode('view')} className="btn-secondary">Cancel</button>
              </div>
            </form>
          </section>
        ) : roadmap && (
          <>
            <section className="panel p-6">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <p className="kicker">Your Roadmap</p>
                  <h2 className="section-title">{roadmap.career_goal}</h2>
                  {roadmap.company_goal && <p className="mt-1 text-sm text-[var(--text-secondary)]">Target: {roadmap.company_goal}</p>}
                </div>
                <button onClick={startEdit} className="btn-secondary">Edit</button>
              </div>
              <div className="mt-4 grid gap-4 md:grid-cols-4">
                <div className="panel-soft p-3">
                  <p className="text-xs text-[var(--text-muted)]">Target Role</p>
                  <p className="mt-1 font-semibold">{roadmap.target_role || '—'}</p>
                </div>
                <div className="panel-soft p-3">
                  <p className="text-xs text-[var(--text-muted)]">Timeline</p>
                  <p className="mt-1 font-semibold">{roadmap.timeline_months ? `${roadmap.timeline_months} months` : '—'}</p>
                </div>
                <div className="panel-soft p-3">
                  <p className="text-xs text-[var(--text-muted)]">Skills Required</p>
                  <p className="mt-1 font-semibold">{roadmap.skills_required?.length || 0}</p>
                </div>
                <div className="panel-soft p-3">
                  <p className="text-xs text-[var(--text-muted)]">Current Skills</p>
                  <p className="mt-1 font-semibold">{roadmap.current_skills?.length || 0}</p>
                </div>
              </div>
            </section>

            <section className="panel p-6">
              <h3 className="section-title">Milestones</h3>
              <form onSubmit={handleAddMilestone} className="mt-4 grid gap-3 rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-4 md:grid-cols-4">
                <input value={milestoneForm.title} onChange={(e) => setMilestoneForm({ ...milestoneForm, title: e.target.value })} placeholder="Milestone title" className="rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] px-4 py-2.5 text-sm outline-none focus:border-[var(--brand-primary)]" required />
                <input value={milestoneForm.description || ''} onChange={(e) => setMilestoneForm({ ...milestoneForm, description: e.target.value })} placeholder="Description" className="rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] px-4 py-2.5 text-sm outline-none focus:border-[var(--brand-primary)]" />
                <select value={milestoneForm.milestone_type} onChange={(e) => setMilestoneForm({ ...milestoneForm, milestone_type: e.target.value })} className="rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] px-4 py-2.5 text-sm outline-none focus:border-[var(--brand-primary)]">
                  <option value="WEEKLY">Weekly</option>
                  <option value="MONTHLY">Monthly</option>
                  <option value="SKILL">Skill</option>
                  <option value="PROJECT">Project</option>
                </select>
                <button type="submit" className="rounded-2xl bg-[var(--brand-primary)] px-4 py-2.5 text-sm font-semibold text-white">Add Milestone</button>
              </form>
              <div className="mt-4 space-y-3">
                {roadmap.milestones?.length === 0 ? (
                  <p className="body-copy">No milestones yet. Add your first milestone above.</p>
                ) : (
                  roadmap.milestones?.map((m) => (
                    <div key={m.id} className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-4">
                      <div className="flex items-center justify-between gap-3">
                        <div className="flex items-center gap-3">
                          <div className={`flex h-8 w-8 items-center justify-center rounded-full text-sm font-semibold ${m.is_completed ? 'bg-emerald-100 text-emerald-700' : 'bg-[var(--surface-interactive)] text-[var(--text-secondary)]'}`}>{m.is_completed ? '✓' : m.order_index + 1}</div>
                          <div>
                            <p className="font-semibold text-[var(--text-primary)]">{m.title}</p>
                            {m.description && <p className="text-sm text-[var(--text-secondary)]">{m.description}</p>}
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="metric-pill">{m.milestone_type}</span>
                          <span className="text-sm text-[var(--text-muted)]">{Math.round(m.progress_pct)}%</span>
                        </div>
                      </div>
                      <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-[var(--surface-interactive)]">
                        <div className="h-full rounded-full bg-[var(--brand-primary)] transition-all" style={{ width: `${m.progress_pct}%` }} />
                      </div>
                    </div>
                  ))
                )}
              </div>
            </section>

            {suggestions && (
              <section className="panel p-6">
                <h3 className="section-title">AI Suggestions</h3>
                <div className="mt-4 space-y-3">
                  {suggestions.suggestions?.map((s, i) => (
                    <div key={i} className="rounded-[24px] border border-[var(--border-subtle)] bg-gradient-to-r from-[var(--brand-primary)]/5 to-transparent p-4">
                      <p className="text-sm text-[var(--text-primary)]">💡 {s}</p>
                    </div>
                  ))}
                  {suggestions.next_steps?.length > 0 && (
                    <div className="mt-4">
                      <p className="text-sm font-semibold text-[var(--text-secondary)]">Next Steps</p>
                      <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-[var(--text-secondary)]">
                        {suggestions.next_steps.map((step, i) => <li key={i}>{step}</li>)}
                      </ul>
                    </div>
                  )}
                </div>
              </section>
            )}
          </>
        )}
      </div>
    </DashboardLayout>
  );
}

