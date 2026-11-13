import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { integrationsApi } from '@/lib/api'
import { useAuthStore } from '@/store/authStore'
import { Plug, CheckCircle, XCircle, TestTube } from 'lucide-react'

type Integration = { id: string; provider: string; name: string; status: string; is_active: boolean; last_sync_at: string | null }

const PROVIDERS = [
  { id: 'gmail', name: 'Gmail', icon: '✉️', desc: 'Connect your Gmail inbox' },
  { id: 'outlook', name: 'Microsoft Outlook', icon: '📧', desc: 'Sync Outlook emails' },
  { id: 'slack', name: 'Slack', icon: '💬', desc: 'Get notifications in Slack' },
  { id: 'hubspot', name: 'HubSpot', icon: '🔶', desc: 'Import contacts and deals' },
  { id: 'openai', name: 'OpenAI', icon: '🤖', desc: 'AI lead scoring & replies' },
  { id: 'anthropic', name: 'Anthropic Claude', icon: '⚡', desc: 'AI with Claude models' },
  { id: 'webhook', name: 'Generic Webhook', icon: '🔗', desc: 'Send events to any URL' },
]

export default function IntegrationsPage() {
  const { currentOrg } = useAuthStore()
  const qc = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['integrations', currentOrg?.id],
    queryFn: () => integrationsApi.list(currentOrg!.id).then(r => r.data),
    enabled: !!currentOrg,
  })

  const createMutation = useMutation({
    mutationFn: (provider: string) => integrationsApi.create({
      organization_id: currentOrg!.id,
      provider,
      name: PROVIDERS.find(p => p.id === provider)?.name || provider,
    }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['integrations'] }),
  })

  const testMutation = useMutation({
    mutationFn: (id: string) => integrationsApi.test(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['integrations'] }),
  })

  const integrations: Integration[] = data || []
  const connectedProviders = new Set(integrations.map(i => i.provider))

  return (
    <div className="space-y-6">
      <div className="bg-card border border-border rounded-xl p-5">
        <h3 className="font-semibold text-foreground mb-1">Connected Integrations</h3>
        <p className="text-sm text-muted-foreground mb-4">Manage your connected services and API keys.</p>
        {isLoading ? (
          <div className="text-muted-foreground animate-pulse text-sm">Loading…</div>
        ) : integrations.length === 0 ? (
          <p className="text-muted-foreground text-sm">No integrations connected yet.</p>
        ) : (
          <div className="space-y-2">
            {integrations.map(int => (
              <div key={int.id} className="flex items-center justify-between p-3 border border-border rounded-lg">
                <div className="flex items-center gap-3">
                  {int.is_active
                    ? <CheckCircle size={16} className="text-green-500" />
                    : <XCircle size={16} className="text-muted-foreground" />}
                  <div>
                    <p className="text-sm font-medium text-foreground">{int.name}</p>
                    <p className="text-xs text-muted-foreground capitalize">{int.provider} · {int.status}</p>
                  </div>
                </div>
                <button
                  onClick={() => testMutation.mutate(int.id)}
                  className="flex items-center gap-1 px-3 py-1.5 text-xs border border-border rounded-md hover:bg-accent text-muted-foreground transition-colors"
                >
                  <TestTube size={12} /> Test
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      <div>
        <h3 className="font-semibold text-foreground mb-3">Available Integrations</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {PROVIDERS.map(provider => (
            <div key={provider.id} className="bg-card border border-border rounded-xl p-4 flex items-start gap-3">
              <span className="text-2xl">{provider.icon}</span>
              <div className="flex-1 min-w-0">
                <p className="font-medium text-foreground text-sm">{provider.name}</p>
                <p className="text-xs text-muted-foreground mt-0.5">{provider.desc}</p>
              </div>
              {connectedProviders.has(provider.id) ? (
                <span className="text-xs px-2 py-1 bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300 rounded-full font-medium flex-shrink-0">Connected</span>
              ) : (
                <button
                  onClick={() => createMutation.mutate(provider.id)}
                  className="text-xs px-2 py-1 bg-primary text-primary-foreground rounded-full font-medium flex-shrink-0 hover:bg-primary/90"
                >
                  Connect
                </button>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
