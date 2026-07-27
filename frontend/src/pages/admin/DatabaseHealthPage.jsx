import { useEffect, useState } from 'react';
import DashboardLayout from '../../layouts/DashboardLayout';
import { getDatabaseHealth, getDatabaseTables } from '../../api/admin';

export default function DatabaseHealthPage() {
  const [health, setHealth] = useState(null);
  const [tables, setTables] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let active = true;
    setLoading(true);
    Promise.all([getDatabaseHealth(), getDatabaseTables()])
      .then(([healthData, tablesData]) => {
        if (active) {
          setHealth(healthData);
          setTables(tablesData.tables || []);
        }
      })
      .catch(() => {
        if (active) setError('Unable to load database health.');
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => { active = false; };
  }, []);

  return (
    <DashboardLayout title="Database Health" role="ADMIN">
      <div className="space-y-6">
        {error && <div className="rounded-[24px] border border-red-200 bg-red-50 p-4 text-sm text-red-700">{error}</div>}

        <section className="panel p-6">
          <p className="kicker">Database</p>
          <h2 className="section-title">Health overview</h2>
          <div className="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <div className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-4">
              <p className="text-sm text-[var(--text-muted)]">Status</p>
              <p className={`mt-2 text-2xl font-semibold ${health?.status === 'healthy' ? 'text-green-600' : 'text-red-600'}`}>
                {health?.status ?? 'Unknown'}
              </p>
            </div>
            <div className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-4">
              <p className="text-sm text-[var(--text-muted)]">Size</p>
              <p className="mt-2 text-2xl font-semibold">{health?.size_mb?.toFixed(2) ?? 0} MB</p>
            </div>
            <div className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-4">
              <p className="text-sm text-[var(--text-muted)]">Connections</p>
              <p className="mt-2 text-2xl font-semibold">{health?.connection_count ?? 0} / {health?.max_connections ?? 100}</p>
            </div>
            <div className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-4">
              <p className="text-sm text-[var(--text-muted)]">Slow queries (24h)</p>
              <p className="mt-2 text-2xl font-semibold">{health?.slow_queries_last_24h ?? 0}</p>
            </div>
          </div>
        </section>

        <section className="panel p-6">
          <p className="kicker">Schema</p>
          <h2 className="section-title">Tables</h2>
          <div className="mt-4 overflow-x-auto">
            <table className="min-w-full divide-y divide-[var(--border-subtle)] text-sm">
              <thead className="bg-[var(--surface-elevated)] text-left text-[var(--text-muted)]">
                <tr>
                  <th className="px-4 py-3">Table name</th>
                  <th className="px-4 py-3">Row count</th>
                  <th className="px-4 py-3">Size (MB)</th>
                  <th className="px-4 py-3">Indexes</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--border-subtle)] bg-[var(--surface)]">
                {loading ? (
                  <tr><td colSpan="4" className="px-4 py-6 text-center text-[var(--text-muted)]">Loading tables...</td></tr>
                ) : tables.length === 0 ? (
                  <tr><td colSpan="4" className="px-4 py-6 text-center text-[var(--text-muted)]">No tables found.</td></tr>
                ) : tables.map((table) => (
                  <tr key={table.table_name} className="hover:bg-[var(--surface-elevated)]">
                    <td className="px-4 py-3 font-medium text-[var(--text-primary)]">{table.table_name}</td>
                    <td className="px-4 py-3 text-[var(--text-secondary)]">{table.row_count.toLocaleString()}</td>
                    <td className="px-4 py-3 text-[var(--text-secondary)]">{table.size_mb.toFixed(2)}</td>
                    <td className="px-4 py-3 text-[var(--text-secondary)]">{table.index_count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </DashboardLayout>
  );
}

