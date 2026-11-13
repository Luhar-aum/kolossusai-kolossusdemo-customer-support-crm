import { Sun, Moon, Bell } from 'lucide-react'
import { useThemeStore } from '@/store/themeStore'
import { useAuthStore } from '@/store/authStore'

interface HeaderProps {
  title: string
}

export default function Header({ title }: HeaderProps) {
  const { theme, toggleTheme } = useThemeStore()
  const { currentOrg } = useAuthStore()

  return (
    <header className="h-14 border-b border-border bg-card px-6 flex items-center justify-between flex-shrink-0">
      <h1 className="text-lg font-semibold text-foreground">{title}</h1>
      <div className="flex items-center gap-2">
        <button
          onClick={toggleTheme}
          className="p-2 rounded-md hover:bg-accent text-muted-foreground hover:text-accent-foreground transition-colors"
          title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
        >
          {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
        </button>
        <button className="p-2 rounded-md hover:bg-accent text-muted-foreground hover:text-accent-foreground transition-colors">
          <Bell size={18} />
        </button>
        <div className="text-xs text-muted-foreground px-2 py-1 rounded bg-secondary border border-border">
          {currentOrg?.name || '—'}
        </div>
      </div>
    </header>
  )
}
