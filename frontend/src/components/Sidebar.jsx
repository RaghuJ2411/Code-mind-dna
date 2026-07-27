import React, { useMemo, useState } from 'react';

import { motion, AnimatePresence } from 'framer-motion';
import { useLocation, useNavigate } from 'react-router-dom';
import { LogOut } from 'lucide-react';
import SidebarItem from './SidebarItem';
import LogoutModal from './LogoutModal';
import { useAuth } from '../context/AuthContext';

export default function Sidebar({ menu, role }) {
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [logoutOpen, setLogoutOpen] = useState(false);
  const [logoutLoading, setLogoutLoading] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { logout } = useAuth();

  const navItems = useMemo(() => menu, [menu]);
  const activePath = location.pathname;

  const handleLogout = async () => {
    setLogoutLoading(true);
    try {
      await logout();
      setLogoutOpen(false);
      navigate('/login', { replace: true });
    } finally {
      setLogoutLoading(false);
    }
  };

  return (
    <>
      <div className="hidden lg:block">
        <aside className={`h-screen w-[260px] overflow-hidden rounded-[32px] border border-slate-200 bg-white/90 p-4 shadow-prem backdrop-blur-xl`}> 
          <div className="mb-8 flex items-center justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.28em] text-slate-400">{role}</p>
              <h2 className="text-xl font-semibold text-slate-900">Workspace</h2>
            </div>
            <button
              onClick={() => setCollapsed((current) => !current)}
              className="rounded-2xl border border-slate-200 bg-white/90 p-2 text-slate-600 transition hover:border-slate-300 hover:text-slate-900"
              aria-label="Toggle sidebar"
            >
              {collapsed ? '→' : '←'}
            </button>
          </div>

          <ul className="space-y-3">
            {navItems.map((item) => (
              <SidebarItem
                key={item.label}
                item={item}
                active={activePath === item.to}
                collapsed={collapsed}
              />
            ))}
          </ul>

          <motion.button
            type="button"
            initial={{ opacity: 0.98 }}
            whileHover={{ scale: 1.01, y: -1 }}
            onClick={() => setLogoutOpen(true)}
            className="mt-6 flex w-full items-center gap-3 rounded-[24px] border border-rose-200 bg-rose-50 px-3 py-3 text-left text-sm font-semibold text-rose-700 transition hover:bg-rose-100"
          >
            <span className="flex h-11 w-11 items-center justify-center rounded-2xl bg-rose-600 text-white">
              <LogOut className="h-5 w-5" />
            </span>
            <span className={`${collapsed ? 'hidden' : 'block'}`}>Logout</span>
          </motion.button>
          <LogoutModal open={logoutOpen} onClose={() => setLogoutOpen(false)} onConfirm={handleLogout} loading={logoutLoading} />
        </aside>
      </div>

      <div className="lg:hidden">
        <button
          onClick={() => setMobileOpen(true)}
          className="fixed bottom-6 right-6 z-50 rounded-full bg-blue-600 p-4 text-white shadow-[0_20px_60px_rgba(37,99,235,0.25)]"
          aria-label="Open navigation"
        >
          ☰
        </button>
        <AnimatePresence>
          {mobileOpen ? (
            <motion.aside
              initial={{ x: '100%' }}
              animate={{ x: 0 }}
              exit={{ x: '100%' }}
              transition={{ duration: 0.3, ease: 'easeOut' }}
              className="fixed inset-y-0 right-0 z-50 w-[260px] overflow-auto rounded-l-[32px] border border-slate-200 bg-white/95 p-5 shadow-prem backdrop-blur-xl"
            >
              <div className="mb-6 flex items-center justify-between">
                <div>
                  <p className="text-xs uppercase tracking-[0.28em] text-slate-400">{role}</p>
                  <h2 className="text-lg font-semibold text-slate-900">Menu</h2>
                </div>
                <button onClick={() => setMobileOpen(false)} className="text-slate-500" aria-label="Close navigation">
                  ✕
                </button>
              </div>
              <ul className="space-y-3">
                {navItems.map((item) => (
                  <SidebarItem
                    key={item.label}
                    item={item}
                    active={activePath === item.to}
                    collapsed={false}
                  />
                ))}
              </ul>
              <motion.button
                type="button"
                whileHover={{ scale: 1.01, y: -1 }}
                onClick={() => setLogoutOpen(true)}
                className="mt-6 flex w-full items-center gap-3 rounded-[24px] border border-rose-200 bg-rose-50 px-3 py-3 text-left text-sm font-semibold text-rose-700 transition hover:bg-rose-100"
              >
                <span className="flex h-11 w-11 items-center justify-center rounded-2xl bg-rose-600 text-white">
                  <LogOut className="h-5 w-5" />
                </span>
                <span>Logout</span>
              </motion.button>
              <LogoutModal open={logoutOpen} onClose={() => setLogoutOpen(false)} onConfirm={handleLogout} loading={logoutLoading} />
            </motion.aside>
          ) : null}
        </AnimatePresence>
      </div>
    </>
  );
}
