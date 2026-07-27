import { useEffect, useState } from 'react';
import DashboardLayout from '../../layouts/DashboardLayout';
import { listPermissions, updateRolePermissions } from '../../api/admin';

export default function PermissionsPage() {
  const [roles, setRoles] = useState([]);
  const [allPermissions, setAllPermissions] = useState([]);
  const [selectedRole, setSelectedRole] = useState(null);
  const [selectedPerms, setSelectedPerms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    listPermissions()
      .then((data) => {
        setRoles(data.roles || []);
        setAllPermissions(data.all_permissions || []);
      })
      .catch(() => setMessage('Unable to load permissions.'))
      .finally(() => setLoading(false));
  }, []);

  const handleSelectRole = (role) => {
    setSelectedRole(role);
    setSelectedPerms([...role.permissions]);
  };

  const togglePermission = (perm) => {
    setSelectedPerms((prev) =>
      prev.includes(perm) ? prev.filter((p) => p !== perm) : [...prev, perm]
    );
  };

  const handleSave = async () => {
    if (!selectedRole) return;
    setSaving(true);
    try {
      const updated = await updateRolePermissions(selectedRole.role, { permissions: selectedPerms });
      setRoles((prev) => prev.map((r) => r.role === updated.role ? { ...r, permissions: updated.permissions } : r));
      setMessage(`Permissions updated for ${selectedRole.role}.`);
    } catch {
      setMessage('Unable to update permissions.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <DashboardLayout title="Roles & Permissions" role="ADMIN">
      <div className="space-y-6">
        {message && <div className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface)] p-3 text-sm text-[var(--text-secondary)]">{message}</div>}

        <section className="panel p-6">
          <p className="kicker">Access control</p>
          <h2 className="section-title">Role permissions</h2>
          <p className="mt-2 body-copy">Manage what each role can access in the platform.</p>

          {loading ? (
            <div className="mt-4 h-48 animate-pulse rounded-[24px] bg-[var(--surface-elevated)]" />
          ) : (
            <div className="mt-6 grid gap-6 xl:grid-cols-[1fr_2fr]">
              <div className="space-y-2">
                <p className="text-sm font-semibold text-[var(--text-secondary)]">Roles</p>
                {roles.map((role) => (
                  <button
                    key={role.role}
                    onClick={() => handleSelectRole(role)}
                    className={`w-full rounded-[24px] border px-4 py-3 text-left text-sm transition ${
                      selectedRole?.role === role.role
                        ? 'border-[var(--brand-primary)] bg-[var(--brand-primary)]/10 text-[var(--brand-primary)]'
                        : 'border-[var(--border-subtle)] bg-[var(--surface-elevated)] text-[var(--text-primary)]'
                    }`}
                  >
                    <span className="font-semibold">{role.role}</span>
                    <span className="ml-2 text-[var(--text-muted)]">({role.permissions.length} permissions)</span>
                  </button>
                ))}
              </div>

              <div>
                {selectedRole ? (
                  <>
                    <div className="mb-3 flex items-center justify-between">
                      <p className="text-sm font-semibold text-[var(--text-secondary)]">{selectedRole.role} permissions</p>
                      <button onClick={handleSave} disabled={saving} className="btn-primary text-xs">
                        {saving ? 'Saving...' : 'Save changes'}
                      </button>
                    </div>
                    <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
                      {allPermissions.map((perm) => (
                        <label
                          key={perm}
                          className={`flex cursor-pointer items-center gap-2 rounded-[24px] border px-3 py-2 text-sm transition ${
                            selectedPerms.includes(perm)
                              ? 'border-[var(--brand-primary)] bg-[var(--brand-primary)]/10'
                              : 'border-[var(--border-subtle)] bg-[var(--surface)]'
                          }`}
                        >
                          <input
                            type="checkbox"
                            checked={selectedPerms.includes(perm)}
                            onChange={() => togglePermission(perm)}
                            className="h-4 w-4 rounded border-[var(--border-subtle)] text-[var(--brand-primary)]"
                          />
                          <span className="text-[var(--text-primary)]">{perm}</span>
                        </label>
                      ))}
                    </div>
                  </>
                ) : (
                  <div className="flex h-32 items-center justify-center rounded-[24px] border border-dashed border-[var(--border-subtle)] text-sm text-[var(--text-muted)]">
                    Select a role to manage permissions
                  </div>
                )}
              </div>
            </div>
          )}
        </section>
      </div>
    </DashboardLayout>
  );
}

