import { useEffect, useState } from 'react';
import DashboardLayout from '../../layouts/DashboardLayout';
import { listMentorNotifications, markNotificationRead, markAllNotificationsRead, createMentorNotification, listMentorStudents } from '../../api/mentor';

export default function MentorNotificationsPage() {
  const [notifications, setNotifications] = useState([]);
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [filter, setFilter] = useState('');
  const [form, setForm] = useState({ title: '', message: '', notification_type: 'INFO', student_ids: [] });

  const load = async () => {
    setLoading(true);
    try {
      const [notifData, studentData] = await Promise.all([listMentorNotifications(), listMentorStudents()]);
      setNotifications(notifData || []);
      setStudents(studentData || []);
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to load notifications');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      await createMentorNotification(form);
      setShowForm(false);
      setForm({ title: '', message: '', notification_type: 'INFO', student_ids: [] });
      await load();
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to create notification');
    }
  };

  const filtered = notifications.filter((n) => !filter || n.notification_type === filter);
  const unreadCount = notifications.filter((n) => !n.is_read).length;

  return (
    <DashboardLayout title="Notifications" role="MENTOR">
      <div className="space-y-6">
        {error && <div className="rounded-[24px] border border-red-200 bg-red-50 p-4 text-sm text-red-600">{error}</div>}

        <section className="panel p-6">
          <div className="flex items-center justify-between gap-3">
            <div>
              <p className="kicker">Notifications</p>
              <h2 className="section-title">Notification Center</h2>
              <p className="mt-1 body-copy">Manage and send notifications to students.</p>
            </div>
            <div className="flex gap-2">
              <span className="metric-pill">{unreadCount} unread</span>
              <button onClick={() => markAllNotificationsRead().then(load)} className="btn-secondary">Mark All Read</button>
              <button onClick={() => setShowForm(!showForm)} className="btn-primary">{showForm ? 'Cancel' : 'Send'}</button>
            </div>
          </div>

          <div className="mt-4 flex flex-wrap gap-2">
            {['', 'INFO', 'WARNING', 'ALERT', 'SUCCESS'].map((t) => (
              <button key={t} onClick={() => setFilter(t)} className={`rounded-full px-3 py-1.5 text-xs font-medium ${filter === t ? 'bg-[var(--brand-primary)] text-white' : 'bg-[var(--surface-elevated)] text-[var(--text-secondary)]'}`}>{t || 'All'}</button>
            ))}
          </div>

          {showForm && (
            <form onSubmit={handleCreate} className="mt-6 space-y-4 rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-6">
              <div className="grid gap-4 md:grid-cols-2">
                <div className="md:col-span-2">
                  <input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} placeholder="Notification title" className="w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] px-4 py-2.5 text-sm outline-none" required />
                </div>
                <div className="md:col-span-2">
                  <textarea value={form.message} onChange={(e) => setForm({ ...form, message: e.target.value })} placeholder="Notification message" rows={3} className="w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] px-4 py-2.5 text-sm outline-none" required />
                </div>
                <div>
                  <select value={form.notification_type} onChange={(e) => setForm({ ...form, notification_type: e.target.value })} className="w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] px-4 py-2.5 text-sm outline-none">
                    <option value="INFO">Info</option>
                    <option value="WARNING">Warning</option>
                    <option value="ALERT">Alert</option>
                    <option value="SUCCESS">Success</option>
                  </select>
                </div>
              </div>
              <button type="submit" className="btn-primary">Send Notification</button>
            </form>
          )}

          {loading ? (
            <div className="mt-4 space-y-3">{[1, 2, 3].map((i) => <div key={i} className="h-16 animate-pulse rounded-[24px] bg-[var(--surface-elevated)]" />)}</div>
          ) : filtered.length === 0 ? (
            <div className="mt-6 rounded-[24px] border border-dashed border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-6 text-center text-sm text-[var(--text-secondary)]">No notifications.</div>
          ) : (
            <div className="mt-4 space-y-2">
              {filtered.map((n) => (
                <div key={n.id} className={`rounded-[24px] border p-4 transition ${n.is_read ? 'border-[var(--border-subtle)] bg-[var(--surface-elevated)]' : 'border-[var(--brand-primary)]/30 bg-[var(--brand-primary)]/5'}`}>
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${
                          n.notification_type === 'WARNING' ? 'bg-amber-100 text-amber-700' :
                          n.notification_type === 'ALERT' ? 'bg-red-100 text-red-700' :
                          n.notification_type === 'SUCCESS' ? 'bg-emerald-100 text-emerald-700' :
                          'bg-blue-100 text-blue-700'
                        }`}>{n.notification_type}</span>
                        <p className="font-medium text-[var(--text-primary)]">{n.title}</p>
                      </div>
                      <p className="mt-1 text-sm text-[var(--text-secondary)]">{n.message}</p>
                      <p className="mt-1 text-xs text-[var(--text-muted)]">{new Date(n.created_at).toLocaleString()}</p>
                    </div>
                    {!n.is_read && (
                      <button onClick={() => markNotificationRead(n.id).then(load)} className="rounded-2xl bg-[var(--brand-primary)] px-3 py-1.5 text-xs text-white">Mark Read</button>
                    )}
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

