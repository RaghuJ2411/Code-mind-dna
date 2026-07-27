import React, { useEffect, useState } from 'react';
import DashboardLayout from '../../layouts/DashboardLayout';
import { getRecruiterSettings, updateRecruiterSettings } from '../../api/recruiter';

export default function RecruiterSettingsPage() {
  const [profile, setProfile] = useState({ full_name: '', email: '', notifications: true, theme: 'light', language: 'English' });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    const load = async () => {
      try {
        const data = await getRecruiterSettings();
        if (data) {
          setProfile({
            full_name: data.full_name || '',
            email: data.email || '',
            notifications: data.notifications !== false,
            theme: data.theme || 'light',
            language: data.language || 'English',
          });
        }
        setError('');
      } catch (err) {
        setError(err?.response?.data?.detail || 'Unable to load settings.');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const handleSave = async () => {
    setSaving(true);
    try {
      await updateRecruiterSettings(profile);
      setSuccess('Settings saved successfully.');
      setError('');
    } catch (err) {
      setError(err?.response?.data?.detail || 'Unable to save settings.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <DashboardLayout title="Settings" role="RECRUITER">
      <div className="space-y-6">
        {success ? <div className="rounded-[24px] border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-700">{success}</div> : null}
        {error ? <div className="rounded-[24px] border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">{error}</div> : null}
        <section className="panel p-6">
          <div>
            <p className="kicker">Workspace settings</p>
            <h2 className="section-title">Recruiter profile and preferences</h2>
          </div>
          {loading ? <div className="mt-6 h-40 animate-pulse rounded-[24px] bg-[var(--surface-elevated)]" /> : (
            <div className="mt-6 space-y-6">
              <div className="grid gap-4 md:grid-cols-2">
                <div><label className="block text-sm font-medium">Full name</label><input className="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm" value={profile.full_name} onChange={(e) => setProfile({ ...profile, full_name: e.target.value })} /></div>
                <div><label className="block text-sm font-medium">Email</label><input className="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm" value={profile.email} onChange={(e) => setProfile({ ...profile, email: e.target.value })} /></div>
                <div><label className="block text-sm font-medium">Language</label><select className="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm" value={profile.language} onChange={(e) => setProfile({ ...profile, language: e.target.value })}><option>English</option><option>Spanish</option><option>French</option></select></div>
              </div>
              <div className="flex flex-wrap gap-4">
                <label className="flex items-center gap-2 text-sm"><input type="checkbox" checked={profile.notifications} onChange={(e) => setProfile({ ...profile, notifications: e.target.checked })} /> Enable notifications</label>
              </div>
              <button className="btn-primary" onClick={handleSave} disabled={saving}>{saving ? 'Saving...' : 'Save Settings'}</button>
            </div>
          )}
        </section>
      </div>
    </DashboardLayout>
  );
}

