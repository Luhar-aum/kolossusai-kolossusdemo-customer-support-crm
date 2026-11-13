import { useQuery } from '@tanstack/react-query'
import { analyticsApi } from '@/lib/api'
import { useAuthStore } from '@/store/authStore'
import { formatCurrency } from '@/lib/utils'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts'

export default function AnalyticsPage() {
  const { currentOrg } = useAuthStore()
  const { data, isLoading } = useQuery({
    queryKey: ['analytics', currentOrg?.id],
    queryFn: () => analyticsApi.dashboard(currentOrg!.id).then(r => r.data),
    enabled: !!currentOrg,
  })

  if (isLoading) return <div className="text-muted-foreground animate-pulse">Loading analytics…</div>
  if (!data) return null

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Total Leads', value: data.total_leads },
          { label: 'Qualified', value: data.qualified_leads },
          { label: 'Conversion Rate', value: `${data.conversion_rate}%` },
          { label: 'Pipeline Value', value: formatCurrency(data.pipeline_value) },
          { label: 'Won Revenue', value: formatCurrency(data.won_revenue) },
          { label: 'Won Deals', value: data.won_deals },
          { label: 'Lost Deals', value: data.lost_deals },
          { label: 'Overdue Tasks', value: data.overdue_tasks },
        ].map(({ label, value }) => (
          <div key={label} className="bg-card border border-border rounded-xl p-5">
            <p className="text-xs text-muted-foreground">{label}</p>
            <p className="text-2xl font-bold text-foreground mt-1">{value}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-card border border-border rounded-xl p-5">
          <h3 className="font-semibold text-foreground mb-4">Deals by Stage</h3>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={data.deals_by_stage}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis dataKey="stage" tick={{ fontSize: 11, fill: 'hsl(var(--muted-foreground))' }} />
              <YAxis tick={{ fontSize: 11, fill: 'hsl(var(--muted-foreground))' }} />
              <Tooltip contentStyle={{ background: 'hsl(var(--card))', border: '1px solid hsl(var(--border))', borderRadius: '8px' }} />
              <Bar dataKey="value" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} name="Value ($)" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-card border border-border rounded-xl p-5">
          <h3 className="font-semibold text-foreground mb-4">Lead Pipeline Funnel</h3>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={data.leads_by_status} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis type="number" tick={{ fontSize: 11, fill: 'hsl(var(--muted-foreground))' }} />
              <YAxis dataKey="status" type="category" tick={{ fontSize: 11, fill: 'hsl(var(--muted-foreground))' }} width={80} />
              <Tooltip contentStyle={{ background: 'hsl(var(--card))', border: '1px solid hsl(var(--border))', borderRadius: '8px' }} />
              <Bar dataKey="count" fill="#10b981" radius={[0, 4, 4, 0]} name="Count" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}
