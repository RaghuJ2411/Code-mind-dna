import { useEffect, useState } from 'react';
import DashboardLayout from '../../layouts/DashboardLayout';
import { createGoal, deleteGoal, listGoals, updateGoal } from '../../api/student';

const goalTypes = [
  { label: 'Solve Problems', value: 'SOLVE_PROBLEMS' },
  { label: 'Active Days', value: 'ACTIVE_DAYS' },
  { label: 'Practice Topic', value: 'PRACTICE_TOPIC' },
  { label: 'Complete Mentor Tasks', value: 'COMPLETE_MENTOR_TASKS' },
];

export default function StudentGoalsPage() {
  const [goals, setGoals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [creatingGoal, setCreatingGoal] = useState(false);
  const [goalError, setGoalError] = useState(null);
  const [editingGoal, setEditingGoal] = useState(null);
  const [goalForm, setGoalForm] = useState({
    goal_type: 'SOLVE_PROBLEMS',
    title: '',
    description: '',
    target_value: 3,
    period_start: '2026-07-01',
    period_end: '2026-07-07',
  });

  const loadGoals = async () => {
    setLoading(true);
    try {
      const data = await listGoals();
      setGoals(data || []);
      setError(null);
    } catch (err) {
      setError(err?.response?.data?.detail || 'Unable to load goals.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadGoals();
  }, []);

  const handleGoalChange = (key, value) => {
    setGoalForm((current) => ({ ...current, [key]: value }));
  };

  const resetGoalForm = () => {
    setGoalForm({
      goal_type: 'SOLVE_PROBLEMS',
      title: '',
      description: '',
      target_value: 3,
      period_start: '2026-07-01',
      period_end: '2026-07-07',
    });
    setEditingGoal(null);
  };

  const handleCreateGoal = async (event) => {
    event.preventDefault();
    setCreatingGoal(true);
    setGoalError(null);

    try {
      if (editingGoal) {
        const updated = await updateGoal(editingGoal.id, goalForm);
        setGoals((current) => current.map((goal) => (goal.id === updated.id ? updated : goal)));
        resetGoalForm();
      } else {
        const created = await createGoal(goalForm);
        setGoals((current) => [created, ...current]);
        resetGoalForm();
      }
    } catch (err) {
      setGoalError(err?.response?.data?.detail || 'Unable to save goal');
    } finally {
      setCreatingGoal(false);
    }
  };

  const handleEditGoal = (goal) => {
    setEditingGoal(goal);
    setGoalForm({
      goal_type: goal.goal_type,
      title: goal.title,
      description: goal.description || '',
      target_value: goal.target_value,
      period_start: goal.period_start,
      period_end: goal.period_end,
    });
  };

  const handleDeleteGoal = async (goalId) => {
    setCreatingGoal(true);
    setGoalError(null);
    try {
      await deleteGoal(goalId);
      setGoals((current) => current.filter((goal) => goal.id !== goalId));
    } catch (err) {
      setGoalError(err?.response?.data?.detail || 'Unable to delete goal');
    } finally {
      setCreatingGoal(false);
    }
  };

  return (
    <DashboardLayout title="Goals" role="STUDENT">
      <div className="grid gap-6 xl:grid-cols-[1fr_1fr]">
        <section className="panel p-6">
          <p className="kicker">Plan</p>
          <h2 className="section-title">{editingGoal ? 'Edit goal' : 'Create a goal'}</h2>
          <p className="mt-2 body-copy">Set a measurable milestone for your coding practice and keep it visible across your workflow.</p>
          <form className="mt-6 space-y-4" onSubmit={handleCreateGoal}>
            <div>
              <label className="block text-sm font-medium text-[var(--text-secondary)]">Goal type</label>
              <select value={goalForm.goal_type} onChange={(event) => handleGoalChange('goal_type', event.target.value)} className="mt-1 w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface-elevated)] px-3 py-2.5 text-sm outline-none transition focus:border-[var(--brand-primary)]">
                {goalTypes.map((option) => (<option key={option.value} value={option.value}>{option.label}</option>))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-[var(--text-secondary)]">Title</label>
              <input type="text" value={goalForm.title} onChange={(event) => handleGoalChange('title', event.target.value)} className="mt-1 w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface-elevated)] px-3 py-2.5 text-sm outline-none transition focus:border-[var(--brand-primary)]" required />
            </div>

            <div>
              <label className="block text-sm font-medium text-[var(--text-secondary)]">Description</label>
              <textarea value={goalForm.description} onChange={(event) => handleGoalChange('description', event.target.value)} className="mt-1 w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface-elevated)] px-3 py-2.5 text-sm outline-none transition focus:border-[var(--brand-primary)]" rows={4} />
            </div>

            <div className="grid gap-4 lg:grid-cols-2">
              <div>
                <label className="block text-sm font-medium text-[var(--text-secondary)]">Target value</label>
                <input type="number" min={1} value={goalForm.target_value} onChange={(event) => handleGoalChange('target_value', Number(event.target.value))} className="mt-1 w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface-elevated)] px-3 py-2.5 text-sm outline-none transition focus:border-[var(--brand-primary)]" required />
              </div>
              <div>
                <label className="block text-sm font-medium text-[var(--text-secondary)]">Start date</label>
                <input type="date" value={goalForm.period_start} onChange={(event) => handleGoalChange('period_start', event.target.value)} className="mt-1 w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface-elevated)] px-3 py-2.5 text-sm outline-none transition focus:border-[var(--brand-primary)]" required />
              </div>
              <div>
                <label className="block text-sm font-medium text-[var(--text-secondary)]">End date</label>
                <input type="date" value={goalForm.period_end} onChange={(event) => handleGoalChange('period_end', event.target.value)} className="mt-1 w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface-elevated)] px-3 py-2.5 text-sm outline-none transition focus:border-[var(--brand-primary)]" required />
              </div>
            </div>

            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <button type="submit" className="btn-primary" disabled={creatingGoal}>{creatingGoal ? 'Saving…' : editingGoal ? 'Save goal' : 'Create goal'}</button>
              {editingGoal && <button type="button" onClick={resetGoalForm} className="btn-secondary" disabled={creatingGoal}>Cancel</button>}
            </div>
            {goalError && <p className="text-sm text-rose-600">{goalError}</p>}
          </form>
        </section>

        <section className="panel p-6">
          <div className="flex items-center justify-between gap-4">
            <div>
              <p className="kicker">Momentum</p>
              <h2 className="section-title">Active goals</h2>
              <p className="mt-2 body-copy">Track your current progress and clear next milestones.</p>
            </div>
          </div>

          {loading ? (
            <div className="mt-6 space-y-3">
              <div className="h-20 animate-pulse rounded-[24px] bg-[var(--surface-elevated)]" />
              <div className="h-20 animate-pulse rounded-[24px] bg-[var(--surface-elevated)]" />
            </div>
          ) : error ? (
            <div className="mt-6 rounded-[24px] border border-red-200 bg-red-50 p-4 text-sm text-red-600">{error}</div>
          ) : goals.length === 0 ? (
            <div className="mt-6 rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-4 body-copy">No goals set yet. Create a new goal to stay focused.</div>
          ) : (
            <div className="mt-6 space-y-4">
              {goals.map((goal) => (
                <div key={goal.id} className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-4">
                  <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                    <div>
                      <p className="font-semibold text-[var(--text-primary)]">{goal.title}</p>
                      <p className="mt-1 text-sm text-[var(--text-secondary)]">{goal.description || 'No description provided.'}</p>
                    </div>
                    <div className="flex items-center gap-2">
                      <button onClick={() => handleEditGoal(goal)} className="btn-secondary">Edit</button>
                      <button onClick={() => handleDeleteGoal(goal.id)} className="rounded-2xl bg-rose-500 px-3 py-2 text-xs font-semibold text-white">Delete</button>
                      <span className="metric-pill">{goal.status}</span>
                    </div>
                  </div>
                  <div className="mt-3 grid gap-3 sm:grid-cols-2">
                    <p className="text-sm text-[var(--text-secondary)]">Target: {goal.target_value}</p>
                    <p className="text-sm text-[var(--text-secondary)]">{goal.period_start} — {goal.period_end}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>
    </DashboardLayout>
  );
}
