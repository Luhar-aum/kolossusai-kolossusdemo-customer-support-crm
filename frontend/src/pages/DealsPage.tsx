import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { dealsApi } from '@/lib/api'
import { useAuthStore } from '@/store/authStore'
import { formatCurrency } from '@/lib/utils'
import { Plus } from 'lucide-react'
import { useState } from 'react'
import { useForm } from 'react-hook-form'

const STAGES = ['new', 'contacted', 'qualified', 'demo_scheduled', 'proposal_sent', 'negotiation', 'won', 'lost']

const STAGE_COLORS: Record<string, string> = {
  new: 'border-blue-400 bg-blue-50 dark:bg-blue-950/30',
  contacted: 'border-yellow-400 bg-yellow-50 dark:bg-yellow-950/30',
  qualified: 'border-green-400 bg-green-50 dark:bg-green-950/30',
  demo_scheduled: 'border-purple-400 bg-purple-50 dark:bg-purple-950/30',
  proposal_sent: 'border-orange-400 bg-orange-50 dark:bg-orange-950/30',
  negotiation: 'border-pink-400 bg-pink-50 dark:bg-pink-950/30',
  won: 'border-emerald-400 bg-emerald-50 dark:bg-emerald-950/30',
  lost: 'border-red-400 bg-red-50 dark:bg-red-950/30',
}

type Deal = {
  id: string; name: string; value: number; currency: string; stage: string;
  company_id: string | null; probability: number | null;
}

export default function DealsPage() {
  const { currentOrg } = useAuthStore()
  const qc = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const { register, handleSubmit, reset } = useForm<{ name: string; value: string; stage: string; currency: string }>()

  const { data, isLoading } = useQuery({
    queryKey: ['deals', currentOrg?.id],
    queryFn: () => dealsApi.list(currentOrg!.id, { page_size: 100 }).then(r => r.data),
    enabled: !!currentOrg,
  })

  const createMutation = useMutation({
    mutationFn: (d: Record<string, unknown>) => dealsApi.create({ ...d, organization_id: currentOrg!.id }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['deals'] }); setShowForm(false); reset() },
  })

  const moveMutation = useMutation({
    mutationFn: ({ id, stage }: { id: string; stage: string }) => dealsApi.moveStage(id, stage),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['deals'] }),
  })

  const deals: Deal[] = data?.data || []
  const byStage = STAGES.reduce((acc, s) => {
    acc[s] = deals.filter(d => d.stage === s)
    return acc
  }, {} as Record<string, Deal[]>)

  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        <button
          onClick={() => setShowForm(!showForm)}
          className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-md text-sm font-medium hover:bg-primary/90"
        >
          <Plus size={14} /> New Deal
        </button>
      </div>

      {showForm && (
        <form
          onSubmit={handleSubmit(d => createMutation.mutate({ ...d, value: parseFloat(d.value) || 0 }))}
          className="bg-card border border-border rounded-xl p-4 flex gap-3 flex-wrap"
        >
          <input {...register('name')} placeholder="Deal name*" className="px-3 py-2 text-sm border border-input rounded-md bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring flex-1 min-w-32" />
          <input {...register('value')} type="number" placeholder="Value" className="px-3 py-2 text-sm border border-input rounded-md bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring w-32" />
          <select {...register('stage')} className="px-3 py-2 text-sm border border-input rounded-md bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-ring">
            {STAGES.map(s => <option key={s} value={s}>{s.replace('_', ' ')}</option>)}
          </select>
          <button type="submit" className="px-4 py-2 bg-primary text-primary-foreground rounded-md text-sm">Save</button>
          <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 border border-border rounded-md text-sm text-muted-foreground">Cancel</button>
        </form>
      )}

      {isLoading ? (
        <div className="text-muted-foreground animate-pulse">Loading pipeline…</div>
      ) : (
        <div className="overflow-x-auto pb-4">
          <div className="flex gap-3 min-w-max">
            {STAGES.map(stage => (
              <div key={stage} className="w-56 flex-shrink-0">
                <div className={`rounded-t-lg border-t-2 px-3 py-2 mb-2 ${STAGE_COLORS[stage]}`}>
                  <p className="text-xs font-semibold text-foreground capitalize">{stage.replace('_', ' ')}</p>
                  <p className="text-xs text-muted-foreground">
                    {byStage[stage].length} deals · {formatCurrency(byStage[stage].reduce((s, d) => s + (d.value || 0), 0))}
                  </p>
                </div>
                <div className="space-y-2">
                  {byStage[stage].map(deal => (
                    <div key={deal.id} className="bg-card border border-border rounded-lg p-3 cursor-pointer hover:shadow-sm transition-shadow">
                      <p className="text-sm font-medium text-foreground truncate">{deal.name}</p>
                      <p className="text-xs text-muted-foreground mt-1">{formatCurrency(deal.value || 0, deal.currency)}</p>
                      {deal.probability != null && (
                        <div className="mt-2">
                          <div className="w-full h-1 bg-secondary rounded-full">
                            <div className="h-full bg-primary rounded-full" style={{ width: `${deal.probability}%` }} />
                          </div>
                        </div>
                      )}
                      <select
                        value={deal.stage}
                        onChange={e => moveMutation.mutate({ id: deal.id, stage: e.target.value })}
                        className="mt-2 w-full text-xs border border-input rounded bg-background text-muted-foreground px-1 py-0.5"
                      >
                        {STAGES.map(s => <option key={s} value={s}>{s.replace('_', ' ')}</option>)}
                      </select>
                    </div>
                  ))}
                  {byStage[stage].length === 0 && (
                    <div className="text-xs text-muted-foreground text-center py-4 border-2 border-dashed border-border rounded-lg">
                      No deals
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
