import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { tasksApi } from '@/lib/api'
import { useAuthStore } from '@/store/authStore'
import { Plus, CheckCircle, Circle, Clock } from 'lucide-react'
import { useForm } from 'react-hook-form'
import { formatDate } from '@/lib/utils'

type Task = { id: string; title: string; description: string | null; status: string; priority: string; due_date: string | null; assigned_to: string | null }

const STATUS_ICON: Record<string, JSX.Element> = {
  todo: <Circle size={14} className="text-muted-foreground" />,
  in_progress: <Clock size={14} className="text-blue-500" />,
  completed: <CheckCircle size={14} className="text-green-500" />,
  blocked: <Circle size={14} className="text-red-500" />,
  cancelled: <Circle size={14} className="text-gray-400" />,
}

const PRIORITY_BADGE: Record<string, string> = {
  low: 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-300',
  medium: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300',
  high: 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-300',
  urgent: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300',
}

export default function TasksPage() {
  const { currentOrg } = useAuthStore()
  const qc = useQueryClient()
  const [statusFilter, setStatusFilter] = useState('')
  const [showForm, setShowForm] = useState(false)
  const { register, handleSubmit, reset } = useForm<{ title: string; description: string; due_date: string; priority: string }>()

  const { data, isLoading } = useQuery({
    queryKey: ['tasks', currentOrg?.id, statusFilter],
    queryFn: () => tasksApi.list(currentOrg!.id, { status: statusFilter, page_size: 50 }).then(r => r.data),
    enabled: !!currentOrg,
  })

  const createMutation = useMutation({
    mutationFn: (d: Record<string, unknown>) => tasksApi.create({ ...d, organization_id: currentOrg!.id }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['tasks'] }); setShowForm(false); reset() },
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, ...data }: Record<string, unknown>) => tasksApi.update(id as string, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['tasks'] }),
  })

  const tasks: Task[] = data?.data || []

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex gap-2">
          <select value={statusFilter} onChange={e => setStatusFilter(e.target.value)} className="px-3 py-2 text-sm border border-input rounded-md bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-ring">
            <option value="">All statuses</option>
            {['todo', 'in_progress', 'blocked', 'completed', 'cancelled'].map(s => <option key={s} value={s}>{s.replace('_', ' ')}</option>)}
          </select>
        </div>
        <button onClick={() => setShowForm(!showForm)} className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-md text-sm font-medium hover:bg-primary/90">
          <Plus size={14} /> New Task
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit(d => createMutation.mutate(d as Record<string, unknown>))} className="bg-card border border-border rounded-xl p-4 grid grid-cols-2 md:grid-cols-4 gap-3">
          <input {...register('title')} placeholder="Task title*" className="col-span-2 px-3 py-2 text-sm border border-input rounded-md bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring" />
          <input {...register('due_date')} type="date" className="px-3 py-2 text-sm border border-input rounded-md bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-ring" />
          <select {...register('priority')} className="px-3 py-2 text-sm border border-input rounded-md bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-ring">
            {['low', 'medium', 'high', 'urgent'].map(p => <option key={p} value={p}>{p}</option>)}
          </select>
          <textarea {...register('description')} placeholder="Description" rows={2} className="col-span-2 md:col-span-4 px-3 py-2 text-sm border border-input rounded-md bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring resize-none" />
          <div className="col-span-2 md:col-span-4 flex gap-2">
            <button type="submit" className="px-4 py-2 bg-primary text-primary-foreground rounded-md text-sm">Save</button>
            <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 border border-border rounded-md text-sm text-muted-foreground">Cancel</button>
          </div>
        </form>
      )}

      {isLoading ? (
        <div className="text-muted-foreground animate-pulse">Loading…</div>
      ) : (
        <div className="bg-card border border-border rounded-xl overflow-hidden">
          <table className="w-full text-sm">
            <thead className="border-b border-border">
              <tr className="text-muted-foreground text-xs">
                <th className="text-left px-4 py-3 font-medium w-6"></th>
                <th className="text-left px-4 py-3 font-medium">Task</th>
                <th className="text-left px-4 py-3 font-medium">Priority</th>
                <th className="text-left px-4 py-3 font-medium">Due</th>
                <th className="text-left px-4 py-3 font-medium">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {tasks.map(task => (
                <tr key={task.id} className="hover:bg-accent/30 transition-colors">
                  <td className="px-4 py-3">{STATUS_ICON[task.status] || <Circle size={14} />}</td>
                  <td className="px-4 py-3">
                    <p className={`font-medium text-foreground ${task.status === 'completed' ? 'line-through text-muted-foreground' : ''}`}>{task.title}</p>
                    {task.description && <p className="text-xs text-muted-foreground truncate max-w-xs">{task.description}</p>}
                  </td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${PRIORITY_BADGE[task.priority]}`}>{task.priority}</span>
                  </td>
                  <td className="px-4 py-3 text-muted-foreground text-xs">{task.due_date ? formatDate(task.due_date) : '—'}</td>
                  <td className="px-4 py-3">
                    <select
                      value={task.status}
                      onChange={e => updateMutation.mutate({ id: task.id, status: e.target.value })}
                      className="text-xs border border-input rounded bg-background text-foreground px-2 py-1"
                    >
                      {['todo', 'in_progress', 'blocked', 'completed', 'cancelled'].map(s => <option key={s} value={s}>{s.replace('_', ' ')}</option>)}
                    </select>
                  </td>
                </tr>
              ))}
              {tasks.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-4 py-8 text-center text-muted-foreground">No tasks found.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
