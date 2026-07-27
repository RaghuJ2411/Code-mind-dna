import React, { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';

function BellIcon({ className = 'h-4 w-4' }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" className={className}>
      <path d="M15 17h5l-1.4-1.4a2 2 0 0 1-.6-1.4V11a5 5 0 0 0-3-4.4V5a2 2 0 0 0-4 0v1.6A5 5 0 0 0 5 11v3.2a2 2 0 0 1-.6 1.4L3 17h5" />
      <path d="M10 19a2 2 0 0 0 4 0" />
    </svg>
  );
}

function CheckIcon({ className = 'h-4 w-4' }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" className={className}>
      <path d="m5 12 4 4 10-10" />
    </svg>
  );
}

export default function NotificationCenter({ notifications = [], onMarkRead, onClearAll }) {
  const [open, setOpen] = useState(false);

  const unreadCount = useMemo(() => notifications.filter((item) => !item.read).length, [notifications]);

  return (
    <div className="relative">
      <button
        type="button"
        className="relative rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-2 text-[var(--text-secondary)]"
        onClick={() => setOpen((current) => !current)}
        aria-label="Open notifications"
      >
        <BellIcon className="h-5 w-5" />
        {unreadCount > 0 ? (
          <span className="absolute -right-1 -top-1 min-h-5 min-w-5 rounded-full bg-rose-500 px-1 text-center text-[10px] font-semibold leading-5 text-white">
            {unreadCount}
          </span>
        ) : null}
      </button>

      {open ? (
        <div className="absolute right-0 mt-2 w-80 max-w-[calc(100vw-2rem)] rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface)] p-4 shadow-[0_20px_60px_rgba(15,23,42,0.18)]">
          <div className="flex items-center justify-between gap-3">
            <div>
              <p className="text-sm font-semibold text-[var(--text-primary)]">Notifications</p>
              <p className="text-xs text-[var(--text-muted)]">Role-aware updates and next actions</p>
            </div>
            {notifications.length > 0 ? (
              <button type="button" className="text-xs font-medium text-[var(--brand-primary)]" onClick={onClearAll}>
                Clear all
              </button>
            ) : null}
          </div>

          <div className="mt-4 space-y-3">
            {notifications.length === 0 ? (
              <div className="rounded-2xl border border-dashed border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-3 text-sm text-[var(--text-secondary)]">
                No updates yet. Your next action will appear here.
              </div>
            ) : (
              notifications.map((item) => (
                <div key={item.id} className={`rounded-2xl border p-3 ${item.read ? 'border-[var(--border-subtle)] bg-[var(--surface-elevated)]' : 'border-[var(--brand-primary)]/30 bg-[var(--surface)]'}`}>
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--text-muted)]">{item.type}</p>
                      <p className="mt-1 text-sm font-semibold text-[var(--text-primary)]">{item.title}</p>
                      <p className="mt-1 text-sm text-[var(--text-secondary)]">{item.explanation}</p>
                    </div>
                    {!item.read ? (
                      <button type="button" className="rounded-full border border-[var(--border-subtle)] p-1 text-[var(--text-muted)]" onClick={() => onMarkRead?.(item.id)} aria-label={`Mark ${item.title} as read`}>
                        <CheckIcon className="h-4 w-4" />
                      </button>
                    ) : null}
                  </div>
                  <div className="mt-3 flex items-center justify-between gap-2">
                    <span className="text-xs text-[var(--text-muted)]">{new Date(item.timestamp).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })}</span>
                    {item.route ? (
                      <Link to={item.route} className="text-sm font-semibold text-[var(--brand-primary)]" onClick={() => setOpen(false)}>
                        Open
                      </Link>
                    ) : null}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      ) : null}
    </div>
  );
}
