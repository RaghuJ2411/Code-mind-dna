import React, { useEffect, useState } from 'react';
import DashboardLayout from '../../layouts/DashboardLayout';
import LoadingState from '../../components/LoadingState';
import RecruiterEmptyState from '../../components/RecruiterEmptyState';
import { listRecruiterConversations, sendRecruiterMessage, listRecruiterCandidates } from '../../api/recruiter';

export default function RecruiterMessagesPage() {
  const [conversations, setConversations] = useState([]);
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState('');
  const [form, setForm] = useState({ recipient_id: '', subject: '', body: '' });

  const loadData = async () => {
    setLoading(true);
    try {
      const [convData, candidatesData] = await Promise.all([
        listRecruiterConversations(),
        listRecruiterCandidates(),
      ]);
      setConversations(convData);
      setCandidates(candidatesData);
      setError('');
    } catch (err) {
      setError(err?.response?.data?.detail || 'Unable to load messages.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleSend = async (e) => {
    e.preventDefault();
    setSending(true);
    try {
      await sendRecruiterMessage(form);
      setForm({ recipient_id: '', subject: '', body: '' });
      await loadData();
    } catch (err) {
      setError(err?.response?.data?.detail || 'Unable to send message.');
    } finally {
      setSending(false);
    }
  };

  return (
    <DashboardLayout title="Messages" role="RECRUITER">
      <div className="space-y-6">
        {error ? <div className="rounded-[24px] border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">{error}</div> : null}
        <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
          <section className="panel p-6">
            <div>
              <p className="kicker">Communication center</p>
              <h2 className="section-title">Inbox</h2>
            </div>
            {loading ? <LoadingState /> : conversations.length === 0 ? <div className="mt-6"><RecruiterEmptyState title="No conversations yet" description="Send a message to start a conversation." /></div> : <div className="mt-6 space-y-4">{conversations.map((conv) => (
              <div key={conv.id} className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-5">
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <p className="text-lg font-semibold text-[var(--text-primary)]">{conv.participant}</p>
                    <p className="mt-1 text-sm text-[var(--text-secondary)]">{conv.message}</p>
                  </div>
                  {conv.unread ? <span className="rounded-full bg-emerald-100 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-emerald-700">Unread</span> : null}
                </div>
              </div>
            ))}</div>}
          </section>

          <section className="panel p-6">
            <div>
              <p className="kicker">Compose</p>
              <h2 className="section-title">Send message</h2>
            </div>
            <form className="mt-6 space-y-4" onSubmit={handleSend}>
              <div>
                <label className="block text-sm font-medium">Recipient</label>
                <select className="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm" value={form.recipient_id} onChange={(e) => setForm({ ...form, recipient_id: e.target.value })} required>
                  <option value="">Select candidate</option>
                  {candidates.map((c) => <option key={c.id} value={c.id}>{c.full_name}</option>)}
                </select>
              </div>
              <div><label className="block text-sm font-medium">Subject</label><input className="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm" value={form.subject} onChange={(e) => setForm({ ...form, subject: e.target.value })} required /></div>
              <div><label className="block text-sm font-medium">Message</label><textarea className="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm" rows={4} value={form.body} onChange={(e) => setForm({ ...form, body: e.target.value })} required /></div>
              <button type="submit" className="btn-primary w-full" disabled={sending}>{sending ? 'Sending...' : 'Send Message'}</button>
            </form>
          </section>
        </div>
      </div>
    </DashboardLayout>
  );
}

