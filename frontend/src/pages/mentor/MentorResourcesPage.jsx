import { useEffect, useState } from 'react';
import DashboardLayout from '../../layouts/DashboardLayout';
import { listMentorResources, createMentorResource, deleteMentorResource } from '../../api/mentor';

export default function MentorResourcesPage() {
  const [resources, setResources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [search, setSearch] = useState('');
  const [form, setForm] = useState({ title: '', description: '', resource_type: 'ARTICLE', url: '', content: '', tags: [], difficulty: 'INTERMEDIATE', category: 'GENERAL' });
  const [tagInput, setTagInput] = useState('');

  const load = async () => {
    setLoading(true);
    try {
      const data = await listMentorResources({ search });
      setResources(data || []);
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to load resources');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [search]);

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      await createMentorResource(form);
      setShowForm(false);
      setForm({ title: '', description: '', resource_type: 'ARTICLE', url: '', content: '', tags: [], difficulty: 'INTERMEDIATE', category: 'GENERAL' });
      await load();
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to create resource');
    }
  };

  return (
    <DashboardLayout title="Resources" role="MENTOR">
      <div className="space-y-6">
        {error && <div className="rounded-[24px] border border-red-200 bg-red-50 p-4 text-sm text-red-600">{error}</div>}

        <section className="panel p-6">
          <div className="flex items-center justify-between gap-3">
            <div>
              <p className="kicker">Learning Resources</p>
              <h2 className="section-title">Resource Library</h2>
              <p className="mt-1 body-copy">Curate and share learning materials with your students.</p>
            </div>
            <button onClick={() => setShowForm(!showForm)} className="btn-primary">{showForm ? 'Cancel' : 'Add Resource'}</button>
          </div>

          <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search resources..." className="mt-4 w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface-elevated)] px-4 py-2.5 text-sm outline-none focus:border-[var(--brand-primary)]" />

          {showForm && (
            <form onSubmit={handleCreate} className="mt-6 space-y-4 rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-6">
              <div className="grid gap-4 md:grid-cols-2">
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-[var(--text-secondary)]">Title *</label>
                  <input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} className="mt-1 w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] px-4 py-2.5 text-sm outline-none" required />
                </div>
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-[var(--text-secondary)]">Description</label>
                  <textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} rows={3} className="mt-1 w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] px-4 py-2.5 text-sm outline-none" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-[var(--text-secondary)]">Type</label>
                  <select value={form.resource_type} onChange={(e) => setForm({ ...form, resource_type: e.target.value })} className="mt-1 w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] px-4 py-2.5 text-sm outline-none">
                    <option value="ARTICLE">Article</option>
                    <option value="VIDEO">Video</option>
                    <option value="COURSE">Course</option>
                    <option value="BOOK">Book</option>
                    <option value="TOOL">Tool</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-[var(--text-secondary)]">Difficulty</label>
                  <select value={form.difficulty} onChange={(e) => setForm({ ...form, difficulty: e.target.value })} className="mt-1 w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] px-4 py-2.5 text-sm outline-none">
                    <option value="BEGINNER">Beginner</option>
                    <option value="INTERMEDIATE">Intermediate</option>
                    <option value="ADVANCED">Advanced</option>
                  </select>
                </div>
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-[var(--text-secondary)]">URL</label>
                  <input value={form.url} onChange={(e) => setForm({ ...form, url: e.target.value })} className="mt-1 w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] px-4 py-2.5 text-sm outline-none" />
                </div>
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-[var(--text-secondary)]">Content</label>
                  <textarea value={form.content} onChange={(e) => setForm({ ...form, content: e.target.value })} rows={4} className="mt-1 w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] px-4 py-2.5 text-sm outline-none" />
                </div>
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-[var(--text-secondary)]">Tags</label>
                  <div className="flex gap-2">
                    <input value={tagInput} onChange={(e) => setTagInput(e.target.value)} className="flex-1 rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] px-4 py-2.5 text-sm outline-none" />
                    <button type="button" onClick={() => { if (tagInput.trim()) { setForm({ ...form, tags: [...form.tags, tagInput.trim()] }); setTagInput(''); } }} className="rounded-2xl bg-[var(--brand-primary)] px-4 py-2 text-sm text-white">Add</button>
                  </div>
                  {form.tags.length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-2">
                      {form.tags.map((t) => <span key={t} className="rounded-full bg-[var(--brand-primary)]/10 px-3 py-1 text-xs text-[var(--brand-primary)]">{t} <button type="button" onClick={() => setForm({ ...form, tags: form.tags.filter((x) => x !== t) })}>×</button></span>)}
                    </div>
                  )}
                </div>
              </div>
              <button type="submit" className="btn-primary">Add Resource</button>
            </form>
          )}

          {loading ? (
            <div className="mt-4 grid gap-4 md:grid-cols-2">{[1, 2, 3].map((i) => <div key={i} className="h-32 animate-pulse rounded-[24px] bg-[var(--surface-elevated)]" />)}</div>
          ) : resources.length === 0 ? (
            <div className="mt-6 rounded-[24px] border border-dashed border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-6 text-center text-sm text-[var(--text-secondary)]">No resources found.</div>
          ) : (
            <div className="mt-4 grid gap-4 md:grid-cols-2">
              {resources.map((r) => (
                <div key={r.id} className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-5">
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <span className="rounded-full bg-[var(--brand-primary)]/10 px-2.5 py-1 text-xs text-[var(--brand-primary)]">{r.resource_type}</span>
                      <p className="mt-2 font-semibold text-[var(--text-primary)]">{r.title}</p>
                      {r.description && <p className="mt-1 text-sm text-[var(--text-secondary)]">{r.description}</p>}
                    </div>
                    <button onClick={() => deleteMentorResource(r.id).then(load)} className="text-xs text-rose-500 hover:text-rose-600">Delete</button>
                  </div>
                  <div className="mt-3 flex flex-wrap gap-1">
                    {r.tags?.map((t) => <span key={t} className="rounded-full bg-[var(--surface-interactive)] px-2 py-0.5 text-xs text-[var(--text-muted)]">{t}</span>)}
                  </div>
                  <div className="mt-2 flex items-center gap-2 text-xs text-[var(--text-muted)]">
                    <span>{r.difficulty}</span>
                    <span>{r.category}</span>
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

