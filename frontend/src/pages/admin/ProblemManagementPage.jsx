import { useEffect, useMemo, useState } from 'react';
import DashboardLayout from '../../layouts/DashboardLayout';
import { createProblem, createTestCase, getProblems, updateProblem } from '../../api/problems';

const DIFFICULTY_OPTIONS = ['EASY', 'MEDIUM', 'HARD'];
const TOPIC_OPTIONS = ['ARRAYS', 'STRINGS', 'HASHING', 'STACKS', 'SEARCHING', 'SORTING', 'RECURSION', 'TREES', 'GRAPHS', 'QUEUES', 'LINKED_LISTS', 'BACKTRACKING', 'DYNAMIC_PROGRAMMING'];

const initialForm = {
  title: '',
  slug: '',
  description: '',
  difficulty: 'EASY',
  topic: 'ARRAYS',
  constraints: '',
  input_format: '',
  output_format: '',
  starter_code: { python: '', javascript: '', java: '' },
  time_limit_ms: 1000,
  memory_limit_mb: 256,
};

export default function ProblemManagementPage() {
  const [problems, setProblems] = useState([]);
  const [form, setForm] = useState(initialForm);
  const [message, setMessage] = useState('');
  const [activeProblemId, setActiveProblemId] = useState(null);
  const [testCaseForm, setTestCaseForm] = useState({ input_data: '', expected_output: '', explanation: '', is_sample: true, order_index: 1 });
  const [filter, setFilter] = useState({ search: '', difficulty: '', topic: '' });

  const fetchProblems = async (nextFilter = filter) => {
    try {
      const response = await getProblems({ ...nextFilter, page: 1, pageSize: 50 });
      setProblems(response.items || []);
    } catch {
      setMessage('Unable to load problems.');
    }
  };

  useEffect(() => {
    fetchProblems();
  }, []);

  const handleInputChange = (event) => {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  };

  const handleStarterCodeChange = (language, value) => {
    setForm((current) => ({ ...current, starter_code: { ...current.starter_code, [language]: value } }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    try {
      const payload = {
        ...form,
        starter_code: Object.fromEntries(Object.entries(form.starter_code).filter(([, value]) => value && value.trim())),
      };
      if (activeProblemId) {
        await updateProblem(activeProblemId, payload);
        setMessage('Problem updated successfully.');
      } else {
        await createProblem(payload);
        setMessage('Problem created successfully.');
      }
      setForm(initialForm);
      setActiveProblemId(null);
      fetchProblems();
    } catch (err) {
      setMessage(err?.response?.data?.detail || 'Unable to save problem.');
    }
  };

  const handleAddTestCase = async (event) => {
    event.preventDefault();
    if (!activeProblemId) {
      setMessage('Create or select a problem first.');
      return;
    }
    try {
      await createTestCase(activeProblemId, testCaseForm);
      setMessage('Test case added successfully.');
      setTestCaseForm({ input_data: '', expected_output: '', explanation: '', is_sample: true, order_index: 1 });
    } catch (err) {
      setMessage(err?.response?.data?.detail || 'Unable to add test case.');
    }
  };

  const filteredProblems = useMemo(() => {
    return problems.filter((problem) => {
      const matchesSearch = !filter.search || problem.title.toLowerCase().includes(filter.search.toLowerCase());
      const matchesDifficulty = !filter.difficulty || problem.difficulty === filter.difficulty;
      const matchesTopic = !filter.topic || problem.topic === filter.topic;
      return matchesSearch && matchesDifficulty && matchesTopic;
    });
  }, [filter, problems]);

  return (
    <DashboardLayout title="Problem Management" role="ADMIN">
      <div className="space-y-4">
        {message ? <div className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface)] p-3 text-sm text-[var(--text-secondary)]">{message}</div> : null}
        <section className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
          <div className="panel p-4 sm:p-6">
            <div className="mb-4 flex items-center justify-between">
              <div>
                <p className="kicker">Content studio</p>
                <h2 className="section-title">Manage problems</h2>
                <p className="mt-1 body-copy">Create and edit coding problems for students.</p>
              </div>
              <button onClick={() => { setForm(initialForm); setActiveProblemId(null); }} className="btn-secondary">New problem</button>
            </div>
            <div className="mb-4 grid gap-3 md:grid-cols-3">
              <input value={filter.search} onChange={(event) => setFilter((current) => ({ ...current, search: event.target.value }))} placeholder="Search problem" className="rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] px-3 py-2 text-sm outline-none" />
              <select value={filter.difficulty} onChange={(event) => setFilter((current) => ({ ...current, difficulty: event.target.value }))} className="rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] px-3 py-2 text-sm outline-none">
                <option value="">All difficulties</option>
                {DIFFICULTY_OPTIONS.map((option) => <option key={option} value={option}>{option}</option>)}
              </select>
              <select value={filter.topic} onChange={(event) => setFilter((current) => ({ ...current, topic: event.target.value }))} className="rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] px-3 py-2 text-sm outline-none">
                <option value="">All topics</option>
                {TOPIC_OPTIONS.map((option) => <option key={option} value={option}>{option}</option>)}
              </select>
            </div>
            <div className="space-y-2">
              {filteredProblems.map((problem) => (
                <button key={problem.id} onClick={() => setActiveProblemId(problem.id)} className="flex w-full items-center justify-between rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] px-3 py-3 text-left text-sm">
                  <span className="font-semibold text-[var(--text-primary)]">{problem.title}</span>
                  <span className="text-[var(--text-muted)]">{problem.difficulty} • {problem.topic}</span>
                </button>
              ))}
            </div>
          </div>
          <div className="panel p-4 sm:p-6">
            <p className="kicker">Problem editor</p>
            <h2 className="section-title">Problem form</h2>
            <form onSubmit={handleSubmit} className="mt-4 space-y-3">
              <input name="title" value={form.title} onChange={handleInputChange} placeholder="Title" className="w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] px-3 py-2 text-sm outline-none" required />
              <input name="slug" value={form.slug} onChange={handleInputChange} placeholder="Slug" className="w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] px-3 py-2 text-sm outline-none" required />
              <textarea name="description" value={form.description} onChange={handleInputChange} placeholder="Description" className="min-h-24 w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] px-3 py-2 text-sm outline-none" required />
              <div className="grid gap-3 md:grid-cols-2">
                <select name="difficulty" value={form.difficulty} onChange={handleInputChange} className="rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] px-3 py-2 text-sm outline-none">
                  {DIFFICULTY_OPTIONS.map((option) => <option key={option} value={option}>{option}</option>)}
                </select>
                <select name="topic" value={form.topic} onChange={handleInputChange} className="rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] px-3 py-2 text-sm outline-none">
                  {TOPIC_OPTIONS.map((option) => <option key={option} value={option}>{option}</option>)}
                </select>
              </div>
              <textarea name="constraints" value={form.constraints} onChange={handleInputChange} placeholder="Constraints" className="min-h-20 w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] px-3 py-2 text-sm outline-none" required />
              <textarea name="input_format" value={form.input_format} onChange={handleInputChange} placeholder="Input Format" className="min-h-20 w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] px-3 py-2 text-sm outline-none" required />
              <textarea name="output_format" value={form.output_format} onChange={handleInputChange} placeholder="Output Format" className="min-h-20 w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] px-3 py-2 text-sm outline-none" required />
              <div className="grid gap-3 md:grid-cols-2">
                <input type="number" name="time_limit_ms" value={form.time_limit_ms} onChange={handleInputChange} className="rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] px-3 py-2 text-sm outline-none" />
                <input type="number" name="memory_limit_mb" value={form.memory_limit_mb} onChange={handleInputChange} className="rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] px-3 py-2 text-sm outline-none" />
              </div>
              <div className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-3">
                <p className="mb-2 text-sm font-semibold text-[var(--text-primary)]">Starter code</p>
                <div className="space-y-2">
                  {['python', 'javascript', 'java'].map((language) => (
                    <div key={language}>
                      <label className="mb-1 block text-sm text-[var(--text-secondary)]">{language}</label>
                      <textarea value={form.starter_code?.[language] || ''} onChange={(event) => handleStarterCodeChange(language, event.target.value)} className="min-h-20 w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] px-3 py-2 text-sm outline-none" />
                    </div>
                  ))}
                </div>
              </div>
              <button className="btn-primary">Save problem</button>
            </form>
          </div>
        </section>

        <section className="panel p-4 sm:p-6">
          <p className="kicker">Validation</p>
          <h2 className="section-title">Add test case</h2>
          <form onSubmit={handleAddTestCase} className="mt-4 grid gap-3 md:grid-cols-2">
            <textarea value={testCaseForm.input_data} onChange={(event) => setTestCaseForm((current) => ({ ...current, input_data: event.target.value }))} placeholder="Input data" className="min-h-20 rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] px-3 py-2 text-sm outline-none" required />
            <textarea value={testCaseForm.expected_output} onChange={(event) => setTestCaseForm((current) => ({ ...current, expected_output: event.target.value }))} placeholder="Expected output" className="min-h-20 rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] px-3 py-2 text-sm outline-none" required />
            <textarea value={testCaseForm.explanation} onChange={(event) => setTestCaseForm((current) => ({ ...current, explanation: event.target.value }))} placeholder="Explanation" className="min-h-20 rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] px-3 py-2 text-sm outline-none" />
            <div className="space-y-2">
              <label className="flex items-center gap-2 text-sm text-[var(--text-secondary)]">
                <input type="checkbox" checked={testCaseForm.is_sample} onChange={(event) => setTestCaseForm((current) => ({ ...current, is_sample: event.target.checked }))} />
                Mark as sample case
              </label>
              <input type="number" value={testCaseForm.order_index} onChange={(event) => setTestCaseForm((current) => ({ ...current, order_index: Number(event.target.value) }))} className="w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] px-3 py-2 text-sm outline-none" />
            </div>
            <button className="btn-primary md:col-span-2">Add test case</button>
          </form>
        </section>
      </div>
    </DashboardLayout>
  );
}
