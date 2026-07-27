import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export default function LogoutModal({ open, onClose, onConfirm, loading }) {
  return (
    <AnimatePresence>
      {open ? (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-[60] flex items-center justify-center bg-slate-950/60 p-4"
        >
          <motion.div
            initial={{ y: 16, opacity: 0, scale: 0.98 }}
            animate={{ y: 0, opacity: 1, scale: 1 }}
            exit={{ y: 8, opacity: 0, scale: 0.98 }}
            transition={{ duration: 0.2 }}
            className="w-full max-w-md rounded-[28px] border border-slate-200 bg-white p-6 shadow-[0_30px_80px_rgba(15,23,42,0.2)]"
          >
            <p className="text-xs uppercase tracking-[0.28em] text-rose-500">Logout</p>
            <h3 className="mt-3 text-xl font-semibold text-slate-900">Are you sure you want to logout from CodeMind DNA?</h3>
            <p className="mt-3 text-sm text-slate-600">You will be signed out from your current workspace and need to sign in again to continue.</p>
            <div className="mt-6 flex justify-end gap-3">
              <button type="button" className="rounded-2xl border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700" onClick={onClose}>
                Cancel
              </button>
              <button type="button" className="rounded-2xl bg-rose-600 px-4 py-2 text-sm font-semibold text-white shadow-[0_12px_30px_rgba(220,38,38,0.2)]" onClick={onConfirm} disabled={loading}>
                {loading ? 'Logging out…' : 'Logout'}
              </button>
            </div>
          </motion.div>
        </motion.div>
      ) : null}
    </AnimatePresence>
  );
}
