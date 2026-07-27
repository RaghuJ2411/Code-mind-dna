import React, { useMemo } from 'react';
import Sidebar from './Sidebar';

import { adminMenu } from '../config/adminMenu';
import { mentorMenu } from '../config/mentorMenu';
import { recruiterMenu } from '../config/recruiterMenu';
import { studentMenu } from '../config/studentMenu';

export default function RoleSidebar({ role }) {
  const menu = useMemo(() => {
    switch (role) {
      case 'ADMIN':
        return adminMenu;
      case 'MENTOR':
        return mentorMenu;
      case 'RECRUITER':
        return recruiterMenu;
      case 'STUDENT':
        return studentMenu;
      default:
        return [];
    }
  }, [role]);

  return <Sidebar menu={menu} role={role} />;
}
