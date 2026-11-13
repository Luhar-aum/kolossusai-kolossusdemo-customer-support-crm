import { create } from 'zustand'

const THEME_KEY = 'customer-support-crm-theme'

type Theme = 'light' | 'dark'

interface ThemeState {
  theme: Theme
  toggleTheme: () => void
  setTheme: (theme: Theme) => void
}

function applyTheme(theme: Theme) {
  if (theme === 'dark') {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }
  localStorage.setItem(THEME_KEY, theme)
}

const initialTheme: Theme = (() => {
  const saved = localStorage.getItem(THEME_KEY) as Theme | null
  if (saved === 'light' || saved === 'dark') return saved
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'dark'
})()

export const useThemeStore = create<ThemeState>((set) => ({
  theme: initialTheme,
  toggleTheme: () =>
    set((state) => {
      const next: Theme = state.theme === 'dark' ? 'light' : 'dark'
      applyTheme(next)
      return { theme: next }
    }),
  setTheme: (theme) => {
    applyTheme(theme)
    set({ theme })
  },
}))
