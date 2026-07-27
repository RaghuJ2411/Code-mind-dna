import React, { useEffect, useMemo, useState } from 'react';
import DashboardLayout from '../../layouts/DashboardLayout';
import ActivityFeed from '../../components/ActivityFeed';
import MentorAlertForm from '../../components/MentorAlertForm';
import RoleOnboardingChecklist from '../../components/RoleOnboardingChecklist';
import {
  listMentorAlerts,
  acknowledgeMentorAlert,
  resolveMentorAlert,
  listMentorStudents,
  createMentorAlert,
  generateMentorAlerts,
} from '../../api/mentor';
import {
  listMentorCareerRoles,
  listMentorCareerReviews,
  createMentorCareerReview,
} from '../../api/mentorCareer';

const actionLabels = {
  OPEN: 'Needs attention',
  ACKNOWLEDGED: 'Under review',
  RESOLVED: 'Improving',
};

function MetricCard({ label, value, caption, tone = 'default' }) {
  const toneClass = {
    default: 'border-[var(--border-subtle)] bg-[var(--surface-elevated)]',
    success: 'border-emerald-200 bg-emerald-50',
    warning: 'border-amber-200 bg-amber-50',
    info: 'border-sky-200 bg-sky-50',
  }[tone];

  return (
    <div className={`rounded-[24px] border p-4 ${toneClass}`}>
      <p className="text-sm text-[var(--text-muted)]">{label}</p>
      <p className="mt-2 text-2xl font-semibold text-[var(--text-primary)]">{value}</p>
      <p className="mt-1 text-sm text-[var(--text-secondary)]">{caption}</p>
    </div>
  );
}

