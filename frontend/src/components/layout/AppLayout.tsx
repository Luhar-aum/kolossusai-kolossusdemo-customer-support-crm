import { Outlet, useLocation } from 'react-router-dom'
import Sidebar from './Sidebar'
import Header from './Header'

const titles: Record<string, string> = {
  '/dashboard': 'Dashboard',
  '/leads': 'Leads',
  '/deals': 'Sales Pipeline',
  '/conversations': 'Customer Inbox',
  '/tasks': 'Tasks',
  '/workflows': 'Workflow Automation',
  '/analytics': 'Analytics',
  '/integrations': 'Integrations',
}

export default function AppLayout() {
  const location = useLocation()
  const title = Object.entries(titles).find(([path]) => location.pathname.startsWith(path))?.[1] || 'CRM'

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header title={title} />
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
