import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { workflowsApi } from '@/lib/api'
import { useAuthStore } from '@/store/authStore'
import { Plus, Play, Pause, Zap } from 'lucide-react'
import { useForm } from 'react-hook-form'

type Workflow = { id: string; name: string; description: string | null; trigger_type: string; status: string; created_at: string }

const TRIGGERS = ['new_lead', 'lead_status_changed', 'deal_stage_changed', 'task_overdue', 'new_message', 'scheduled', 'webhook']

export default function WorkflowsPage() {
  const { currentOrg } = useAuthStore()
  const qc = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const { register, handleSubmit, reset } = useForm<{ name: string; description: string; trigger_type: string }>()

  const { data, isLoading } = useQuery({
    queryKey: ['workflows', currentOrg?.id],
    queryFn: () => workflowsApi.list(currentOrg!.id).then(r => r.data),
    enabled: !!currentOrg,
  })

  const createMutation = useMutation({
    mutationFn: (d: Record<string, unknown>) => workflowsApi.create({ ...d, organization_id: currentOrg!.id }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['workflows'] }); setShowForm(false); reset() },
  })

  const statusMutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) => workflowsApi.updateStatus(id, status),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['workflows'] }),
  })

  const workflows: Workflow[] = data || []

  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        <button onClick={() => setShowForm(!showForm)} className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-md text-sm font-medium hover:bg-primary/90">
          <Plus size={14} /> New Workflow
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit(d => createMutation.mutate(d as Record<string, unknown>))} className="bg-card border border-border rounded-xl p-4 space-y-3">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <input {...register('name')} placeholder="Workflow name*" className="px-3 py-2 text-sm border border-input rounded-md bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring" />
            <input {...register('description')} placeholder="Description" className="px-3 py-2 text-sm border border-input rounded-md bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring" />
            <select {...register('trigger_type')} className="px-3 py-2 text-sm border border-input rounded-md bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-ring">
              {TRIGGERS.map(t => <option key={t} value={t}>{t.replace(/_/g, ' ')}</option>)}
            </select>
          </div>
          <div className="flex gap-2">
            <button type="submit" className="px-4 py-2 bg-primary text-primary-foreground rounded-md text-sm">Create</button>
            <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 border border-border rounded-md text-sm text-muted-foreground">Cancel</button>
          </div>
        </form>
      )}

      {isLoading ? (
        <div className="text-muted-foreground animate-pulse">Loading…</div>
      ) : (
        <div className="grid gap-3">
          {workflows.map(wf => (
            <div key={wf.id} className="bg-card border border-border rounded-xl p-4 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${wf.status === 'active' ? 'bg-green-100 dark:bg-green-900/30' : 'bg-secondary'}`}>
                  <Zap size={16} className={wf.status === 'active' ? 'text-green-600 dark:text-green-400' : 'text-muted-foreground'} />
                </div>
                <div>
                  <p className="font-medium text-foreground text-sm">{wf.name}</p>
                  <p className="text-xs text-muted-foreground">Trigger: {wf.trigger_type.replace(/_/g, ' ')} · {wf.description || 'No description'}</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                  wf.status === 'active' ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300' :
                  wf.status === 'paused' ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300' :
                  'bg-secondary text-secondary-foreground'
                }`}>{wf.status}</span>
                {wf.status === 'active' ? (
                  <button onClick={() => statusMutation.mutate({ id: wf.id, status: 'paused' })} className="p-1.5 hover:bg-accent rounded text-muted-foreground">
                    <Pause size={14} />
                  </button>
                ) : (
                  <button onClick={() => statusMutation.mutate({ id: wf.id, status: 'active' })} className="p-1.5 hover:bg-accent rounded text-muted-foreground">
                    <Play size={14} />
                  </button>
                )}
              </div>
            </div>
          ))}
          {workflows.length === 0 && (
            <div className="text-center py-16 text-muted-foreground">
              <Zap size={32} className="mx-auto mb-2 opacity-30" />
              <p className="text-sm">No workflows yet. Create your first automation.</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
