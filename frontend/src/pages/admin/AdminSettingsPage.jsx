import { useEffect, useState } from 'react';
import DashboardLayout from '../../layouts/DashboardLayout';
import { getAdminSettings, updateAdminSettings } from '../../api/admin';

export default function AdminSettingsPage() {
  const [settings, setSettings] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');
  const [form, setForm] = useState({});

  useEffect(() => {
    let active = true;
    getAdminSettings()
      .then((data) => {
        if (active) {
          setSettings(data);
          setForm({
            allow_registration: data.allow_registration,
            default_role: data.default_role,
            session_timeout_minutes: data.session_timeout_minutes,
            max_login_attempts: data.max_login_attempts,
            maintenance_mode: data.maintenance_mode,
            ai_features_enabled: data.ai_features_enabled,
          });
        }
      })
      .catch(() => {
        if (active) setMessage('Unable to load settings.');
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => { active = false; };
  }, []);

  const handleSave = async () => {
    setSaving(true);
    try {
      const updated = await updateAdminSettings(form);
      setSettings(updated);
      setMessage('Settings updated successfully.');
    } catch {
      setMessage('Unable to update settings.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <DashboardLayout title="Settings" role="ADMIN">
      <div className="space-y-6">
        {message && <div className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface)] p-3 text-sm text-[var(--text-secondary)]">{message}</div>}

        <section className="panel p-6">
          <p className="kicker">Configuration</p>
          <h2 className="section-title">Platform settings</h2>
          <p className="mt-2 body-copy">Manage global platform configuration.</p>

          {loading ? (
            <div className="mt-4 h-64 animate-pulse rounded-[24px] bg-[var(--surface-elevated)]" />
          ) : (
            <div className="mt-6 space-y-4 max-w-lg">
              <div className="flex items-center justify-between rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] px-4 py-3">
                <span className="text-sm text-[var(--text-primary)]">Allow registration</span>
                <button
                  onClick={() => setForm((prev) => ({ ...prev, allow_registration: !prev.allow_registration }))}
                  className={`rounded-2xl px-4 py-1 text-xs font-semibold text-white ${form.allow_registration ? 'bg-green-600' : 'bg-slate-400'}`}
                >
                  {form.allow_registration ? 'Enabled' : 'Disabled'}
                </button>
              </div>

              <div className="flex items-center justify-between rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] px-4 py-3">
                <span className="text-sm text-[var(--text-primary)]">Maintenance mode</span>
                <button
                  onClick={() => setForm((prev) => ({ ...prev, maintenance_mode: !prev.maintenance_mode }))}
                  className={`rounded-2xl px-4 py-1 text-xs font-semibold text-white ${form.maintenance_mode ? 'bg-red-600' : 'bg-slate-400'}`}
                >
                  {form.maintenance_mode ? 'Active' : 'Inactive'}
                </button>
              </div>

              <div className="flex items-center justify-between rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] px-4 py-3">
                <span className="text-sm text-[var(--text-primary)]">AI features</span>
                <button
                  onClick={() => setForm((prev) => ({ ...prev, ai_features_enabled: !prev.ai_features_enabled }))}
                  className={`rounded-2xl px-4 py-1 text-xs font-semibold text-white ${form.ai_features_enabled ? 'bg-green-600' : 'bg-slate-400'}`}
                >
                  {form.ai_features_enabled ? 'Enabled' : 'Disabled'}
                </button>
              </div>

              <div className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] px-4 py-3">
                <label className="mb-1 block text-sm text-[var(--text-primary)]">Default role</label>
                <select
                  value={form.default_role}
                  onChange={(e) => setForm((prev) => ({ ...prev, default_role: e.target.value }))}
                  className="w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] px-3 py-2 text-sm outline-none"
                >
                  <option value="STUDENT">Student</option>
                  <option value="MENTOR">Mentor</option>
                  <option value="RECRUITER">Recruiter</option>
                </select>
              </div>

              <div className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] px-4 py-3">
                <label className="mb-1 block text-sm text-[var(--text-primary)]">Session timeout (minutes)</label>
                <input
                  type="number"
                  value={form.session_timeout_minutes}
                  onChange={(e) => setForm((prev) => ({ ...prev, session_timeout_minutes: Number(e.target.value) }))}
                  className="w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] px-3 py-2 text-sm outline-none"
                />
              </div>

              <div className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] px-4 py-3">
                <label className="mb-1 block text-sm text-[var(--text-primary)]">Max login attempts</label>
                <input
                  type="number"
                  value={form.max_login_attempts}
                  onChange={(e) => setForm((prev) => ({ ...prev, max_login_attempts: Number(e.target.value) }))}
                  className="w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] px-3 py-2 text-sm outline-none"
                />
              </div>

              <button onClick={handleSave} disabled={saving} className="btn-primary">
                {saving ? 'Saving...' : 'Save settings'}
              </button>
            </div>
          )}
        </section>
      </div>
    </DashboardLayout>
  );
}

