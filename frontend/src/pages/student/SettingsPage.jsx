import { useEffect, useState } from 'react';
import DashboardLayout from '../../layouts/DashboardLayout';
import { getProfile, updateProfile, uploadPhoto, changePassword, getSettings, updateSettings } from '../../api/settings';

const SETTINGS_TABS = ['Profile', 'Account', 'Notifications', 'Appearance', 'Privacy'];

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState('Profile');
  const [profile, setProfile] = useState(null);
  const [settings, setSettings] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState('');
  const [profileForm, setProfileForm] = useState({ full_name: '', phone: '', bio: '' });
  const [passwordForm, setPasswordForm] = useState({ current_password: '', new_password: '', confirm_password: '' });
  const [settingsForm, setSettingsForm] = useState({});
  const [photoFile, setPhotoFile] = useState(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    const loadData = async () => {
      try {
        const [profileData, settingsData] = await Promise.all([getProfile(), getSettings()]);
        setProfile(profileData);
        setSettings(settingsData);
        setProfileForm({ full_name: profileData.full_name || '', phone: profileData.phone || '', bio: profileData.bio || '' });
        setSettingsForm({
          theme: settingsData.theme,
          language: settingsData.language,
          email_notifications: settingsData.email_notifications,
          push_notifications: settingsData.push_notifications,
          sms_notifications: settingsData.sms_notifications,
          profile_visibility: settingsData.profile_visibility,
        });
      } catch (err) {
        setError(err?.response?.data?.detail || 'Failed to load settings');
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  const handleProfileSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const updated = await updateProfile(profileForm);
      setProfile(updated);
      setSuccess('Profile updated successfully');
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to update profile');
    } finally {
      setSaving(false);
    }
  };

  const handlePhotoUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    try {
      const updated = await uploadPhoto(file);
      setProfile(updated);
      setSuccess('Photo uploaded successfully');
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to upload photo');
    }
  };

  const handlePasswordChange = async (e) => {
    e.preventDefault();
    if (passwordForm.new_password !== passwordForm.confirm_password) {
      setError('New passwords do not match');
      return;
    }
    setSaving(true);
    try {
      await changePassword(passwordForm);
      setPasswordForm({ current_password: '', new_password: '', confirm_password: '' });
      setSuccess('Password changed successfully');
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to change password');
    } finally {
      setSaving(false);
    }
  };

  const handleSettingsSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const updated = await updateSettings(settingsForm);
      setSettings(updated);
      setSuccess('Settings saved');
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  return (
    <DashboardLayout title="Settings" role="STUDENT">
      <div className="space-y-6">
        {error && <div className="rounded-[24px] border border-red-200 bg-red-50 p-4 text-sm text-red-600">{error}</div>}
        {success && <div className="rounded-[24px] border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-700">{success} <button onClick={() => setSuccess('')} className="ml-2 font-semibold">Dismiss</button></div>}

        <section className="panel p-4 sm:p-6">
          <div className="flex flex-wrap gap-2">
            {SETTINGS_TABS.map((tab) => (
              <button key={tab} onClick={() => setActiveTab(tab)} className={`rounded-full px-4 py-2 text-sm font-medium transition ${activeTab === tab ? 'bg-[var(--brand-primary)] text-white' : 'bg-[var(--surface-elevated)] text-[var(--text-secondary)]'}`}>{tab}</button>
            ))}
          </div>
        </section>

        {activeTab === 'Profile' && (
          <section className="panel p-6">
            <h2 className="section-title">Profile Information</h2>
            <form onSubmit={handleProfileSave} className="mt-4 space-y-4">
              <div className="flex items-center gap-4">
                <div className="flex h-16 w-16 items-center justify-center rounded-full bg-[var(--brand-primary)] text-2xl font-bold text-white">
                  {profile?.full_name?.charAt(0) || 'U'}
                </div>
                <div>
                  <label className="btn-secondary cursor-pointer">
                    <input type="file" accept="image/*" onChange={handlePhotoUpload} className="hidden" />
                    Change Photo
                  </label>
                </div>
              </div>
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <label className="block text-sm font-medium text-[var(--text-secondary)]">Full Name</label>
                  <input value={profileForm.full_name} onChange={(e) => setProfileForm({ ...profileForm, full_name: e.target.value })} className="mt-1 w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface-elevated)] px-4 py-2.5 text-sm outline-none focus:border-[var(--brand-primary)]" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-[var(--text-secondary)]">Email</label>
                  <input value={profile?.email || ''} disabled className="mt-1 w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface-interactive)] px-4 py-2.5 text-sm text-[var(--text-muted)] outline-none" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-[var(--text-secondary)]">Phone</label>
                  <input value={profileForm.phone} onChange={(e) => setProfileForm({ ...profileForm, phone: e.target.value })} className="mt-1 w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface-elevated)] px-4 py-2.5 text-sm outline-none focus:border-[var(--brand-primary)]" />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-[var(--text-secondary)]">Bio</label>
                <textarea value={profileForm.bio} onChange={(e) => setProfileForm({ ...profileForm, bio: e.target.value })} rows={3} className="mt-1 w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface-elevated)] px-4 py-2.5 text-sm outline-none focus:border-[var(--brand-primary)]" />
              </div>
              <button type="submit" disabled={saving} className="btn-primary">{saving ? 'Saving...' : 'Save Profile'}</button>
            </form>
          </section>
        )}

        {activeTab === 'Account' && (
          <section className="panel p-6">
            <h2 className="section-title">Change Password</h2>
            <form onSubmit={handlePasswordChange} className="mt-4 space-y-4 max-w-md">
              <div>
                <label className="block text-sm font-medium text-[var(--text-secondary)]">Current Password</label>
                <input type="password" value={passwordForm.current_password} onChange={(e) => setPasswordForm({ ...passwordForm, current_password: e.target.value })} className="mt-1 w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface-elevated)] px-4 py-2.5 text-sm outline-none focus:border-[var(--brand-primary)]" required />
              </div>
              <div>
                <label className="block text-sm font-medium text-[var(--text-secondary)]">New Password</label>
                <input type="password" value={passwordForm.new_password} onChange={(e) => setPasswordForm({ ...passwordForm, new_password: e.target.value })} className="mt-1 w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface-elevated)] px-4 py-2.5 text-sm outline-none focus:border-[var(--brand-primary)]" required minLength={8} />
              </div>
              <div>
                <label className="block text-sm font-medium text-[var(--text-secondary)]">Confirm New Password</label>
                <input type="password" value={passwordForm.confirm_password} onChange={(e) => setPasswordForm({ ...passwordForm, confirm_password: e.target.value })} className="mt-1 w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface-elevated)] px-4 py-2.5 text-sm outline-none focus:border-[var(--brand-primary)]" required />
              </div>
              <button type="submit" disabled={saving} className="btn-primary">{saving ? 'Changing...' : 'Change Password'}</button>
            </form>
          </section>
        )}

        {activeTab === 'Notifications' && (
          <section className="panel p-6">
            <h2 className="section-title">Notification Preferences</h2>
            <form onSubmit={handleSettingsSave} className="mt-4 space-y-4 max-w-md">
              {[
                { key: 'email_notifications', label: 'Email Notifications', desc: 'Receive updates via email' },
                { key: 'push_notifications', label: 'Push Notifications', desc: 'Receive push notifications in browser' },
                { key: 'sms_notifications', label: 'SMS Notifications', desc: 'Receive text message updates' },
              ].map((item) => (
                <label key={item.key} className="flex items-center justify-between rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-4">
                  <div>
                    <p className="font-medium text-[var(--text-primary)]">{item.label}</p>
                    <p className="text-sm text-[var(--text-muted)]">{item.desc}</p>
                  </div>
                  <input type="checkbox" checked={settingsForm[item.key]} onChange={(e) => setSettingsForm({ ...settingsForm, [item.key]: e.target.checked })} className="h-5 w-5 rounded text-[var(--brand-primary)]" />
                </label>
              ))}
              <button type="submit" disabled={saving} className="btn-primary">{saving ? 'Saving...' : 'Save Notifications'}</button>
            </form>
          </section>
        )}

        {activeTab === 'Appearance' && (
          <section className="panel p-6">
            <h2 className="section-title">Theme & Language</h2>
            <form onSubmit={handleSettingsSave} className="mt-4 space-y-4 max-w-md">
              <div>
                <label className="block text-sm font-medium text-[var(--text-secondary)]">Theme</label>
                <select value={settingsForm.theme} onChange={(e) => setSettingsForm({ ...settingsForm, theme: e.target.value })} className="mt-1 w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface-elevated)] px-4 py-2.5 text-sm outline-none focus:border-[var(--brand-primary)]">
                  <option value="light">Light</option>
                  <option value="dark">Dark</option>
                  <option value="system">System</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-[var(--text-secondary)]">Language</label>
                <select value={settingsForm.language} onChange={(e) => setSettingsForm({ ...settingsForm, language: e.target.value })} className="mt-1 w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface-elevated)] px-4 py-2.5 text-sm outline-none focus:border-[var(--brand-primary)]">
                  <option value="en">English</option>
                  <option value="es">Spanish</option>
                  <option value="fr">French</option>
                  <option value="de">German</option>
                </select>
              </div>
              <button type="submit" disabled={saving} className="btn-primary">{saving ? 'Saving...' : 'Save Appearance'}</button>
            </form>
          </section>
        )}

        {activeTab === 'Privacy' && (
          <section className="panel p-6">
            <h2 className="section-title">Privacy & Security</h2>
            <div className="mt-4 space-y-4 max-w-md">
              <div>
                <label className="block text-sm font-medium text-[var(--text-secondary)]">Profile Visibility</label>
                <select value={settingsForm.profile_visibility} onChange={(e) => setSettingsForm({ ...settingsForm, profile_visibility: e.target.value })} className="mt-1 w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface-elevated)] px-4 py-2.5 text-sm outline-none focus:border-[var(--brand-primary)]">
                  <option value="public">Public</option>
                  <option value="private">Private</option>
                  <option value="mentors">Mentors Only</option>
                </select>
              </div>
              <div className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-[var(--text-primary)]">Two-Factor Authentication</p>
                    <p className="text-sm text-[var(--text-muted)]">{settings?.two_factor_enabled ? 'Enabled' : 'Add extra security to your account'}</p>
                  </div>
                  <span className={`rounded-full px-3 py-1 text-xs font-semibold ${settings?.two_factor_enabled ? 'bg-emerald-100 text-emerald-700' : 'bg-[var(--surface-interactive)] text-[var(--text-muted)]'}`}>{settings?.two_factor_enabled ? 'Active' : 'Off'}</span>
                </div>
              </div>
              <button onClick={handleSettingsSave} disabled={saving} className="btn-primary">{saving ? 'Saving...' : 'Save Privacy Settings'}</button>
            </div>
          </section>
        )}
      </div>
    </DashboardLayout>
  );
}

