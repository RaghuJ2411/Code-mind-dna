import { useEffect, useMemo, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import Editor from '@monaco-editor/react';
import DashboardLayout from '../../layouts/DashboardLayout';
import { getDraft, getMySubmissions, getProblemBySlug, runCode, saveDraft, submitCode } from '../../api/problems';
import AICodeReviewPanel from '../../components/AICodeReviewPanel';
import AIAssistancePanel from '../../components/AIAssistancePanel';

const LANGUAGE_OPTIONS = ['python', 'javascript', 'java'];
const LANGUAGE_LABELS = { python: 'Python', javascript: 'JavaScript', java: 'Java' };

export default function CodingArenaPage() {
  const { slug } = useParams();
  const navigate = useNavigate();
  const [problem, setProblem] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [language, setLanguage] = useState('python');
  const [code, setCode] = useState('');
  const [saveState, setSaveState] = useState('Saved');
  const [activeCase, setActiveCase] = useState(0);
  const [runState, setRunState] = useState('idle');
  const [submitState, setSubmitState] = useState('idle');
  const [runResult, setRunResult] = useState(null);
  const [submitResult, setSubmitResult] = useState(null);
  const [submissions, setSubmissions] = useState([]);

  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true);
        const data = await getProblemBySlug(slug);
        setProblem(data);
        const starter = data?.starter_code?.[language] || '';
        setCode(starter);
        const draft = await getDraft(data.id, language).catch(() => null);
        if (draft?.code) {
          setCode(draft.code);
        }
      } catch (err) {
        setError(err?.response?.data?.detail || 'Unable to load this problem.');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [slug]);

  useEffect(() => {
    if (!problem) return;
    const starter = problem?.starter_code?.[language] || '';
    const loadDraft = async () => {
      try {
        const draft = await getDraft(problem.id, language).catch(() => null);
        if (draft?.code) {
          setCode(draft.code);
        } else {
          setCode(starter);
        }
      } catch {
        setCode(starter);
      }
    };
    loadDraft();
  }, [language, problem]);

  useEffect(() => {
    if (!problem || !code) return;
    const timer = setTimeout(async () => {
      try {
        setSaveState('Saving...');
        await saveDraft(problem.id, language, code);
        setSaveState('Saved');
      } catch {
        setSaveState('Save failed');
      }
    }, 1200);
    return () => clearTimeout(timer);
  }, [code, language, problem]);

  useEffect(() => {
    const loadSubmissions = async () => {
      if (!problem) return;
      try {
        const data = await getMySubmissions({ problemId: problem.id, page: 1, pageSize: 10 });
        setSubmissions(data.items || []);
      } catch {
        setSubmissions([]);
      }
    };
    loadSubmissions();
  }, [problem]);

  const sampleCases = useMemo(() => problem?.sample_test_cases || [], [problem]);

  const handleRun = async () => {
    if (!problem) return;
    setRunState('running');
    setRunResult(null);
    try {
      const result = await runCode(problem.id, language, code);
      setRunResult(result);
    } catch (err) {
      setRunResult({ error: err?.response?.data?.detail || 'Unable to run code right now.' });
    } finally {
      setRunState('idle');
    }
  };

  const handleSubmit = async () => {
    if (!problem) return;
    setSubmitState('running');
    setSubmitResult(null);
    try {
      const result = await submitCode(problem.id, language, code);
      setSubmitResult(result);
      const refreshed = await getMySubmissions({ problemId: problem.id, page: 1, pageSize: 10 });
      setSubmissions(refreshed.items || []);
    } catch (err) {
      setSubmitResult({ error: err?.response?.data?.detail || 'Unable to submit code right now.' });
    } finally {
      setSubmitState('idle');
    }
  };

  if (loading) {
    return <DashboardLayout title="Coding Arena" role="STUDENT"><div className="panel p-6">Loading problem details...</div></DashboardLayout>;
  }

  if (error) {
    return <DashboardLayout title="Coding Arena" role="STUDENT"><div className="panel p-6 text-rose-600">{error}</div></DashboardLayout>;
  }

  return (
    <DashboardLayout title={problem?.title || 'Coding Arena'} role="STUDENT">
      <div className="grid gap-6 xl:grid-cols-[1.05fr_1.35fr_0.95fr]">
        <section className="panel p-4 sm:p-6">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <p className="kicker">Challenge</p>
              <h2 className="section-title">{problem.title}</h2>
            </div>
            <button onClick={() => navigate('/student/problems')} className="btn-secondary">Back</button>
          </div>
          <div className="space-y-4 body-copy">
            <div>
              <h3 className="mb-1 font-semibold text-[var(--text-primary)]">Description</h3>
              <p>{problem.description}</p>
            </div>
            <div>
              <h3 className="mb-1 font-semibold text-[var(--text-primary)]">Constraints</h3>
              <p>{problem.constraints}</p>
            </div>
            <div>
              <h3 className="mb-1 font-semibold text-[var(--text-primary)]">Input Format</h3>
              <p>{problem.input_format}</p>
            </div>
            <div>
              <h3 className="mb-1 font-semibold text-[var(--text-primary)]">Output Format</h3>
              <p>{problem.output_format}</p>
            </div>
            <div>
              <h3 className="mb-1 font-semibold text-[var(--text-primary)]">Difficulty / Topic</h3>
              <p>{problem.difficulty} • {problem.topic}</p>
            </div>
          </div>
        </section>
        <section className="panel p-4 sm:p-6">
          <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="kicker">Workspace</p>
              <h2 className="section-title">Write your solution</h2>
            </div>
            <div className="flex flex-wrap items-center gap-2">
              <select value={language} onChange={(event) => setLanguage(event.target.value)} className="rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface-elevated)] px-3 py-2 text-sm outline-none">
                {LANGUAGE_OPTIONS.map((option) => (<option key={option} value={option}>{LANGUAGE_LABELS[option]}</option>))}
              </select>
              <span className="metric-pill">{saveState}</span>
            </div>
          </div>
          <div className="overflow-hidden rounded-[24px] border border-[var(--border-subtle)]">
            <Editor height="420px" language={language === 'javascript' ? 'javascript' : language} theme="vs-light" value={code} onChange={(value) => setCode(value || '')} options={{ minimap: { enabled: false }, fontSize: 14, lineNumbers: 'on' }} loading={<div className="flex h-[420px] items-center justify-center text-sm text-[var(--text-muted)]">Loading editor...</div>} />
          </div>
          <div className="mt-4 flex flex-wrap gap-3">
            <button onClick={handleRun} disabled={runState === 'running'} className="btn-secondary">{runState === 'running' ? 'Running...' : 'Run Code'}</button>
            <button onClick={handleSubmit} disabled={submitState === 'running'} className="btn-primary">{submitState === 'running' ? 'Evaluating submission...' : 'Submit Code'}</button>
          </div>
          {runResult && !runResult.error && (
            <div className="mt-4 rounded-[24px] border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-800">
              <div className="font-semibold">Sample results</div>
              <div className="mt-2 space-y-2">
                {runResult.results?.map((result) => (
                  <div key={result.test_case_number} className="rounded-[20px] bg-white p-2">
                    <div className="flex items-center justify-between">
                      <span>Test Case {result.test_case_number}</span>
                      <span className={result.passed ? 'text-emerald-600' : 'text-rose-600'}>{result.passed ? '✓ Passed' : '✗ Failed'}</span>
                    </div>
                    <div className="mt-1 text-xs text-[var(--text-secondary)]">
                      <div><span className="font-semibold">Input:</span> <pre className="mt-1 whitespace-pre-wrap">{result.input}</pre></div>
                      <div><span className="font-semibold">Expected:</span> <pre className="mt-1 whitespace-pre-wrap">{result.expected_output}</pre></div>
                      <div><span className="font-semibold">Actual:</span> <pre className="mt-1 whitespace-pre-wrap">{result.actual_output}</pre></div>
                      <div className="mt-1">Runtime: {result.runtime_ms ?? '—'} ms • Memory: {result.memory_kb ? `${Math.round(result.memory_kb / 1024)} MB` : '—'}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
          {runResult?.error && <div className="mt-4 rounded-[24px] border border-red-200 bg-red-50 p-3 text-sm text-red-700">{runResult.error}</div>}
          {submitResult && !submitResult.error && (
            <div className="mt-4 rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-3 text-sm text-[var(--text-secondary)]">
              <div className="text-lg font-semibold capitalize">{submitResult.verdict.toLowerCase().replace(/_/g, ' ')}</div>
              <div className="mt-1">{submitResult.message}</div>
              <div className="mt-2 text-xs text-[var(--text-muted)]">Attempt {submitResult.attempt_number} • {submitResult.passed_test_cases}/{submitResult.total_test_cases} tests passed</div>
            </div>
          )}
          {submitResult?.error && <div className="mt-4 rounded-[24px] border border-red-200 bg-red-50 p-3 text-sm text-red-700">{submitResult.error}</div>}
        </section>
        <section className="panel p-4 sm:p-6">
          <div className="mb-4">
            <p className="kicker">Evidence</p>
            <h2 className="section-title">Sample cases & history</h2>
          </div>
          {sampleCases.length === 0 ? (<div className="body-copy">No sample cases available yet.</div>) : (
            <>
              <div className="mb-3 flex flex-wrap gap-2">
                {sampleCases.map((sample, index) => (<button key={sample.id} onClick={() => setActiveCase(index)} className={`rounded-full px-3 py-1 text-sm ${activeCase === index ? 'bg-[var(--brand-primary)] text-white' : 'bg-[var(--surface-elevated)] text-[var(--text-secondary)]'}`}>Case {index + 1}</button>))}
              </div>
              <div className="space-y-3 rounded-[24px] bg-[var(--surface-elevated)] p-3 text-sm text-[var(--text-secondary)]">
                <div><h3 className="mb-1 font-semibold text-[var(--text-primary)]">Input</h3><pre className="whitespace-pre-wrap rounded-[20px] bg-[var(--surface)] p-3">{sampleCases[activeCase].input_data}</pre></div>
                <div><h3 className="mb-1 font-semibold text-[var(--text-primary)]">Expected Output</h3><pre className="whitespace-pre-wrap rounded-[20px] bg-[var(--surface)] p-3">{sampleCases[activeCase].expected_output}</pre></div>
                <div><h3 className="mb-1 font-semibold text-[var(--text-primary)]">Explanation</h3><p>{sampleCases[activeCase].explanation}</p></div>
              </div>
            </>
          )}
          <div className="mt-4 rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-3 text-sm text-[var(--text-secondary)]">
            <div className="font-semibold text-[var(--text-primary)]">Submission history</div>
            {submissions.length === 0 ? (<div className="mt-2 text-xs text-[var(--text-muted)]">No submissions yet.</div>) : (<div className="mt-2 space-y-2">{submissions.map((submission) => (<div key={submission.submission_id} className="rounded-[20px] bg-[var(--surface)] p-2 text-xs"><div className="flex items-center justify-between"><span>#{submission.attempt_number}</span><span className="font-semibold">{submission.verdict}</span></div><div className="mt-1 text-[var(--text-muted)]">{submission.language} • {submission.passed_test_cases}/{submission.total_test_cases} tests</div><div className="mt-2 space-y-3"><AICodeReviewPanel submissionId={submission.submission_id} /><AIAssistancePanel taskKey="ERROR_EXPLANATION" submissionId={submission.submission_id} /><AIAssistancePanel taskKey="SKILL_GAP" submissionId={submission.submission_id} /><AIAssistancePanel taskKey="ROADMAP" submissionId={submission.submission_id} /></div></div>))}</div>)}
          </div>
        </section>
      </div>
    </DashboardLayout>
  );
}
