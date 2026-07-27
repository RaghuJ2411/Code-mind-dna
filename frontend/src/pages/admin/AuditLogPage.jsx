import { useEffect, useState } from 'react';
import DashboardLayout from '../../layouts/DashboardLayout';
import { listAuditLogs } from '../../api/admin';

export default function AuditLogPage() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');
  const [userEmail, setUserEmail] = useState('');
  const [path, setPath] = useState('');
  const [statusCode, setStatusCode] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const pageSize = 20;

  const fetchLogs = async (nextPage = 1) => {
    setLoading(true);
    try {
      const params = {
        page: nextPage,
        page_size: pageSize,
        user_email: userEmail || undefined,
        path: path || undefined,
        status_code: statusCode ? Number(statusCode) : undefined,
      };
      const response = await listAuditLogs(params);
      setLogs(response.items || []);
      setPage(response.page || nextPage);
      setTotalPages(response.total_pages || 1);
    } catch (err) {
      setMessage('Unable to load audit logs.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs(page);
  }, []);

  const handleFilter = () => {
    fetchLogs(1);
  };

  return (
    <DashboardLayout title="Audit Logs" role="ADMIN">
      <div className="space-y-4">
        {message ? <div className="rounded-[24px] border border-red-200 bg-red-50 p-3 text-sm text-red-700">{message}</div> : null}
        <section className="panel p-6">
          <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="kicker">Governance</p>
              <h2 className="section-title">Audit log</h2>
              <p className="mt-1 body-copy">Recent audited requests for governance and troubleshooting.</p>
            </div>
            <div className="flex flex-wrap items-center gap-2">
              <input value={userEmail} onChange={(event) => setUserEmail(event.target.value)} placeholder="User email" className="rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] px-3 py-2 text-sm outline-none" />
              <input value={path} onChange={(event) => setPath(event.target.value)} placeholder="Path" className="rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] px-3 py-2 text-sm outline-none" />
              <input type="number" value={statusCode} onChange={(event) => setStatusCode(event.target.value)} placeholder="Status code" className="rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] px-3 py-2 text-sm outline-none" />
              <button onClick={handleFilter} className="btn-primary">Filter</button>
              <button onClick={() => fetchLogs(page)} className="btn-secondary">Refresh</button>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-[var(--border-subtle)] text-sm">
              <thead className="bg-[var(--surface-elevated)] text-left text-[var(--text-muted)]">
                <tr>
                  <th className="px-4 py-3">Timestamp</th>
                  <th className="px-4 py-3">User</th>
                  <th className="px-4 py-3">Method</th>
                  <th className="px-4 py-3">Path</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Remote address</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--border-subtle)] bg-[var(--surface)]">
                {loading ? (
                  <tr><td colSpan="6" className="px-4 py-6 text-center text-[var(--text-muted)]">Loading audit logs...</td></tr>
                ) : logs.length === 0 ? (
                  <tr><td colSpan="6" className="px-4 py-6 text-center text-[var(--text-muted)]">No audit logs available.</td></tr>
                ) : (
                  logs.map((log) => (
                    <tr key={log.id} className="hover:bg-[var(--surface-elevated)]">
                      <td className="px-4 py-3 text-[var(--text-secondary)]">{new Date(log.created_at).toLocaleString()}</td>
                      <td className="px-4 py-3 text-[var(--text-secondary)]">{log.user_email || 'Anonymous'}</td>
                      <td className="px-4 py-3 text-[var(--text-secondary)]">{log.method}</td>
                      <td className="px-4 py-3 text-[var(--text-secondary)]">{log.path}</td>
                      <td className="px-4 py-3 text-[var(--text-secondary)]">{log.status_code}</td>
                      <td className="px-4 py-3 text-[var(--text-secondary)]">{log.remote_addr || 'N/A'}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          <div className="mt-4 flex items-center justify-between text-sm text-[var(--text-secondary)]">
            <div>Page {page} of {totalPages}</div>
            <div className="flex items-center gap-2">
              <button onClick={() => fetchLogs(Math.max(page - 1, 1))} disabled={page <= 1} className="rounded-2xl border border-[var(--border-subtle)] px-3 py-2 text-sm disabled:cursor-not-allowed disabled:opacity-50">Prev</button>
              <button onClick={() => fetchLogs(Math.min(page + 1, totalPages))} disabled={page >= totalPages} className="rounded-2xl border border-[var(--border-subtle)] px-3 py-2 text-sm disabled:cursor-not-allowed disabled:opacity-50">Next</button>
            </div>
          </div>
        </section>
      </div>
    </DashboardLayout>
  );
}
