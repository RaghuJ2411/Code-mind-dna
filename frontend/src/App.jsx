import { Navigate, Route, Routes } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import Toast from './components/Toast';
import LoginPage from './pages/auth/LoginPage';
import RegisterPage from './pages/auth/RegisterPage';
import StudentDashboard from './pages/student/StudentDashboard';
import StudentGoalsPage from './pages/student/StudentGoalsPage';
import MentorDashboard from './pages/mentor/MentorDashboard';
import MentorStudentsPage from './pages/mentor/MentorStudentsPage';
import MentorIntelligencePage from './pages/mentor/MentorIntelligencePage';
import MentorRiskAlertsPage from './pages/mentor/MentorRiskAlertsPage';
import MentorAnalyticsPage from './pages/mentor/MentorAnalyticsPage';
import MentorSessionsPage from './pages/mentor/MentorSessionsPage';
import MentorAssignmentsPage from './pages/mentor/MentorAssignmentsPage';
import MentorResourcesPage from './pages/mentor/MentorResourcesPage';
import MentorMessagesPage from './pages/mentor/MentorMessagesPage';
import MentorReportsPage from './pages/mentor/MentorReportsPage';
import MentorNotificationsPage from './pages/mentor/MentorNotificationsPage';
import MentorProfilePage from './pages/mentor/MentorProfilePage';
import AdminDashboard from './pages/admin/AdminDashboard';
import RecruiterDashboard from './pages/recruiter/RecruiterDashboard';
import RecruiterJobsPage from './pages/recruiter/RecruiterJobsPage';
import RecruiterCandidatesPage from './pages/recruiter/RecruiterCandidatesPage';
import RecruiterMatchingPage from './pages/recruiter/RecruiterMatchingPage';
import RecruiterApplicationsPage from './pages/recruiter/RecruiterApplicationsPage';
import RecruiterAnalyticsPage from './pages/recruiter/RecruiterAnalyticsPage';
import RecruiterShortlistedPage from './pages/recruiter/RecruiterShortlistedPage';
import RecruiterInterviewsPage from './pages/recruiter/RecruiterInterviewsPage';
import RecruiterMessagesPage from './pages/recruiter/RecruiterMessagesPage';
import RecruiterReportsPage from './pages/recruiter/RecruiterReportsPage';
import RecruiterCompanyPage from './pages/recruiter/RecruiterCompanyPage';
import RecruiterSettingsPage from './pages/recruiter/RecruiterSettingsPage';
import CandidateDetailPage from './pages/recruiter/CandidateDetailPage';
import JobDetailPage from './pages/recruiter/JobDetailPage';
import ProtectedRoute from './routes/ProtectedRoute';
import RoleBasedRoute from './routes/RoleBasedRoute';
import ProblemBankPage from './pages/student/ProblemBankPage';
import CodingArenaPage from './pages/student/CodingArenaPage';
import AnalyticsPage from './pages/student/AnalyticsPage';
import AIInsightsPage from './pages/student/AIInsightsPage';
import CareerPage from './pages/student/CareerPage';
import CareerRoleDetailPage from './pages/student/CareerRoleDetailPage';
import SkillDNAPage from './pages/student/SkillDNAPage';
import JobsPage from './pages/student/JobsPage';
import LearningPage from './pages/student/LearningPage';
import CodingPracticePage from './pages/student/CodingPracticePage';
import ProgressPage from './pages/student/ProgressPage';
import CareerRoadmapPage from './pages/student/CareerRoadmapPage';
import AIMentorPage from './pages/student/AIMentorPage';
import AssessmentsPage from './pages/student/AssessmentsPage';
import AchievementsPage from './pages/student/AchievementsPage';
import ApplicationsPage from './pages/student/ApplicationsPage';
import MessagesPage from './pages/student/MessagesPage';
import SettingsPage from './pages/student/SettingsPage';
import ProblemManagementPage from './pages/admin/ProblemManagementPage';
import UserManagementPage from './pages/admin/UserManagementPage';
import AuditLogPage from './pages/admin/AuditLogPage';
import AdminAnalyticsPage from './pages/admin/AdminAnalyticsPage';
import SystemHealthPage from './pages/admin/SystemHealthPage';
import DatabaseHealthPage from './pages/admin/DatabaseHealthPage';
import AIMonitoringPage from './pages/admin/AIMonitoringPage';
import AdminReportsPage from './pages/admin/AdminReportsPage';
import AdminSettingsPage from './pages/admin/AdminSettingsPage';
import PermissionsPage from './pages/admin/PermissionsPage';

