import {
  Home,
  Users,
  Shield,
  FileSearch,
  Activity,
  BarChart3,
  Database,
  Bot,
  FileText,
  Settings,
  UserCog,
} from 'lucide-react';

export const adminMenu = [
  { label: 'Dashboard', to: '/admin/dashboard', icon: Home },
  { label: 'Users', to: '/admin/users', icon: Users },
  { label: 'Roles & Permissions', to: '/admin/permissions', icon: Shield },
  { label: 'Problems', to: '/admin/problems', icon: FileSearch },
  { label: 'Audit Logs', to: '/admin/audit-logs', icon: Activity },
  { label: 'Platform Analytics', to: '/admin/analytics', icon: BarChart3 },
  { label: 'System Monitoring', to: '/admin/system', icon: Activity },
  { label: 'Database Health', to: '/admin/database', icon: Database },
  { label: 'AI Monitoring', to: '/admin/ai-monitoring', icon: Bot },
  { label: 'Reports', to: '/admin/reports', icon: FileText },
  { label: 'Settings', to: '/admin/settings', icon: Settings },
];

