import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { leadsApi } from '@/lib/api'
import { useAuthStore } from '@/store/authStore'
import { Plus, Search, Sparkles, Trash2 } from 'lucide-react'
import { useForm } from 'react-hook-form'

const STATUS_COLORS: Record<string, string> = {
  new: 'bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300',
  contacted: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/40 dark:text-yellow-300',
  qualified: 'bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300',
  unqualified: 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300',
  converted: 'bg-purple-100 text-purple-800 dark:bg-purple-900/40 dark:text-purple-300',
  lost: 'bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-300',
}

const CLASS_COLORS: Record<string, string> = {
  hot: 'bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300',
  warm: 'bg-orange-100 text-orange-700 dark:bg-orange-900/40 dark:text-orange-300',
  cold: 'bg-cyan-100 text-cyan-700 dark:bg-cyan-900/40 dark:text-cyan-300',
}

function Badge({ value, map }: { value: string; map: Record<string, string> }) {
  return (
    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${map[value] || 'bg-secondary text-secondary-foreground'}`}>
      {value}
    </span>
  )
}

export default function LeadsPage() {
  const { currentOrg } = useAuthStore()
  const qc = useQueryClient()
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState('')
  const [showForm, setShowForm] = useState(false)
  const { register, handleSubmit, reset } = useForm<{ name: string; email: string; company: string; phone: string; industry: string }>()

  const { data, isLoading } = useQuery({
    queryKey: ['leads', currentOrg?.id, search, status],
    queryFn: () => leadsApi.list(currentOrg!.id, { search, status, page_size: 50 }).then(r => r.data),
    enabled: !!currentOrg,
  })

  const createMutation = useMutation({
    mutationFn: (d: Record<string, unknown>) => leadsApi.create({ ...d, organization_id: currentOrg!.id }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['leads'] }); setShowForm(false); reset() },
  })

  const qualifyMutation = useMutation({
    mutationFn: (id: string) => leadsApi.qualify(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['leads'] }),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => leadsApi.delete(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['leads'] }),
  })

  const leads = data?.data || []

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex gap-2">
          <div className="relative">
            <Search className="absolute left-3 top-2.5 text-muted-foreground" size={14} />
            <input
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder="Search leads…"
              className="pl-8 pr-3 py-2 text-sm border border-input rounded-md bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring w-56"
            />
          </div>
          <select
            value={status}
            onChange={e => setStatus(e.target.value)}
            className="px-3 py-2 text-sm border border-input rounded-md bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
          >
            <option value="">All statuses</option>
            {['new', 'contacted', 'qualified', 'unqualified', 'converted', 'lost'].map(s => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-md text-sm font-medium hover:bg-primary/90 transition-colors"
        >
          <Plus size={14} /> Add Lead
        </button>
      </div>

      {showForm && (
        <form
          onSubmit={handleSubmit(d => createMutation.mutate(d as Record<string, unknown>))}
          className="bg-card border border-border rounded-xl p-4 grid grid-cols-2 md:grid-cols-5 gap-3"
        >
          {[
            { n: 'name', p: 'Name*' }, { n: 'email', p: 'Email' },
            { n: 'company', p: 'Company' }, { n: 'phone', p: 'Phone' },
            { n: 'industry', p: 'Industry' },
          ].map(({ n, p }) => (
            <input
              key={n}
              {...register(n as 'name')}
              placeholder={p}
              className="px-3 py-2 text-sm border border-input rounded-md bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            />
          ))}
          <div className="col-span-2 md:col-span-5 flex gap-2">
            <button type="submit" className="px-4 py-2 bg-primary text-primary-foreground rounded-md text-sm font-medium">Save</button>
            <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 border border-border rounded-md text-sm text-muted-foreground hover:bg-accent">Cancel</button>
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
                <th className="text-left px-4 py-3 font-medium">Name</th>
                <th className="text-left px-4 py-3 font-medium">Company</th>
                <th className="text-left px-4 py-3 font-medium">Status</th>
                <th className="text-left px-4 py-3 font-medium">Score</th>
                <th className="text-left px-4 py-3 font-medium">Class</th>
                <th className="text-left px-4 py-3 font-medium">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {leads.map((lead: Record<string, string | number>) => (
                <tr key={lead.id as string} className="hover:bg-accent/30 transition-colors">
                  <td className="px-4 py-3">
                    <div>
                      <p className="font-medium text-foreground">{lead.name as string}</p>
                      <p className="text-xs text-muted-foreground">{lead.email as string}</p>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-muted-foreground">{lead.company as string || '—'}</td>
                  <td className="px-4 py-3">
                    <Badge value={lead.status as string} map={STATUS_COLORS} />
                  </td>
                  <td className="px-4 py-3">
                    {lead.lead_score !== null && lead.lead_score !== undefined ? (
                      <div className="flex items-center gap-1">
                        <div className="w-16 h-1.5 bg-secondary rounded-full overflow-hidden">
                          <div
                            className="h-full bg-primary rounded-full"
                            style={{ width: `${lead.lead_score}%` }}
                          />
                        </div>
                        <span className="text-xs text-muted-foreground">{lead.lead_score}</span>
                      </div>
                    ) : '—'}
                  </td>
                  <td className="px-4 py-3">
                    {lead.classification ? (
                      <Badge value={lead.classification as string} map={CLASS_COLORS} />
                    ) : '—'}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex gap-1">
                      <button
                        onClick={() => qualifyMutation.mutate(lead.id as string)}
                        title="AI Qualify"
                        className="p-1.5 hover:bg-primary/10 rounded text-primary transition-colors"
                        disabled={qualifyMutation.isPending}
                      >
                        <Sparkles size={14} />
                      </button>
                      <button
                        onClick={() => { if (confirm('Delete this lead?')) deleteMutation.mutate(lead.id as string) }}
                        title="Delete"
                        className="p-1.5 hover:bg-destructive/10 rounded text-destructive transition-colors"
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
              {leads.length === 0 && (
                <tr>
                  <td colSpan={6} className="px-4 py-8 text-center text-muted-foreground">
                    No leads found. Add your first lead above.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
