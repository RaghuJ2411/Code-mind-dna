import { useEffect, useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import DashboardLayout from '../../layouts/DashboardLayout';
import { listAdminUsers, updateAdminUser } from '../../api/admin';

const roleOptions = ['STUDENT', 'MENTOR', 'RECRUITER', 'ADMIN'];

export default function UserManagementPage() {
  const { user: currentUser } = useAuth();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [role, setRole] = useState('');
  const [isActive, setIsActive] = useState('');
  const [message, setMessage] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const pageSize = 10;

  const fetchUsers = async (nextPage = 1) => {
    setLoading(true);
    try {
      const params = {
        search: search || undefined,
        role: role || undefined,
        is_active: isActive === '' ? undefined : isActive === 'true',
        page: nextPage,
        page_size: pageSize,
      };
      const response = await listAdminUsers(params);
      setUsers(response.items || []);
      setPage(response.page || nextPage);
      setTotalPages(response.total_pages || 1);
    } catch (err) {
      setMessage('Unable to load users.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers(page);
  }, []);

  const handleRefresh = () => {
    fetchUsers(page);
  };

  const handleFilter = () => {
    setPage(1);
    fetchUsers(1);
  };

  const handleToggleActive = async (user) => {
    try {
      await updateAdminUser(user.id, { is_active: !user.is_active });
      setMessage(`Updated ${user.email}`);
      fetchUsers(page);
    } catch (err) {
      setMessage(err?.response?.data?.detail || 'Unable to update user.');
    }
  };

  const handleRoleChange = async (user, newRole) => {
    try {
      await updateAdminUser(user.id, { role: newRole });
      setMessage(`Updated ${user.email} role to ${newRole}`);
      fetchUsers(page);
    } catch (err) {
      setMessage(err?.response?.data?.detail || 'Unable to update user role.');
    }
  };

  return (
    <DashboardLayout title="User Management" role="ADMIN">
      <div className="space-y-4">
        {message ? <div className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface)] p-3 text-sm text-[var(--text-secondary)]">{message}</div> : null}
        <section className="panel p-6">
          <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="kicker">Admin operations</p>
              <h2 className="section-title">User management</h2>
              <p className="mt-1 body-copy">Search and update user roles and activation state.</p>
            </div>
            <button onClick={handleRefresh} className="btn-primary">Refresh</button>
          </div>

          <div className="grid gap-3 md:grid-cols-4">
            <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search name or email" className="rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] px-3 py-2 text-sm outline-none" />
            <select value={role} onChange={(event) => setRole(event.target.value)} className="rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] px-3 py-2 text-sm outline-none">
              <option value="">All roles</option>
              {roleOptions.map((option) => (<option key={option} value={option}>{option}</option>))}
            </select>
            <select value={isActive} onChange={(event) => setIsActive(event.target.value)} className="rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] px-3 py-2 text-sm outline-none">
              <option value="">All statuses</option>
              <option value="true">Active</option>
              <option value="false">Inactive</option>
            </select>
            <button onClick={handleFilter} className="btn-primary">Apply</button>
          </div>

          <div className="mt-4 overflow-x-auto">
            <table className="min-w-full divide-y divide-[var(--border-subtle)] text-sm">
              <thead className="bg-[var(--surface-elevated)] text-left text-[var(--text-muted)]">
                <tr>
                  <th className="px-4 py-3">Name</th>
                  <th className="px-4 py-3">Email</th>
                  <th className="px-4 py-3">Role</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Created</th>
                  <th className="px-4 py-3">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--border-subtle)] bg-[var(--surface)]">
                {loading ? (
                  <tr><td colSpan="6" className="px-4 py-6 text-center text-[var(--text-muted)]">Loading users...</td></tr>
                ) : users.length === 0 ? (
                  <tr><td colSpan="6" className="px-4 py-6 text-center text-[var(--text-muted)]">No users found.</td></tr>
                ) : (
                  users.map((user) => (
                    <tr key={user.id} className="hover:bg-[var(--surface-elevated)]">
                      <td className="px-4 py-3 font-medium text-[var(--text-primary)]">{user.full_name}</td>
                      <td className="px-4 py-3 text-[var(--text-secondary)]">{user.email}</td>
                      <td className="px-4 py-3">
                        <select value={user.role} onChange={(event) => handleRoleChange(user, event.target.value)} className="rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] px-2 py-1 text-sm outline-none" disabled={user.id === currentUser?.id}>
                          {roleOptions.map((option) => (<option key={option} value={option}>{option}</option>))}
                        </select>
                      </td>
                      <td className="px-4 py-3 text-[var(--text-secondary)]">{user.is_active ? 'Active' : 'Inactive'}</td>
                      <td className="px-4 py-3 text-[var(--text-muted)]">{new Date(user.created_at).toLocaleString()}</td>
                      <td className="px-4 py-3">
                        <button onClick={() => handleToggleActive(user)} disabled={user.id === currentUser?.id} className={`rounded-2xl px-3 py-1 text-xs font-semibold text-white ${user.id === currentUser?.id ? 'cursor-not-allowed bg-slate-400' : 'bg-[var(--brand-primary)]'}`}>
                          {user.is_active ? 'Deactivate' : 'Activate'}
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          <div className="mt-4 flex items-center justify-between text-sm text-[var(--text-secondary)]">
            <div>Page {page} of {totalPages}</div>
            <div className="flex items-center gap-2">
              <button onClick={() => fetchUsers(Math.max(page - 1, 1))} disabled={page <= 1} className="rounded-2xl border border-[var(--border-subtle)] px-3 py-2 text-sm disabled:cursor-not-allowed disabled:opacity-50">Prev</button>
              <button onClick={() => fetchUsers(Math.min(page + 1, totalPages))} disabled={page >= totalPages} className="rounded-2xl border border-[var(--border-subtle)] px-3 py-2 text-sm disabled:cursor-not-allowed disabled:opacity-50">Next</button>
            </div>
          </div>
        </section>
      </div>
    </DashboardLayout>
  );
}