function AppRoutes() {
  const { user, loading } = useAuth();
  const [toast, setToast] = useState({ message: '', visible: false });

  useEffect(() => {
    const handleSessionCleared = () => {
      setToast({ message: 'You have been logged out successfully.', visible: true });
    };
    window.addEventListener('auth:session-cleared', handleSessionCleared);
    return () => window.removeEventListener('auth:session-cleared', handleSessionCleared);
  }, []);

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center">Loading...</div>;
  }

  return (
    <>
    <Routes>
      <Route path="/" element={user ? <Navigate to={`/${user.role.toLowerCase()}/dashboard`} replace /> : <LoginPage />} />
      <Route path="/login" element={user ? <Navigate to={`/${user.role.toLowerCase()}/dashboard`} replace /> : <LoginPage />} />
      <Route path="/register" element={user ? <Navigate to={`/${user.role.toLowerCase()}/dashboard`} replace /> : <RegisterPage />} />

      <Route
        path="/student/dashboard"
        element={
          <ProtectedRoute>
            <RoleBasedRoute allowedRoles={['STUDENT']}>
              <StudentDashboard />
            </RoleBasedRoute>
          </ProtectedRoute>
        }
      />
      <Route
        path="/student/problems"
        element={
          <ProtectedRoute>
            <RoleBasedRoute allowedRoles={['STUDENT']}>
              <ProblemBankPage />
            </RoleBasedRoute>
          </ProtectedRoute>
        }
      />
      <Route
        path="/student/problems/:slug"
        element={
          <ProtectedRoute>
            <RoleBasedRoute allowedRoles={['STUDENT']}>
              <CodingArenaPage />
            </RoleBasedRoute>
          </ProtectedRoute>
        }
      />
      <Route
        path="/student/goals"
        element={
          <ProtectedRoute>
            <RoleBasedRoute allowedRoles={['STUDENT']}>
              <StudentGoalsPage />
            </RoleBasedRoute>
          </ProtectedRoute>
        }
      />
      <Route
        path="/student/analytics"
        element={
          <ProtectedRoute>
            <RoleBasedRoute allowedRoles={['STUDENT']}>
              <AnalyticsPage />
            </RoleBasedRoute>
          </ProtectedRoute>
        }
      />
      <Route
        path="/student/ai-insights"
        element={
          <ProtectedRoute>
            <RoleBasedRoute allowedRoles={['STUDENT']}>
              <AIInsightsPage />
            </RoleBasedRoute>
          </ProtectedRoute>
        }
      />
      <Route
        path="/student/career"
        element={
          <ProtectedRoute>
            <RoleBasedRoute allowedRoles={['STUDENT']}>
              <CareerPage />
            </RoleBasedRoute>
          </ProtectedRoute>
        }
      />
      <Route
        path="/student/career/roles/:roleId"
        element={
          <ProtectedRoute>
            <RoleBasedRoute allowedRoles={['STUDENT']}>
              <CareerRoleDetailPage />
            </RoleBasedRoute>
          </ProtectedRoute>
        }
      />
      <Route
        path="/student/skilldna"
        element={
          <ProtectedRoute>
            <RoleBasedRoute allowedRoles={['STUDENT']}>
              <SkillDNAPage />
            </RoleBasedRoute>
          </ProtectedRoute>
        }
      />
      <Route
        path="/student/jobs"
        element={
          <ProtectedRoute>
            <RoleBasedRoute allowedRoles={['STUDENT']}>
              <JobsPage />
            </RoleBasedRoute>
          </ProtectedRoute>
        }
      />
      <Route
        path="/student/learning"
        element={
          <ProtectedRoute>
            <RoleBasedRoute allowedRoles={['STUDENT']}>
              <LearningPage />
            </RoleBasedRoute>
          </ProtectedRoute>
        }
      />
      <Route
        path="/student/practice"
        element={
          <ProtectedRoute>
            <RoleBasedRoute allowedRoles={['STUDENT']}>
              <CodingPracticePage />
            </RoleBasedRoute>
          </ProtectedRoute>
        }
      />
      <Route
        path="/student/progress"
        element={
          <ProtectedRoute>
            <RoleBasedRoute allowedRoles={['STUDENT']}>
              <ProgressPage />
            </RoleBasedRoute>
          </ProtectedRoute>
        }
      />
      <Route
        path="/student/career-roadmap"
        element={
          <ProtectedRoute>
            <RoleBasedRoute allowedRoles={['STUDENT']}>
              <CareerRoadmapPage />
            </RoleBasedRoute>
          </ProtectedRoute>
        }
      />
      <Route
        path="/student/ai-mentor"
        element={
          <ProtectedRoute>
            <RoleBasedRoute allowedRoles={['STUDENT']}>
              <AIMentorPage />
            </RoleBasedRoute>
          </ProtectedRoute>
        }
      />
      <Route
        path="/student/assessments"
        element={
          <ProtectedRoute>
            <RoleBasedRoute allowedRoles={['STUDENT']}>
              <AssessmentsPage />
            </RoleBasedRoute>
          </ProtectedRoute>
        }
      />
      <Route
        path="/student/achievements"
        element={
          <ProtectedRoute>
            <RoleBasedRoute allowedRoles={['STUDENT']}>
              <AchievementsPage />
            </RoleBasedRoute>
          </ProtectedRoute>
        }
      />
      <Route
        path="/student/applications"
        element={
          <ProtectedRoute>
            <RoleBasedRoute allowedRoles={['STUDENT']}>
              <ApplicationsPage />
            </RoleBasedRoute>
          </ProtectedRoute>
        }
      />
      <Route
        path="/student/messages"
        element={
          <ProtectedRoute>
            <RoleBasedRoute allowedRoles={['STUDENT']}>
              <MessagesPage />
            </RoleBasedRoute>
          </ProtectedRoute>
        }
      />
      <Route
        path="/student/settings"
        element={
          <ProtectedRoute>
            <RoleBasedRoute allowedRoles={['STUDENT']}>
              <SettingsPage />
            </RoleBasedRoute>
          </ProtectedRoute>
        }
      />
      <Route path="/mentor" element={<Navigate to="/mentor/dashboard" replace />} />
      <Route
        path="/mentor/dashboard"
        element={
          <ProtectedRoute>
            <RoleBasedRoute allowedRoles={['MENTOR']}>
              <MentorDashboard />
            </RoleBasedRoute>
          </ProtectedRoute>
        }
      />
      <Route
        path="/mentor/students"
        element={
          <ProtectedRoute>
            <RoleBasedRoute allowedRoles={['MENTOR']}>
              <MentorStudentsPage />
            </RoleBasedRoute>
          </ProtectedRoute>
        }
      />
      <Route
        path="/mentor/intelligence"
        element={
          <ProtectedRoute>
            <RoleBasedRoute allowedRoles={['MENTOR']}>
              <MentorIntelligencePage />
            </RoleBasedRoute>
          </ProtectedRoute>
        }
      />
      <Route
        path="/mentor/risk-alerts"
        element={
          <ProtectedRoute>
            <RoleBasedRoute allowedRoles={['MENTOR']}>
              <MentorRiskAlertsPage />
            </RoleBasedRoute>
          </ProtectedRoute>
        }
      />
      <Route
        path="/mentor/analytics"
        element={
          <ProtectedRoute>
            <RoleBasedRoute allowedRoles={['MENTOR']}>
              <MentorAnalyticsPage />
            </RoleBasedRoute>
          </ProtectedRoute>
        }
      />
      <Route
        path="/mentor/sessions"
        element={
          <ProtectedRoute>
            <RoleBasedRoute allowedRoles={['MENTOR']}>
              <MentorSessionsPage />
            </RoleBasedRoute>
          </ProtectedRoute>
        }
      />
      <Route
        path="/mentor/assignments"
        element={
          <ProtectedRoute>
            <RoleBasedRoute allowedRoles={['MENTOR']}>
              <MentorAssignmentsPage />
            </RoleBasedRoute>
          </ProtectedRoute>
        }
      />
      <Route
        path="/mentor/resources"
        element={
          <ProtectedRoute>
            <RoleBasedRoute allowedRoles={['MENTOR']}>
              <MentorResourcesPage />
            </RoleBasedRoute>
          </ProtectedRoute>
        }
      />
      <Route
        path="/mentor/messages"
        element={
          <ProtectedRoute>
            <RoleBasedRoute allowedRoles={['MENTOR']}>
              <MentorMessagesPage />
            </RoleBasedRoute>
          </ProtectedRoute>
        }
      />
      <Route
        path="/mentor/reports"
        element={
          <ProtectedRoute>
            <RoleBasedRoute allowedRoles={['MENTOR']}>
              <MentorReportsPage />
            </RoleBasedRoute>
          </ProtectedRoute>
        }
      />
      <Route
        path="/mentor/notifications"
        element={
          <ProtectedRoute>
            <RoleBasedRoute allowedRoles={['MENTOR']}>
              <MentorNotificationsPage />
            </RoleBasedRoute>
          </ProtectedRoute>
        }
      />
      <Route
        path="/mentor/settings"
        element={
          <ProtectedRoute>
            <RoleBasedRoute allowedRoles={['MENTOR']}>
              <MentorProfilePage />
            </RoleBasedRoute>
          </ProtectedRoute>
        }
      />
      <Route path="/admin" element={<Navigate to="/admin/dashboard" replace />} />
      <Route
        path="/admin/dashboard"
        element={
          <ProtectedRoute>
            <RoleBasedRoute allowedRoles={['ADMIN']}>
              <AdminDashboard />
            </RoleBasedRoute>
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/problems"
        element={
          <ProtectedRoute>
            <RoleBasedRoute allowedRoles={['ADMIN']}>
              <ProblemManagementPage />
            </RoleBasedRoute>
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/users"
        element={
          <ProtectedRoute>
            <RoleBasedRoute allowedRoles={['ADMIN']}>
              <UserManagementPage />
            </RoleBasedRoute>
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/audit-logs"
        element={
          <ProtectedRoute>
            <RoleBasedRoute allowedRoles={['ADMIN']}>
              <AuditLogPage />
            </RoleBasedRoute>
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/analytics"
        element={
          <ProtectedRoute>
            <RoleBasedRoute allowedRoles={['ADMIN']}>
              <AdminAnalyticsPage />
            </RoleBasedRoute>
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/system"
        element={
          <ProtectedRoute>
            <RoleBasedRoute allowedRoles={['ADMIN']}>
              <SystemHealthPage />
            </RoleBasedRoute>
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/database"
        element={
          <ProtectedRoute>
            <RoleBasedRoute allowedRoles={['ADMIN']}>
              <DatabaseHealthPage />
            </RoleBasedRoute>
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/ai-monitoring"
        element={
          <ProtectedRoute>
            <RoleBasedRoute allowedRoles={['ADMIN']}>
              <AIMonitoringPage />
            </RoleBasedRoute>
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/reports"
        element={
          <ProtectedRoute>
            <RoleBasedRoute allowedRoles={['ADMIN']}>
              <AdminReportsPage />
            </RoleBasedRoute>
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/settings"
        element={
          <ProtectedRoute>
            <RoleBasedRoute allowedRoles={['ADMIN']}>
              <AdminSettingsPage />
            </RoleBasedRoute>
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/permissions"
        element={
          <ProtectedRoute>
            <RoleBasedRoute allowedRoles={['ADMIN']}>
              <PermissionsPage />
            </RoleBasedRoute>
          </ProtectedRoute>
        }
      />
      <Route
        path="/recruiter/dashboard"
        element={
          <ProtectedRoute>
            <RoleBasedRoute allowedRoles={['RECRUITER']}>
              <RecruiterDashboard />
            </RoleBasedRoute>
          </ProtectedRoute>
        }
      />
      <Route
        path="/recruiter/jobs"
        element={
          <ProtectedRoute>
            <RoleBasedRoute allowedRoles={['RECRUITER']}>
              <RecruiterJobsPage />
            </RoleBasedRoute>
          </ProtectedRoute>
        }
      />
      <Route
        path="/recruiter/candidates"
        element={
          <ProtectedRoute>
            <RoleBasedRoute allowedRoles={['RECRUITER']}>
              <RecruiterCandidatesPage />
            </RoleBasedRoute>
          </ProtectedRoute>
        }
      />
      <Route
        path="/recruiter/matching"
        element={
          <ProtectedRoute>
            <RoleBasedRoute allowedRoles={['RECRUITER']}>
              <RecruiterMatchingPage />
            </RoleBasedRoute>
          </ProtectedRoute>
        }
      />
      <Route
        path="/recruiter/applications"
        element={
          <ProtectedRoute>
            <RoleBasedRoute allowedRoles={['RECRUITER']}>
              <RecruiterApplicationsPage />
            </RoleBasedRoute>
          </ProtectedRoute>
        }
      />
      <Route
        path="/recruiter/analytics"
        element={
          <ProtectedRoute>
            <RoleBasedRoute allowedRoles={['RECRUITER']}>
              <RecruiterAnalyticsPage />
            </RoleBasedRoute>
          </ProtectedRoute>
        }
      />
      <Route
        path="/recruiter/shortlisted"
        element={
          <ProtectedRoute>
            <RoleBasedRoute allowedRoles={['RECRUITER']}>
              <RecruiterShortlistedPage />
            </RoleBasedRoute>
          </ProtectedRoute>
        }
      />
      <Route
        path="/recruiter/interviews"
        element={
          <ProtectedRoute>
            <RoleBasedRoute allowedRoles={['RECRUITER']}>
              <RecruiterInterviewsPage />
            </RoleBasedRoute>
          </ProtectedRoute>
        }
      />
      <Route
        path="/recruiter/messages"
        element={
          <ProtectedRoute>
            <RoleBasedRoute allowedRoles={['RECRUITER']}>
              <RecruiterMessagesPage />
            </RoleBasedRoute>
          </ProtectedRoute>
        }
      />
      <Route
        path="/recruiter/reports"
        element={
          <ProtectedRoute>
            <RoleBasedRoute allowedRoles={['RECRUITER']}>
              <RecruiterReportsPage />
            </RoleBasedRoute>
          </ProtectedRoute>
        }
      />
      <Route
        path="/recruiter/company"
        element={
          <ProtectedRoute>
            <RoleBasedRoute allowedRoles={['RECRUITER']}>
              <RecruiterCompanyPage />
            </RoleBasedRoute>
          </ProtectedRoute>
        }
      />
      <Route
        path="/recruiter/settings"
        element={
          <ProtectedRoute>
            <RoleBasedRoute allowedRoles={['RECRUITER']}>
              <RecruiterSettingsPage />
            </RoleBasedRoute>
          </ProtectedRoute>
        }
      />
      <Route
        path="/recruiter/candidates/:studentId"
        element={
          <ProtectedRoute>
            <RoleBasedRoute allowedRoles={['RECRUITER']}>
              <CandidateDetailPage />
            </RoleBasedRoute>
          </ProtectedRoute>
        }
      />
      <Route
        path="/recruiter/jobs/:jobId"
        element={
          <ProtectedRoute>
            <RoleBasedRoute allowedRoles={['RECRUITER']}>
              <JobDetailPage />
            </RoleBasedRoute>
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
    <Toast message={toast.message} visible={toast.visible} onClose={() => setToast({ message: '', visible: false })} />
    </>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <AppRoutes />
    </AuthProvider>
  );
}
