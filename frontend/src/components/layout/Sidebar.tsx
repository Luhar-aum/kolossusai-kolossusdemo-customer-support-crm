import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard, Users, Briefcase, MessageSquare,
  CheckSquare, Zap, BarChart2, Settings, Plug, LogOut
} from 'lucide-react'
import { useAuthStore } from '@/store/authStore'
import { cn } from '@/lib/utils'

const nav = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/leads', icon: Users, label: 'Leads' },
  { to: '/deals', icon: Briefcase, label: 'Pipeline' },
  { to: '/conversations', icon: MessageSquare, label: 'Inbox' },
  { to: '/tasks', icon: CheckSquare, label: 'Tasks' },
  { to: '/workflows', icon: Zap, label: 'Workflows' },
  { to: '/analytics', icon: BarChart2, label: 'Analytics' },
  { to: '/integrations', icon: Plug, label: 'Integrations' },
]

export default function Sidebar() {
  const { logout, user, currentOrg } = useAuthStore()

  return (
    <aside className="w-64 h-screen bg-card border-r border-border flex flex-col">
      <div className="p-4 border-b border-border">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
            <span className="text-primary-foreground font-bold text-sm">C</span>
          </div>
          <div>
            <p className="font-semibold text-sm text-foreground">{currentOrg?.name || 'CRM'}</p>
            <p className="text-xs text-muted-foreground capitalize">{currentOrg?.role || 'member'}</p>
          </div>
        </div>
      </div>

      <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
        {nav.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors',
                isActive
                  ? 'bg-primary text-primary-foreground'
                  : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
              )
            }
          >
            <Icon size={16} />
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="p-3 border-t border-border">
        <div className="flex items-center gap-2 px-3 py-2 mb-1">
          <div className="w-7 h-7 rounded-full bg-primary/20 flex items-center justify-center">
            <span className="text-xs font-semibold text-primary">
              {user?.full_name?.[0]?.toUpperCase() || 'U'}
            </span>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-xs font-medium text-foreground truncate">{user?.full_name}</p>
            <p className="text-xs text-muted-foreground truncate">{user?.email}</p>
          </div>
        </div>
        <button
          onClick={logout}
          className="w-full flex items-center gap-3 px-3 py-2 rounded-md text-sm text-muted-foreground hover:bg-accent hover:text-accent-foreground transition-colors"
        >
          <LogOut size={16} />
          Sign out
        </button>
      </div>
    </aside>
  )
}
