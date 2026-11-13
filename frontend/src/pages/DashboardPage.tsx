import { useQuery } from '@tanstack/react-query'
import { analyticsApi } from '@/lib/api'
import { useAuthStore } from '@/store/authStore'
import { formatCurrency } from '@/lib/utils'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend
} from 'recharts'

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16']

function StatCard({ label, value, sub }: { label: string; value: string | number; sub?: string }) {
  return (
    <div className="bg-card border border-border rounded-xl p-5">
      <p className="text-sm text-muted-foreground">{label}</p>
      <p className="text-2xl font-bold text-foreground mt-1">{value}</p>
      {sub && <p className="text-xs text-muted-foreground mt-1">{sub}</p>}
    </div>
  )
}

export default function DashboardPage() {
  const { currentOrg } = useAuthStore()
  const { data, isLoading } = useQuery({
    queryKey: ['dashboard', currentOrg?.id],
    queryFn: () => analyticsApi.dashboard(currentOrg!.id).then((r) => r.data),
    enabled: !!currentOrg,
  })

  if (isLoading) return <div className="text-muted-foreground animate-pulse">Loading dashboard…</div>
  if (!data) return null

  return (
    <div className="space-y-6">
      {/* KPI row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard label="Total Leads" value={data.total_leads} />
        <StatCard label="Qualified Leads" value={data.qualified_leads} />
        <StatCard label="Conversion Rate" value={`${data.conversion_rate}%`} />
        <StatCard label="Pipeline Value" value={formatCurrency(data.pipeline_value)} />
        <StatCard label="Won Deals" value={data.won_deals} />
        <StatCard label="Lost Deals" value={data.lost_deals} />
        <StatCard label="Won Revenue" value={formatCurrency(data.won_revenue)} />
        <StatCard label="Overdue Tasks" value={data.overdue_tasks} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Pipeline by stage */}
        <div className="bg-card border border-border rounded-xl p-5">
          <h3 className="font-semibold text-foreground mb-4">Pipeline by Stage</h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={data.deals_by_stage}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
              <XAxis dataKey="stage" tick={{ fontSize: 11, fill: 'var(--muted-foreground)' }} />
              <YAxis tick={{ fontSize: 11, fill: 'var(--muted-foreground)' }} />
              <Tooltip
                contentStyle={{ background: 'hsl(var(--card))', border: '1px solid hsl(var(--border))', borderRadius: '8px' }}
                labelStyle={{ color: 'hsl(var(--foreground))' }}
              />
              <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Leads by status */}
        <div className="bg-card border border-border rounded-xl p-5">
          <h3 className="font-semibold text-foreground mb-4">Leads by Status</h3>
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie data={data.leads_by_status} dataKey="count" nameKey="status" cx="50%" cy="50%" outerRadius={80} label>
                {data.leads_by_status.map((_: unknown, i: number) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Legend />
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}
