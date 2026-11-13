import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useAuthStore } from '@/store/authStore'
import AppLayout from '@/components/layout/AppLayout'
import LoginPage from '@/pages/LoginPage'
import RegisterPage from '@/pages/RegisterPage'
import DashboardPage from '@/pages/DashboardPage'
import LeadsPage from '@/pages/LeadsPage'
import DealsPage from '@/pages/DealsPage'
import ConversationsPage from '@/pages/ConversationsPage'
import TasksPage from '@/pages/TasksPage'
import WorkflowsPage from '@/pages/WorkflowsPage'
import AnalyticsPage from '@/pages/AnalyticsPage'
import IntegrationsPage from '@/pages/IntegrationsPage'

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: 1, staleTime: 30000 } },
})

function RequireAuth({ children }: { children: React.ReactNode }) {
  const token = useAuthStore((s) => s.token)
  if (!token) return <Navigate to="/login" replace />
  return <>{children}</>
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route
            path="/"
            element={
              <RequireAuth>
                <AppLayout />
              </RequireAuth>
            }
          >
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<DashboardPage />} />
            <Route path="leads" element={<LeadsPage />} />
            <Route path="deals" element={<DealsPage />} />
            <Route path="conversations" element={<ConversationsPage />} />
            <Route path="tasks" element={<TasksPage />} />
            <Route path="workflows" element={<WorkflowsPage />} />
            <Route path="analytics" element={<AnalyticsPage />} />
            <Route path="integrations" element={<IntegrationsPage />} />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}