export default function MentorDashboard() {
  const [alerts, setAlerts] = useState([]);
  const [students, setStudents] = useState([]);
  const [careerRoles, setCareerRoles] = useState([]);
  const [careerReviews, setCareerReviews] = useState([]);
  const [careerReviewForm, setCareerReviewForm] = useState({ student_id: '', role_id: '', note: '' });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [updating, setUpdating] = useState(false);
  const [creatingAlert, setCreatingAlert] = useState(false);
  const [reviewSubmitting, setReviewSubmitting] = useState(false);
  const [generatingAlerts, setGeneratingAlerts] = useState(false);
  const [feedback, setFeedback] = useState('');
  const [selectedStudentId, setSelectedStudentId] = useState('');

  const loadData = async () => {
    setLoading(true);
    try {
      const [alertResponse, studentResponse, roleResponse, reviewResponse] = await Promise.all([
        listMentorAlerts(),
        listMentorStudents(),
        listMentorCareerRoles(),
        listMentorCareerReviews(),
      ]);
      setAlerts(alertResponse.items || []);
      setStudents(studentResponse || []);
      setCareerRoles(roleResponse || []);
      setCareerReviews(reviewResponse.items || []);
      setError(null);
    } catch (err) {
      setError(err?.response?.data?.detail || 'Unable to load mentor data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const loadAlerts = async () => {
    setLoading(true);
    try {
      const alertResponse = await listMentorAlerts();
      setAlerts(alertResponse.items || []);
      setError(null);
    } catch (err) {
      setError(err?.response?.data?.detail || 'Unable to load alerts.');
    } finally {
      setLoading(false);
    }
  };

  const loadCareerReviews = async () => {
    try {
      const reviewResponse = await listMentorCareerReviews();
      setCareerReviews(reviewResponse.items || []);
    } catch (err) {
      setError(err?.response?.data?.detail || 'Unable to load career reviews.');
    }
  };

  const handleCareerReviewChange = (key, value) => {
    setCareerReviewForm((current) => ({ ...current, [key]: value }));
  };

  const handleCareerReviewSubmit = async (event) => {
    event.preventDefault();
    setReviewSubmitting(true);
    try {
      await createMentorCareerReview({
        student_id: Number(careerReviewForm.student_id),
        role_id: careerReviewForm.role_id ? Number(careerReviewForm.role_id) : null,
        note: careerReviewForm.note,
      });
      setCareerReviewForm({ student_id: '', role_id: '', note: '' });
      await loadCareerReviews();
      setError(null);
    } catch (err) {
      setError(err?.response?.data?.detail || 'Unable to save career review.');
    } finally {
      setReviewSubmitting(false);
    }
  };

  const updateAlert = async (alertId, actionFn) => {
    setUpdating(true);
    try {
      await actionFn(alertId);
      await loadAlerts();
      setFeedback('Alert updated successfully.');
    } catch (err) {
      setError(err?.response?.data?.detail || 'Unable to update alert.');
    } finally {
      setUpdating(false);
    }
  };

  const handleCreateAlert = async (payload) => {
    setCreatingAlert(true);
    try {
      await createMentorAlert(payload);
      await loadData();
      setError(null);
    } catch (err) {
      setError(err?.response?.data?.detail || 'Unable to create alert.');
    } finally {
      setCreatingAlert(false);
    }
  };

  const handleGenerateAlerts = async () => {
    setGeneratingAlerts(true);
    try {
      await generateMentorAlerts();
      await loadAlerts();
      setError(null);
    } catch (err) {
      setError(err?.response?.data?.detail || 'Unable to generate alerts.');
    } finally {
      setGeneratingAlerts(false);
    }
  };

  const onboardingItems = useMemo(() => [
    {
      label: 'Review the priority queue',
      description: 'Scan the students most likely to benefit from a timely intervention.',
      completed: students.length > 0,
      href: '/mentor/dashboard',
    },
    {
      label: 'Acknowledge a live signal',
      description: 'Move one alert into review so it remains visible and actionable.',
      completed: alerts.some((alert) => alert.status === 'ACKNOWLEDGED' || alert.status === 'RESOLVED'),
      href: '/mentor/dashboard',
    },
    {
      label: 'Leave a career guidance note',
      description: 'Capture mentoring advice that helps a student act on their next milestone.',
      completed: careerReviews.length > 0,
      href: '/mentor/dashboard',
    },
    {
      label: 'Generate fresh alerts',
      description: 'Let the system surface new support opportunities from recent activity.',
      completed: alerts.length > 0,
      href: '/mentor/dashboard',
    },
  ], [alerts, careerReviews.length, students.length]);

  const summaryMetrics = useMemo(() => ({
    students: students.length,
    alerts: alerts.filter((alert) => alert.status === 'OPEN').length,
    interventions: alerts.filter((alert) => alert.status !== 'RESOLVED').length,
    reviews: careerReviews.length,
  }), [alerts, careerReviews.length, students.length]);

  const priorityStudents = useMemo(() => {
    return students.slice(0, 6).map((student) => ({
      ...student,
      openAlertCount: alerts.filter((alert) => alert.student_id === student.id && alert.status !== 'RESOLVED').length,
      priority: alerts.some((alert) => alert.student_id === student.id && alert.status === 'OPEN') ? 'HIGH' : 'WATCH',
      reason: alerts.some((alert) => alert.student_id === student.id) ? 'Recent signal needs follow-up' : 'Steady progress',
      action: alerts.some((alert) => alert.student_id === student.id) ? 'Review evidence' : 'Continue monitoring',
    }));
  }, [alerts, students]);

  return (
    <DashboardLayout title="Mentor Dashboard" role="MENTOR">
      <div className="space-y-6">
        <RoleOnboardingChecklist
          title="Your mentoring launchpad"
          description="Keep your attention focused on the students and signals that matter most today."
          items={onboardingItems}
        />

        <section className="panel p-6">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <p className="kicker">Mentor action center</p>
              <h2 className="page-title">Guide student growth with clear next actions.</h2>
              <p className="page-subtitle">Focus on students who need attention, understand the latest evidence, and move to the right intervention without losing context.</p>
            </div>
            <div className="flex flex-wrap gap-2">
              <button
                className="btn-primary"
                data-testid="generate-mentor-alerts"
                onClick={handleGenerateAlerts}
                disabled={generatingAlerts || loading}
              >
                {generatingAlerts ? 'Generating…' : 'Generate alerts'}
              </button>
              <button className="btn-secondary" onClick={loadAlerts} disabled={loading}>{loading ? 'Refreshing…' : 'Refresh'}</button>
            </div>
          </div>

          <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <MetricCard label="Assigned students" value={summaryMetrics.students} caption="Students currently visible to you" />
            <MetricCard label="Needs attention" value={summaryMetrics.alerts} caption="Open alerts requiring action" tone="warning" />
            <MetricCard label="Active interventions" value={summaryMetrics.interventions} caption="Signals currently being tracked" tone="info" />
            <MetricCard label="Pending reviews" value={summaryMetrics.reviews} caption="Career guidance notes saved" tone="success" />
          </div>
        </section>

        <section className="panel p-6">
          <div className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <p className="kicker">Students needing attention</p>
              <h2 className="section-title">Priority queue</h2>
              <p className="mt-1 body-copy">This queue highlights the students most likely to benefit from intervention or support.</p>
            </div>
            <div className="metric-pill">Evidence-led follow-up</div>
          </div>

          {loading ? (
            <div className="mt-6 grid gap-3 md:grid-cols-2">
              {[1, 2, 3, 4].map((item) => <div key={item} className="h-24 animate-pulse rounded-[24px] bg-[var(--surface-elevated)]" />)}
            </div>
          ) : priorityStudents.length === 0 ? (
            <div className="mt-6 rounded-[24px] border border-dashed border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-6 text-sm text-[var(--text-secondary)]">No students are currently queued for action.</div>
          ) : (
            <div className="mt-6 grid gap-4 xl:grid-cols-2">
              {priorityStudents.map((student) => (
                <div key={student.id} className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-5">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="text-lg font-semibold text-[var(--text-primary)]">{student.full_name}</p>
                      <p className="mt-1 text-sm text-[var(--text-secondary)]">{student.email}</p>
                      <div className="mt-3 flex flex-wrap gap-2">
                        <span className={`rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] ${student.priority === 'HIGH' ? 'bg-amber-100 text-amber-700' : 'bg-sky-100 text-sky-700'}`}>{student.priority === 'HIGH' ? 'High priority' : 'Watch'}</span>
                        <span className="rounded-full bg-[var(--surface-interactive)] px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-[var(--text-secondary)]">{student.openAlertCount} alert{student.openAlertCount === 1 ? '' : 's'}</span>
                      </div>
                    </div>
                    <button className="btn-secondary" onClick={() => setSelectedStudentId(student.id)}>View student</button>
                  </div>
                  <div className="mt-4 rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] p-4">
                    <p className="text-sm font-semibold text-[var(--text-primary)]">Why this needs attention</p>
                    <p className="mt-2 text-sm text-[var(--text-secondary)]">{student.reason}</p>
                    <p className="mt-3 text-sm text-[var(--text-secondary)]">Current action: {student.action}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        <section className="panel p-6">
          <div className="flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">
            <div>
              <p className="kicker">Open alerts</p>
              <h2 className="section-title">Signal review and action workflow</h2>
              <p className="mt-2 body-copy">Review student support signals and make the next intervention clear and timely.</p>
            </div>
            <div className="flex flex-wrap gap-2">
              <button aria-label="generate mentor alerts" className="btn-primary" onClick={handleGenerateAlerts} disabled={generatingAlerts || loading}>{generatingAlerts ? 'Generating…' : 'Generate for mentor'}</button>
              <button className="btn-secondary" onClick={loadAlerts} disabled={loading}>{loading ? 'Refreshing…' : 'Refresh'}</button>
            </div>
          </div>

          <div className="mt-6 grid gap-6 lg:grid-cols-[1fr_400px]">
            <div>
              {loading ? (
                <div className="space-y-3">
                  <div className="h-20 animate-pulse rounded-[24px] bg-[var(--surface-elevated)]" />
                  <div className="h-20 animate-pulse rounded-[24px] bg-[var(--surface-elevated)]" />
                </div>
              ) : error ? (
                <p className="text-sm text-rose-600">{error}</p>
              ) : alerts.length === 0 ? (
                <div className="rounded-[24px] border border-dashed border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-6 text-sm text-[var(--text-secondary)]">No active alerts yet. The system will surface students who need support once a signal appears.</div>
              ) : (
                <div className="space-y-4">
                  {alerts.map((alert) => (
                    <div key={alert.id} className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-4">
                      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                        <div>
                          <div className="flex flex-wrap items-center gap-2">
                            <span className="text-sm uppercase tracking-[0.2em] text-[var(--text-muted)]">{alert.severity}</span>
                            <span className="rounded-full bg-[var(--surface-interactive)] px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-[var(--text-secondary)]">{actionLabels[alert.status] || alert.status}</span>
                          </div>
                          <p className="mt-2 text-lg font-semibold text-[var(--text-primary)]">{alert.message}</p>
                          <p className="mt-2 text-sm text-[var(--text-secondary)]">Student ID: {alert.student_id ?? 'N/A'}</p>
                        </div>
                        <div className="flex flex-wrap gap-2">
                          <button onClick={() => updateAlert(alert.id, acknowledgeMentorAlert)} className="rounded-2xl bg-amber-600 px-3 py-2 text-xs font-semibold text-white" disabled={updating}>Acknowledge</button>
                          <button onClick={() => updateAlert(alert.id, resolveMentorAlert)} className="rounded-2xl bg-emerald-600 px-3 py-2 text-xs font-semibold text-white" disabled={updating}>Resolve</button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-6">
              <h3 className="text-base font-semibold text-[var(--text-primary)]">Create alert</h3>
              <p className="mt-2 body-copy">Flag a student or batch issue for follow-up.</p>
              <div className="mt-4">
                <MentorAlertForm students={students} onSubmit={handleCreateAlert} loading={creatingAlert} />
              </div>
            </div>
          </div>
        </section>

        <section className="panel p-6">
          <div className="flex items-center justify-between gap-4">
            <div>
              <p className="kicker">Career guidance</p>
              <h2 className="section-title">Mentor recommendations</h2>
              <p className="mt-1 body-copy">Record guidance that helps students build toward the right next milestone.</p>
            </div>
          </div>

          <div className="mt-6 grid gap-6 lg:grid-cols-[1fr_420px]">
            <div>
              {careerReviews.length === 0 ? (
                <div className="rounded-[24px] border border-dashed border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-6 text-sm text-[var(--text-secondary)]">No career reviews added yet.</div>
              ) : (
                <div className="space-y-4">
                  {careerReviews.map((review) => (
                    <div key={review.id} className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-4">
                      <div className="flex flex-col gap-2">
                        <div className="flex flex-wrap items-center gap-2">
                          <span className="rounded-full bg-[var(--surface-interactive)] px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-[var(--text-secondary)]">Mentor recommendation</span>
                          <span className="text-xs text-[var(--text-muted)]">{new Date(review.created_at).toLocaleString()}</span>
                        </div>
                        <p className="text-sm font-semibold text-[var(--text-primary)]">Student ID: {review.student_id}</p>
                        <p className="text-sm text-[var(--text-secondary)]">Role ID: {review.role_id ?? 'Any'}</p>
                        <p className="text-sm text-[var(--text-secondary)]">{review.note}</p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-6">
              <h3 className="text-base font-semibold text-[var(--text-primary)]">Add guidance</h3>
              <form onSubmit={handleCareerReviewSubmit} className="mt-4 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-[var(--text-secondary)]">Student</label>
                  <select value={careerReviewForm.student_id} onChange={(event) => handleCareerReviewChange('student_id', event.target.value)} className="mt-1 w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] px-3 py-2 text-sm outline-none" required>
                    <option value="">Select a student</option>
                    {students.map((student) => (<option key={student.id} value={student.id}>{student.full_name}</option>))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-[var(--text-secondary)]">Role</label>
                  <select value={careerReviewForm.role_id} onChange={(event) => handleCareerReviewChange('role_id', event.target.value)} className="mt-1 w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] px-3 py-2 text-sm outline-none">
                    <option value="">Any role</option>
                    {careerRoles.map((role) => (<option key={role.id} value={role.id}>{role.name}</option>))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-[var(--text-secondary)]">Mentor guidance</label>
                  <textarea value={careerReviewForm.note} onChange={(event) => handleCareerReviewChange('note', event.target.value)} className="mt-1 w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] px-3 py-2 text-sm outline-none" rows={5} required />
                </div>

                <button type="submit" className="btn-primary" disabled={reviewSubmitting}>{reviewSubmitting ? 'Saving…' : 'Save review'}</button>
              </form>
            </div>
          </div>
        </section>

        <ActivityFeed />
      </div>
    </DashboardLayout>
  );
}
