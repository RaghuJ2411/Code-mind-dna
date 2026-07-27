import {
  Home,
  Briefcase,
  UserRound,
  Bot,
  FileText,
  BarChart3,
  CalendarClock,
  MessageCircle,
  Settings,
  Sparkles,
} from 'lucide-react';

export const recruiterMenu = [
  { label: 'Dashboard', to: '/recruiter/dashboard', icon: Home },
  { label: 'Jobs', to: '/recruiter/jobs', icon: Briefcase },
  { label: 'Candidates', to: '/recruiter/candidates', icon: UserRound },
  { label: 'AI Matching', to: '/recruiter/matching', icon: Bot },
  { label: 'Applications', to: '/recruiter/applications', icon: FileText },
  { label: 'Hiring Analytics', to: '/recruiter/analytics', icon: BarChart3 },
  { label: 'Shortlisted', to: '/recruiter/shortlisted', icon: Sparkles },
  { label: 'Interviews', to: '/recruiter/interviews', icon: CalendarClock },
  { label: 'Messages', to: '/recruiter/messages', icon: MessageCircle },
  { label: 'Reports', to: '/recruiter/reports', icon: BarChart3 },
  { label: 'Company Profile', to: '/recruiter/company', icon: Briefcase },
  { label: 'Settings', to: '/recruiter/settings', icon: Settings },
];
