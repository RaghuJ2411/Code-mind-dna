import { useEffect, useState } from 'react';
import DashboardLayout from '../../layouts/DashboardLayout';
import { getMentorProfile, updateMentorProfile, uploadMentorPhoto } from '../../api/mentor';

export default function MentorProfilePage() {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState('');
  const [form, setForm] = useState({ full_name: '', title: '', department: '', bio: '', expertise: [], phone: '' });
  const [expertiseInput, setExpertiseInput] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    const load = async () => {
      try {
        const data = await getMentorProfile();
        setProfile(data);
        setForm({
          full_name: data.full_name || '',
          title: data.title || '',
          department: data.department || '',
          bio: data.bio || '',
          expertise: data.expertise || [],
          phone: data.phone || '',
        });
      } catch (err) {
        setError(err?.response?.data?.detail || 'Failed to load profile');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const updated = await updateMentorProfile(form);
      setProfile(updated);
      setSuccess('Profile updated');
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to update');
    } finally {
      setSaving(false);
    }
  };

  const handlePhoto = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    try {
      await uploadMentorPhoto(file);
      const updated = await getMentorProfile();
      setProfile(updated);
      setSuccess('Photo updated');
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to upload photo');
    }
  };

  return (
    <DashboardLayout title="Profile" role="MENTOR">
      <div className="space-y-6">
        {error && <div className="rounded-[24px] border border-red-200 bg-red-50 p-4 text-sm text-red-600">{error}</div>}
        {success && <div className="rounded-[24px] border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-700">{success}</div>}

        <section className="panel p-6">
          <p className="kicker">Mentor Profile</p>
          <h2 className="section-title">Professional Profile</h2>

          {loading ? (
            <div className="mt-4 space-y-4">{[1, 2, 3].map((i) => <div key={i} className="h-12 animate-pulse rounded-2xl bg-[var(--surface-elevated)]" />)}</div>
          ) : (
            <form onSubmit={handleSave} className="mt-6 space-y-4">
              <div className="flex items-center gap-4">
                <div className="flex h-16 w-16 items-center justify-center rounded-full bg-[var(--brand-primary)] text-2xl font-bold text-white">
                  {profile?.full_name?.charAt(0) || 'M'}
                </div>
                <div>
                  <label className="btn-secondary cursor-pointer">
                    <input type="file" accept="image/*" onChange={handlePhoto} className="hidden" />
                    Change Photo
                  </label>
                </div>
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <label className="block text-sm font-medium text-[var(--text-secondary)]">Full Name</label>
                  <input value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} className="mt-1 w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface-elevated)] px-4 py-2.5 text-sm outline-none focus:border-[var(--brand-primary)]" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-[var(--text-secondary)]">Title</label>
                  <input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} placeholder="e.g., Senior Software Engineer" className="mt-1 w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface-elevated)] px-4 py-2.5 text-sm outline-none focus:border-[var(--brand-primary)]" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-[var(--text-secondary)]">Department</label>
                  <input value={form.department} onChange={(e) => setForm({ ...form, department: e.target.value })} placeholder="e.g., Computer Science" className="mt-1 w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface-elevated)] px-4 py-2.5 text-sm outline-none focus:border-[var(--brand-primary)]" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-[var(--text-secondary)]">Phone</label>
                  <input value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} className="mt-1 w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface-elevated)] px-4 py-2.5 text-sm outline-none focus:border-[var(--brand-primary)]" />
                </div>
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-[var(--text-secondary)]">Bio</label>
                  <textarea value={form.bio} onChange={(e) => setForm({ ...form, bio: e.target.value })} rows={3} className="mt-1 w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface-elevated)] px-4 py-2.5 text-sm outline-none focus:border-[var(--brand-primary)]" />
                </div>
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-[var(--text-secondary)]">Expertise Areas</label>
                  <div className="mt-1 flex gap-2">
                    <input value={expertiseInput} onChange={(e) => setExpertiseInput(e.target.value)} placeholder="Add expertise area" className="flex-1 rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface-elevated)] px-4 py-2.5 text-sm outline-none focus:border-[var(--brand-primary)]" />
                    <button type="button" onClick={() => { if (expertiseInput.trim()) { setForm({ ...form, expertise: [...form.expertise, expertiseInput.trim()] }); setExpertiseInput(''); } }} className="rounded-2xl bg-[var(--brand-primary)] px-4 py-2 text-sm text-white">Add</button>
                  </div>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {form.expertise.map((e) => (
                      <span key={e} className="rounded-full bg-[var(--brand-primary)]/10 px-3 py-1 text-xs text-[var(--brand-primary)]">
                        {e} <button type="button" onClick={() => setForm({ ...form, expertise: form.expertise.filter((x) => x !== e) })} className="ml-1">×</button>
                      </span>
                    ))}
                  </div>
                </div>
              </div>
              <button type="submit" disabled={saving} className="btn-primary">{saving ? 'Saving...' : 'Save Profile'}</button>
            </form>
          )}
        </section>
      </div>
    </DashboardLayout>
  );
}

