import { useEffect, useState } from 'react';
import DashboardLayout from '../../layouts/DashboardLayout';
import { listAssessments, getAssessment, startAssessment, submitAssessment, getAssessmentHistory, getPerformanceAnalysis } from '../../api/assessments';

const TABS = ['Available', 'History', 'Performance'];

export default function AssessmentsPage() {
  const [activeTab, setActiveTab] = useState('Available');
  const [assessments, setAssessments] = useState([]);
  const [history, setHistory] = useState([]);
  const [performance, setPerformance] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeAssessment, setActiveAssessment] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [attemptId, setAttemptId] = useState(null);
  const [answers, setAnswers] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);
  const [timeLeft, setTimeLeft] = useState(null);

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        const [assessmentsData, historyData, perfData] = await Promise.all([
          listAssessments(),
          getAssessmentHistory(),
          getPerformanceAnalysis(),
        ]);
        setAssessments(assessmentsData);
        setHistory(historyData.items || []);
        setPerformance(perfData);
      } catch (err) {
        setError(err?.response?.data?.detail || 'Failed to load assessments');
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  useEffect(() => {
    if (!timeLeft || timeLeft <= 0) return;
    const timer = setInterval(() => setTimeLeft((t) => t - 1), 1000);
    return () => clearInterval(timer);
  }, [timeLeft]);

  const handleStart = async (assessmentId) => {
    try {
      const data = await startAssessment(assessmentId);
      setAttemptId(data.attempt_id);
      setQuestions(data.questions || []);
      setActiveAssessment(assessmentId);
      setAnswers({});
      setResult(null);
      if (data.time_limit_minutes) {
        setTimeLeft(data.time_limit_minutes * 60);
      }
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to start');
    }
  };

  const handleSubmit = async () => {
    if (!activeAssessment || !attemptId) return;
    setSubmitting(true);
    try {
      const formatted = Object.entries(answers).map(([questionId, answer]) => ({
        question_id: parseInt(questionId),
        answer,
      }));
      const data = await submitAssessment(activeAssessment, formatted);
      setResult(data);
      setActiveAssessment(null);
      setQuestions([]);
      setTimeLeft(null);
      const refreshed = await getAssessmentHistory();
      setHistory(refreshed.items || []);
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to submit');
    } finally {
      setSubmitting(false);
    }
  };

  const formatTime = (seconds) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}:${s.toString().padStart(2, '0')}`;
  };

  if (activeAssessment && questions.length > 0) {
    return (
      <DashboardLayout title="Assessment" role="STUDENT">
        <div className="space-y-6">
          {timeLeft !== null && (
            <div className="sticky top-0 z-10 rounded-[24px] bg-[var(--surface-elevated)] p-4 text-center shadow-md">
              <p className={`text-2xl font-bold ${timeLeft < 60 ? 'text-red-500' : 'text-[var(--text-primary)]'}`}>{formatTime(timeLeft)}</p>
              <p className="text-sm text-[var(--text-muted)]">Time Remaining</p>
            </div>
          )}
          {questions.map((q, i) => (
            <div key={q.id} className="panel p-6">
              <div className="flex items-start gap-3">
                <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-[var(--brand-primary)] text-xs font-semibold text-white">{i + 1}</span>
                <div className="flex-1">
                  <p className="font-medium text-[var(--text-primary)]">{q.question_text}</p>
                  <p className="mt-1 text-xs text-[var(--text-muted)]">{q.points} point{q.points !== 1 ? 's' : ''}</p>
                  {q.question_type === 'MCQ' && q.options?.length > 0 && (
                    <div className="mt-3 space-y-2">
                      {q.options.map((option, oi) => (
                        <label key={oi} className="flex cursor-pointer items-center gap-3 rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-3 text-sm transition hover:border-[var(--brand-primary)]">
                          <input type="radio" name={`q_${q.id}`} value={option} onChange={(e) => setAnswers({ ...answers, [q.id]: e.target.value })} checked={answers[q.id] === option} className="text-[var(--brand-primary)]" />
                          {option}
                        </label>
                      ))}
                    </div>
                  )}
                  {q.question_type === 'CODING' && (
                    <textarea value={answers[q.id] || ''} onChange={(e) => setAnswers({ ...answers, [q.id]: e.target.value })} placeholder="Write your code here..." rows={6} className="mt-3 w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface-elevated)] px-4 py-3 font-mono text-sm outline-none focus:border-[var(--brand-primary)]" />
                  )}
                </div>
              </div>
            </div>
          ))}
          <div className="flex gap-3">
            <button onClick={handleSubmit} disabled={submitting} className="btn-primary">{submitting ? 'Submitting...' : `Submit (${Object.keys(answers).length}/${questions.length} answered)`}</button>
            <button onClick={() => { setActiveAssessment(null); setQuestions([]); }} className="btn-secondary">Cancel</button>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  if (result) {
    return (
      <DashboardLayout title="Assessment Result" role="STUDENT">
        <div className="space-y-6">
          <section className={`panel p-6 ${result.passed ? 'border-emerald-200' : 'border-red-200'}`}>
            <div className="text-center">
              <p className="text-4xl">{result.passed ? '🎉' : '📚'}</p>
              <p className={`mt-4 text-3xl font-bold ${result.passed ? 'text-emerald-600' : 'text-red-600'}`}>{result.score.toFixed(1)}%</p>
              <p className={`mt-2 text-lg font-semibold ${result.passed ? 'text-emerald-600' : 'text-red-600'}`}>{result.passed ? 'Passed!' : 'Needs Improvement'}</p>
              <p className="mt-2 text-sm text-[var(--text-secondary)]">{result.correct_answers}/{result.total_questions} correct</p>
              {result.time_taken_seconds && <p className="text-sm text-[var(--text-muted)]">Time: {formatTime(result.time_taken_seconds)}</p>}
            </div>
            <div className="mt-6 space-y-3">
              {result.results?.map((r, i) => (
                <div key={i} className={`rounded-[24px] p-4 ${r.is_correct ? 'border border-emerald-200 bg-emerald-50' : 'border border-red-200 bg-red-50'}`}>
                  <div className="flex items-center justify-between gap-3">
                    <p className="text-sm font-medium">{r.question_text}</p>
                    <span className={`text-sm font-semibold ${r.is_correct ? 'text-emerald-600' : 'text-red-600'}`}>{r.is_correct ? '✓ Correct' : '✗ Incorrect'}</span>
                  </div>
                  <p className="mt-1 text-xs text-[var(--text-secondary)]">Your answer: {r.student_answer}</p>
                  {!r.is_correct && <p className="mt-1 text-xs text-red-600">Correct: {r.correct_answer}</p>}
                </div>
              ))}
            </div>
            <button onClick={() => setResult(null)} className="btn-primary mt-6">Back to Assessments</button>
          </section>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout title="Assessments" role="STUDENT">
      <div className="space-y-6">
        {error && <div className="rounded-[24px] border border-red-200 bg-red-50 p-4 text-sm text-red-600">{error}</div>}

        <section className="panel p-4 sm:p-6">
          <div className="flex flex-wrap gap-2">
            {TABS.map((tab) => (
              <button key={tab} onClick={() => setActiveTab(tab)} className={`rounded-full px-4 py-2 text-sm font-medium transition ${activeTab === tab ? 'bg-[var(--brand-primary)] text-white' : 'bg-[var(--surface-elevated)] text-[var(--text-secondary)]'}`}>{tab}</button>
            ))}
          </div>
        </section>

        {activeTab === 'Available' && (
          <section className="panel p-6">
            <h3 className="section-title">Available Assessments</h3>
            {loading ? (
              <div className="mt-4 space-y-3">{[1, 2].map((i) => <div key={i} className="h-20 animate-pulse rounded-[24px] bg-[var(--surface-elevated)]" />)}</div>
            ) : assessments.length === 0 ? (
              <p className="mt-4 body-copy">No assessments available yet.</p>
            ) : (
              <div className="mt-4 space-y-3">
                {assessments.map((a) => (
                  <div key={a.id} className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-4">
                    <div className="flex items-center justify-between gap-3">
                      <div>
                        <p className="font-semibold text-[var(--text-primary)]">{a.title}</p>
                        <p className="mt-1 text-sm text-[var(--text-secondary)]">{a.description}</p>
                        <div className="mt-2 flex flex-wrap gap-2">
                          <span className="rounded-full bg-[var(--brand-primary)]/10 px-2.5 py-1 text-xs text-[var(--brand-primary)]">{a.assessment_type}</span>
                          <span className="rounded-full bg-amber-100 px-2.5 py-1 text-xs text-amber-700">{a.difficulty}</span>
                          <span className="text-xs text-[var(--text-muted)]">{a.total_questions} questions</span>
                          {a.time_limit_minutes && <span className="text-xs text-[var(--text-muted)]">{a.time_limit_minutes} min</span>}
                        </div>
                      </div>
                      <button onClick={() => handleStart(a.id)} className="btn-primary">Start</button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>
        )}

        {activeTab === 'History' && (
          <section className="panel p-6">
            <h3 className="section-title">Assessment History</h3>
            {history.length === 0 ? (
              <p className="mt-4 body-copy">No assessment history yet.</p>
            ) : (
              <div className="mt-4 space-y-3">
                {history.map((h) => (
                  <div key={h.attempt_id} className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-4">
                    <div className="flex items-center justify-between gap-3">
                      <div>
                        <p className="font-semibold text-[var(--text-primary)]">{h.assessment_title}</p>
                        <p className="mt-1 text-sm text-[var(--text-secondary)]">{new Date(h.submitted_at || h.started_at).toLocaleDateString()}</p>
                      </div>
                      <div className="text-right">
                        <p className={`text-lg font-semibold ${h.passed ? 'text-emerald-600' : 'text-red-600'}`}>{h.score?.toFixed(1)}%</p>
                        <span className={`metric-pill ${h.passed ? 'bg-emerald-100 text-emerald-700' : 'bg-red-100 text-red-700'}`}>{h.passed ? 'Passed' : 'Failed'}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>
        )}

        {activeTab === 'Performance' && (
          <section className="panel p-6">
            <h3 className="section-title">Performance Analysis</h3>
            {!performance ? (
              <p className="mt-4 body-copy">Complete assessments to see your performance analysis.</p>
            ) : (
              <div className="mt-4 space-y-4">
                <div className="grid gap-4 md:grid-cols-3">
                  <div className="panel-soft p-4">
                    <p className="text-sm text-[var(--text-muted)]">Total Assessments</p>
                    <p className="mt-2 text-2xl font-semibold">{performance.total_assessments}</p>
                  </div>
                  <div className="panel-soft p-4">
                    <p className="text-sm text-[var(--text-muted)]">Average Score</p>
                    <p className="mt-2 text-2xl font-semibold">{performance.average_score.toFixed(1)}%</p>
                  </div>
                  <div className="panel-soft p-4">
                    <p className="text-sm text-[var(--text-muted)]">Pass Rate</p>
                    <p className="mt-2 text-2xl font-semibold">{performance.pass_rate.toFixed(1)}%</p>
                  </div>
                </div>
                {performance.strengths?.length > 0 && (
                  <div>
                    <p className="text-sm font-semibold text-emerald-600">Strengths</p>
                    <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-[var(--text-secondary)]">
                      {performance.strengths.map((s, i) => <li key={i}>{s}</li>)}
                    </ul>
                  </div>
                )}
                {performance.weaknesses?.length > 0 && (
                  <div>
                    <p className="text-sm font-semibold text-amber-600">Weaknesses</p>
                    <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-[var(--text-secondary)]">
                      {performance.weaknesses.map((s, i) => <li key={i}>{s}</li>)}
                    </ul>
                  </div>
                )}
                {performance.recommendations?.length > 0 && (
                  <div>
                    <p className="text-sm font-semibold text-[var(--brand-primary)]">Recommendations</p>
                    <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-[var(--text-secondary)]">
                      {performance.recommendations.map((s, i) => <li key={i}>{s}</li>)}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </section>
        )}
      </div>
    </DashboardLayout>
  );
}

