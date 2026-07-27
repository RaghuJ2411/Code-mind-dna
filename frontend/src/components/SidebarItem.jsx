import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';


export default function SidebarItem({ item, active, collapsed }) {
  return (
    <motion.li
      layout
      whileHover={{ y: -2, scale: 1.01 }}
      transition={{ duration: 0.24, ease: 'easeOut' }}
    >
      <Link
        to={item.to}
        aria-label={item.label}
        aria-current={active ? 'page' : undefined}
        className={`group flex items-center gap-3 rounded-[24px] px-3 py-3 transition-all duration-300 ${
          active
            ? 'bg-sky-100 shadow-[0_18px_45px_rgba(37,99,235,0.18)]'
            : 'bg-white hover:bg-sky-50/80 hover:shadow-[0_18px_45px_rgba(15,23,42,0.08)]'
        }`}
      >
        <span
          className={`flex h-11 w-11 items-center justify-center rounded-2xl transition-colors duration-300 ${
            active ? 'bg-blue-600 text-white shadow-[0_12px_30px_rgba(37,99,235,0.16)]' : 'bg-white text-slate-600'
          }`}
        >
          <item.icon className="h-5 w-5" />
        </span>

        <span className={`text-sm font-semibold text-slate-800 transition-all duration-300 ${collapsed ? 'hidden' : 'block'}`}>
          {item.label}
        </span>
      </Link>
    </motion.li>
  );
}
