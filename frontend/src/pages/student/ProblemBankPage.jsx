import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import DashboardLayout from '../../layouts/DashboardLayout';
import { getProblems } from '../../api/problems';

const DIFFICULTY_OPTIONS = ['EASY', 'MEDIUM', 'HARD'];
const TOPIC_OPTIONS = ['ARRAYS', 'STRINGS', 'HASHING', 'STACKS', 'SEARCHING', 'SORTING', 'RECURSION', 'TREES', 'GRAPHS', 'QUEUES', 'LINKED_LISTS', 'BACKTRACKING', 'DYNAMIC_PROGRAMMING'];

export default function ProblemBankPage() {
  const [filters, setFilters] = useState({ search: '', difficulty: '', topic: '' });
  const [problems, setProblems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [pagination, setPagination] = useState({ page: 1, page_size: 12, total: 0, total_pages: 1 });
  const navigate = useNavigate();

  const fetchProblems = async (nextFilters = filters, page = 1) => {
    try {
      setLoading(true);
      const response = await getProblems({ ...nextFilters, page, pageSize: 12 });
      setProblems(response.items || []);
      setPagination({
        page: response.page || 1,
        page_size: response.page_size || 12,
        total: response.total || 0,
        total_pages: response.total_pages || 1,
      });
      setError('');
    } catch (err) {
      setError(err?.response?.data?.detail || 'Unable to load problem bank right now.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProblems(filters, 1);
  }, []);

  const handleSearch = (event) => {
    const value = event.target.value;
    setFilters((current) => ({ ...current, search: value }));
    fetchProblems({ ...filters, search: value }, 1);
  };

  const handleFilterChange = (event) => {
    const { name, value } = event.target;
    const nextFilters = { ...filters, [name]: value };
    setFilters(nextFilters);
    fetchProblems(nextFilters, 1);
  };

  const clearFilters = () => {
    const nextFilters = { search: '', difficulty: '', topic: '' };
    setFilters(nextFilters);
    fetchProblems(nextFilters, 1);
  };

  const pages = useMemo(() => Array.from({ length: pagination.total_pages }, (_, index) => index + 1), [pagination.total_pages]);

  return (
    <DashboardLayout title="Problem Bank" role="STUDENT">
      <div className="space-y-6">
        <section className="panel p-5 sm:p-6">
          <div className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <p className="kicker">Practice library</p>
              <h2 className="section-title">Browse coding challenges</h2>
              <p className="mt-1 body-copy">Search, filter, and select the next challenge that matches your current growth focus.</p>
            </div>
            <div className="metric-pill">{pagination.total} problems available</div>
          </div>
          <div className="mt-5 grid gap-3 md:grid-cols-3">
            <label className="text-sm text-[var(--text-secondary)]">
              <span className="mb-1 block">Search</span>
              <input value={filters.search} onChange={handleSearch} placeholder="Search title or keyword" className="w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface-elevated)] px-3 py-2.5 outline-none transition focus:border-[var(--brand-primary)]" />
            </label>
            <label className="text-sm text-[var(--text-secondary)]">
              <span className="mb-1 block">Difficulty</span>
              <select name="difficulty" value={filters.difficulty} onChange={handleFilterChange} className="w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface-elevated)] px-3 py-2.5 outline-none transition focus:border-[var(--brand-primary)]">
                <option value="">All difficulties</option>
                {DIFFICULTY_OPTIONS.map((option) => (
                  <option key={option} value={option}>{option}</option>
                ))}
              </select>
            </label>
            <label className="text-sm text-[var(--text-secondary)]">
              <span className="mb-1 block">Topic</span>
              <select name="topic" value={filters.topic} onChange={handleFilterChange} className="w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface-elevated)] px-3 py-2.5 outline-none transition focus:border-[var(--brand-primary)]">
                <option value="">All topics</option>
                {TOPIC_OPTIONS.map((option) => (
                  <option key={option} value={option}>{option}</option>
                ))}
              </select>
            </label>
          </div>
          <div className="mt-4">
            <button onClick={clearFilters} className="btn-secondary">Clear filters</button>
          </div>
        </section>

        {loading ? (
          <div className="space-y-3">
            {[1, 2, 3].map((item) => (<div key={item} className="h-24 animate-pulse rounded-[24px] bg-[var(--surface)] shadow-sm" />))}
          </div>
        ) : error ? (
          <div className="panel p-4 text-sm text-red-600">{error}</div>
        ) : problems.length === 0 ? (
          <div className="panel p-8 text-center body-copy">No problems match your current filters yet.</div>
        ) : (
          <div className="panel overflow-hidden">
            <div className="hidden grid-cols-[2fr_1fr_1fr_auto] gap-4 border-b border-[var(--border-subtle)] px-4 py-3 text-sm font-semibold text-[var(--text-muted)] md:grid">
              <div>Problem</div>
              <div>Difficulty</div>
              <div>Topic</div>
              <div />
            </div>
            <div className="divide-y divide-[var(--border-subtle)]">
              {problems.map((problem) => (
                <div key={problem.id} className="grid gap-3 px-4 py-4 md:grid-cols-[2fr_1fr_1fr_auto] md:items-center">
                  <div>
                    <h3 className="text-base font-semibold text-[var(--text-primary)]">{problem.title}</h3>
                    <p className="mt-1 text-sm text-[var(--text-muted)]">{problem.slug}</p>
                  </div>
                  <div className="text-sm text-[var(--text-secondary)]">{problem.difficulty}</div>
                  <div className="text-sm text-[var(--text-secondary)]">{problem.topic}</div>
                  <div className="flex items-center gap-2">
                    <span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${problem.status === 'SOLVED' ? 'bg-emerald-100 text-emerald-700' : problem.status === 'ATTEMPTED' ? 'bg-amber-100 text-amber-700' : 'bg-[var(--surface-elevated)] text-[var(--text-secondary)]'}`}>
                      {problem.status === 'SOLVED' ? '✓ Solved' : problem.status === 'ATTEMPTED' ? '◐ Attempted' : '○ New'}
                    </span>
                    <button onClick={() => navigate(`/student/problems/${problem.slug}`)} className="btn-primary">Solve</button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="flex flex-wrap gap-2">
          {pages.map((page) => (
            <button key={page} onClick={() => fetchProblems(filters, page)} className={`rounded-2xl px-3 py-2 text-sm ${pagination.page === page ? 'bg-[var(--brand-primary)] text-white' : 'bg-[var(--surface)] text-[var(--text-secondary)] border border-[var(--border-subtle)]'}`}>
              {page}
            </button>
          ))}
        </div>
      </div>
    </DashboardLayout>
  );
}
