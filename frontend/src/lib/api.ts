import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || ''

export const api = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('crm_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('crm_token')
      localStorage.removeItem('crm_user')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

// Auth
export const authApi = {
  register: (data: { email: string; password: string; full_name: string; org_name: string }) =>
    api.post('/api/v1/auth/register', data),
  login: (data: { email: string; password: string }) =>
    api.post('/api/v1/auth/login', data),
  me: () => api.get('/api/v1/auth/me'),
}

// Leads
export const leadsApi = {
  list: (orgId: string, params?: Record<string, unknown>) =>
    api.get('/api/v1/leads', { params: { organization_id: orgId, ...params } }),
  get: (id: string) => api.get(`/api/v1/leads/${id}`),
  create: (data: Record<string, unknown>) => api.post('/api/v1/leads', data),
  update: (id: string, data: Record<string, unknown>) => api.patch(`/api/v1/leads/${id}`, data),
  delete: (id: string) => api.delete(`/api/v1/leads/${id}`),
  qualify: (id: string) => api.post(`/api/v1/ai/leads/${id}/qualify`),
}

// Deals
export const dealsApi = {
  list: (orgId: string, params?: Record<string, unknown>) =>
    api.get('/api/v1/deals', { params: { organization_id: orgId, ...params } }),
  get: (id: string) => api.get(`/api/v1/deals/${id}`),
  create: (data: Record<string, unknown>) => api.post('/api/v1/deals', data),
  update: (id: string, data: Record<string, unknown>) => api.patch(`/api/v1/deals/${id}`, data),
  delete: (id: string) => api.delete(`/api/v1/deals/${id}`),
  moveStage: (id: string, stage: string) =>
    api.post(`/api/v1/deals/${id}/move-stage`, null, { params: { stage } }),
}

// Conversations
export const conversationsApi = {
  list: (orgId: string, params?: Record<string, unknown>) =>
    api.get('/api/v1/conversations', { params: { organization_id: orgId, ...params } }),
  get: (id: string) => api.get(`/api/v1/conversations/${id}`),
  create: (data: Record<string, unknown>) => api.post('/api/v1/conversations', data),
  messages: (id: string) => api.get(`/api/v1/conversations/${id}/messages`),
  addMessage: (id: string, data: Record<string, unknown>) =>
    api.post(`/api/v1/conversations/${id}/messages`, data),
  approveMessage: (convId: string, msgId: string) =>
    api.post(`/api/v1/conversations/${convId}/messages/${msgId}/approve`),
  suggestReply: (id: string) => api.post(`/api/v1/ai/conversations/${id}/suggest-reply`),
  summarize: (id: string) => api.post(`/api/v1/ai/conversations/${id}/summarize`),
}

// Tasks
export const tasksApi = {
  list: (orgId: string, params?: Record<string, unknown>) =>
    api.get('/api/v1/tasks', { params: { organization_id: orgId, ...params } }),
  create: (data: Record<string, unknown>) => api.post('/api/v1/tasks', data),
  update: (id: string, data: Record<string, unknown>) => api.patch(`/api/v1/tasks/${id}`, data),
  delete: (id: string) => api.delete(`/api/v1/tasks/${id}`),
  notifications: (orgId: string) =>
    api.get('/api/v1/tasks/notifications', { params: { organization_id: orgId } }),
  markRead: (id: string) => api.post(`/api/v1/tasks/notifications/${id}/read`),
}

// Analytics
export const analyticsApi = {
  dashboard: (orgId: string) =>
    api.get('/api/v1/analytics/dashboard', { params: { organization_id: orgId } }),
}

// Workflows
export const workflowsApi = {
  list: (orgId: string) =>
    api.get('/api/v1/workflows', { params: { organization_id: orgId } }),
  create: (data: Record<string, unknown>) => api.post('/api/v1/workflows', data),
  updateStatus: (id: string, status: string) =>
    api.patch(`/api/v1/workflows/${id}/status`, null, { params: { status } }),
  executions: (id: string) => api.get(`/api/v1/workflows/${id}/executions`),
}

// Integrations
export const integrationsApi = {
  list: (orgId: string) =>
    api.get('/api/v1/integrations', { params: { organization_id: orgId } }),
  create: (data: Record<string, unknown>) => api.post('/api/v1/integrations', data),
  test: (id: string) => api.post(`/api/v1/integrations/${id}/test`),
}
