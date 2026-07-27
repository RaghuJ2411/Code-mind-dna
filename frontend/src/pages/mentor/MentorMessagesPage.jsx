import { useEffect, useState, useRef } from 'react';
import DashboardLayout from '../../layouts/DashboardLayout';
import { listMentorConversations, getMentorConversation, sendMentorMessage } from '../../api/mentor';

export default function MentorMessagesPage() {
  const [conversations, setConversations] = useState([]);
  const [activeConv, setActiveConv] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [sending, setSending] = useState(false);
  const [filter, setFilter] = useState('');
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    const load = async () => {
      try {
        const data = await listMentorConversations();
        setConversations(data || []);
      } catch (err) {
        setError(err?.response?.data?.detail || 'Failed to load conversations');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const handleSelect = async (convId) => {
    try {
      const data = await getMentorConversation(convId);
      setActiveConv(data);
      setMessages(data.messages || []);
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to load conversation');
    }
  };

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || !activeConv || sending) return;
    setSending(true);
    try {
      await sendMentorMessage(activeConv.id, { content: input.trim() });
      setInput('');
      const data = await getMentorConversation(activeConv.id);
      setMessages(data.messages || []);
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to send');
    } finally {
      setSending(false);
    }
  };

  const filtered = conversations.filter((c) => !filter || c.conversation_type === filter);

  return (
    <DashboardLayout title="Messages" role="MENTOR">
      <div className="flex gap-6" style={{ height: 'calc(100vh - 180px)' }}>
        <div className="w-80 shrink-0 space-y-3 overflow-y-auto">
          {error && <div className="rounded-[24px] border border-red-200 bg-red-50 p-3 text-sm text-red-600">{error}</div>}
          <div className="panel p-3">
            <p className="text-sm font-semibold text-[var(--text-primary)]">Conversations</p>
            <div className="mt-2 flex gap-1">
              {['', 'DIRECT', 'GROUP', 'MENTOR'].map((t) => (
                <button key={t} onClick={() => setFilter(t)} className={`rounded-full px-2.5 py-1 text-xs ${!filter ? 'bg-[var(--brand-primary)] text-white' : 'bg-[var(--surface-elevated)] text-[var(--text-secondary)]'}`}>{t || 'All'}</button>
              ))}
            </div>
          </div>
          {filtered.map((conv) => (
            <button key={conv.id} onClick={() => handleSelect(conv.id)} className={`w-full rounded-[24px] border p-4 text-left transition ${activeConv?.id === conv.id ? 'border-[var(--brand-primary)] bg-[var(--brand-primary)]/5' : 'border-[var(--border-subtle)] bg-[var(--surface-elevated)]'}`}>
              <div className="flex items-center justify-between gap-2">
                <p className="text-sm font-semibold text-[var(--text-primary)]">{conv.title || conv.conversation_type}</p>
                {conv.unread_count > 0 && <span className="rounded-full bg-red-500 px-2 py-0.5 text-xs text-white">{conv.unread_count}</span>}
              </div>
              {conv.last_message && <p className="mt-1 truncate text-xs text-[var(--text-muted)]">{conv.last_message}</p>}
            </button>
          ))}
          {filtered.length === 0 && !loading && <p className="text-center text-sm text-[var(--text-muted)]">No conversations.</p>}
        </div>

        <div className="flex flex-1 flex-col rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface)]">
          {activeConv ? (
            <>
              <div className="border-b border-[var(--border-subtle)] p-4">
                <p className="font-semibold text-[var(--text-primary)]">{activeConv.title || activeConv.conversation_type}</p>
                <div className="mt-1 flex flex-wrap gap-2">
                  {activeConv.participants?.map((p) => (
                    <span key={p.user_id} className="rounded-full bg-[var(--surface-elevated)] px-2.5 py-0.5 text-xs text-[var(--text-muted)]">{p.user_name} ({p.user_role})</span>
                  ))}
                </div>
              </div>
              <div className="flex-1 space-y-3 overflow-y-auto p-4">
                {messages.map((msg, i) => (
                  <div key={msg.id || i} className={`flex ${msg.sender_id === 1 ? 'justify-start' : 'justify-end'}`}>
                    <div className={`max-w-[70%] rounded-[24px] p-3 text-sm ${msg.sender_id === 1 ? 'bg-[var(--surface-elevated)] text-[var(--text-primary)]' : 'bg-[var(--brand-primary)] text-white'}`}>
                      <p className="text-xs opacity-70">{msg.sender_name || 'Unknown'}</p>
                      <pre className="mt-1 whitespace-pre-wrap font-sans">{msg.content}</pre>
                      <p className="mt-1 text-xs opacity-50">{new Date(msg.created_at).toLocaleTimeString()}</p>
                    </div>
                  </div>
                ))}
                <div ref={messagesEndRef} />
              </div>
              <form onSubmit={handleSend} className="flex gap-3 border-t border-[var(--border-subtle)] p-4">
                <input value={input} onChange={(e) => setInput(e.target.value)} placeholder="Type a message..." className="flex-1 rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface-elevated)] px-4 py-2.5 text-sm outline-none focus:border-[var(--brand-primary)]" disabled={sending} />
                <button type="submit" disabled={sending || !input.trim()} className="rounded-2xl bg-[var(--brand-primary)] px-6 py-2.5 text-sm font-semibold text-white disabled:opacity-50">{sending ? 'Sending...' : 'Send'}</button>
              </form>
            </>
          ) : (
            <div className="flex flex-1 items-center justify-center">
              <div className="text-center">
                <p className="text-4xl">💬</p>
                <p className="mt-3 font-semibold text-[var(--text-primary)]">Select a conversation</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
}

