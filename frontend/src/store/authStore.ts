import { create } from 'zustand'

interface Organization {
  id: string
  name: string
  slug: string
  role: string
}

interface User {
  id: string
  email: string
  full_name: string
  organizations: Organization[]
}

interface AuthState {
  user: User | null
  currentOrg: Organization | null
  token: string | null
  setAuth: (user: User, token: string) => void
  setCurrentOrg: (org: Organization) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  user: (() => {
    try { return JSON.parse(localStorage.getItem('crm_user') || 'null') } catch { return null }
  })(),
  currentOrg: (() => {
    try { return JSON.parse(localStorage.getItem('crm_org') || 'null') } catch { return null }
  })(),
  token: localStorage.getItem('crm_token'),

  setAuth: (user, token) => {
    localStorage.setItem('crm_token', token)
    localStorage.setItem('crm_user', JSON.stringify(user))
    const org = user.organizations[0] || null
    if (org) localStorage.setItem('crm_org', JSON.stringify(org))
    set({ user, token, currentOrg: org })
  },

  setCurrentOrg: (org) => {
    localStorage.setItem('crm_org', JSON.stringify(org))
    set({ currentOrg: org })
  },

  logout: () => {
    localStorage.removeItem('crm_token')
    localStorage.removeItem('crm_user')
    localStorage.removeItem('crm_org')
    set({ user: null, token: null, currentOrg: null })
  },
}))
