import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { conversationsApi } from '@/lib/api'
import { useAuthStore } from '@/store/authStore'
import { MessageSquare, Sparkles, CheckCircle, Plus } from 'lucide-react'

type Conversation = { id: string; subject: string; channel: string; status: string; sentiment: string | null; ai_summary: string | null; created_at: string }
type Message = { id: string; body: string; sender_type: string; sender_name: string | null; is_ai_generated: boolean; is_approved: boolean; is_sent: boolean; created_at: string }

export default function ConversationsPage() {
  const { currentOrg } = useAuthStore()
  const qc = useQueryClient()
  const [selected, setSelected] = useState<string | null>(null)
  const [newMsg, setNewMsg] = useState('')

  const { data: convsData } = useQuery({
    queryKey: ['conversations', currentOrg?.id],
    queryFn: () => conversationsApi.list(currentOrg!.id).then(r => r.data),
    enabled: !!currentOrg,
  })

  const { data: msgs } = useQuery({
    queryKey: ['messages', selected],
    queryFn: () => conversationsApi.messages(selected!).then(r => r.data),
    enabled: !!selected,
  })

  const sendMutation = useMutation({
    mutationFn: (body: string) => conversationsApi.addMessage(selected!, { body, sender_type: 'agent' }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['messages', selected] }); setNewMsg('') },
  })

  const suggestMutation = useMutation({
    mutationFn: () => conversationsApi.suggestReply(selected!),
    onSuccess: (res) => setNewMsg(res.data.suggested_reply),
  })

  const approveMutation = useMutation({
    mutationFn: (msgId: string) => conversationsApi.approveMessage(selected!, msgId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['messages', selected] }),
  })

  const createMutation = useMutation({
    mutationFn: () => conversationsApi.create({ organization_id: currentOrg!.id, channel: 'email', subject: 'New conversation' }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['conversations'] }),
  })

  const convs: Conversation[] = convsData?.data || []
  const messages: Message[] = msgs || []
  const selectedConv = convs.find(c => c.id === selected)

  return (
    <div className="flex gap-4 h-[calc(100vh-120px)]">
      {/* Conversation list */}
      <div className="w-72 flex-shrink-0 bg-card border border-border rounded-xl overflow-hidden flex flex-col">
        <div className="p-3 border-b border-border flex items-center justify-between">
          <h3 className="font-semibold text-foreground text-sm">Conversations</h3>
          <button onClick={() => createMutation.mutate()} className="p-1 hover:bg-accent rounded text-muted-foreground">
            <Plus size={14} />
          </button>
        </div>
        <div className="overflow-y-auto flex-1">
          {convs.map(conv => (
            <button
              key={conv.id}
              onClick={() => setSelected(conv.id)}
              className={`w-full text-left p-3 border-b border-border hover:bg-accent/50 transition-colors ${selected === conv.id ? 'bg-accent' : ''}`}
            >
              <div className="flex items-center gap-2">
                <MessageSquare size={12} className="text-muted-foreground flex-shrink-0" />
                <p className="text-xs font-medium text-foreground truncate">{conv.subject || 'Untitled'}</p>
              </div>
              <p className="text-xs text-muted-foreground mt-1 capitalize">{conv.channel} · {conv.status}</p>
              {conv.sentiment && (
                <span className={`text-xs px-1.5 py-0.5 rounded mt-1 inline-block ${
                  conv.sentiment === 'positive' ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300' :
                  conv.sentiment === 'negative' ? 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300' :
                  'bg-secondary text-secondary-foreground'
                }`}>{conv.sentiment}</span>
              )}
            </button>
          ))}
          {convs.length === 0 && (
            <div className="p-6 text-center text-xs text-muted-foreground">No conversations yet</div>
          )}
        </div>
      </div>

      {/* Message view */}
      <div className="flex-1 bg-card border border-border rounded-xl flex flex-col overflow-hidden">
        {selected ? (
          <>
            <div className="p-4 border-b border-border flex items-center justify-between">
              <div>
                <h3 className="font-semibold text-foreground text-sm">{selectedConv?.subject || 'Conversation'}</h3>
                <p className="text-xs text-muted-foreground capitalize">{selectedConv?.channel}</p>
              </div>
              {selectedConv?.ai_summary && (
                <div className="max-w-xs text-xs text-muted-foreground bg-secondary/50 rounded-lg px-3 py-1.5 border border-border">
                  <span className="text-primary font-medium">AI Summary:</span> {selectedConv.ai_summary}
                </div>
              )}
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-3">
              {messages.map(msg => (
                <div key={msg.id} className={`flex ${msg.sender_type === 'agent' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-xs lg:max-w-sm rounded-xl px-4 py-2.5 ${
                    msg.sender_type === 'agent'
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-secondary text-secondary-foreground'
                  }`}>
                    {msg.sender_name && <p className="text-xs opacity-70 mb-1">{msg.sender_name}</p>}
                    <p className="text-sm">{msg.body}</p>
                    {msg.is_ai_generated && (
                      <div className="flex items-center gap-1 mt-1">
                        <Sparkles size={10} className="opacity-70" />
                        <span className="text-xs opacity-70">AI-generated</span>
                        {!msg.is_approved && (
                          <button onClick={() => approveMutation.mutate(msg.id)} className="ml-2 text-xs underline opacity-80 hover:opacity-100">
                            Approve & Send
                          </button>
                        )}
                        {msg.is_approved && <CheckCircle size={10} className="opacity-70 ml-1" />}
                      </div>
                    )}
                  </div>
                </div>
              ))}
              {messages.length === 0 && (
                <div className="text-center text-muted-foreground text-sm py-12">No messages yet</div>
              )}
            </div>

            <div className="p-4 border-t border-border">
              <div className="flex gap-2">
                <textarea
                  value={newMsg}
                  onChange={e => setNewMsg(e.target.value)}
                  placeholder="Type a message…"
                  rows={2}
                  className="flex-1 px-3 py-2 text-sm border border-input rounded-lg bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring resize-none"
                />
                <div className="flex flex-col gap-2">
                  <button
                    onClick={() => newMsg && sendMutation.mutate(newMsg)}
                    disabled={!newMsg || sendMutation.isPending}
                    className="px-4 py-2 bg-primary text-primary-foreground rounded-lg text-sm font-medium hover:bg-primary/90 disabled:opacity-50"
                  >
                    Send
                  </button>
                  <button
                    onClick={() => suggestMutation.mutate()}
                    disabled={suggestMutation.isPending}
                    className="px-4 py-2 border border-border rounded-lg text-sm text-muted-foreground hover:bg-accent flex items-center gap-1"
                  >
                    <Sparkles size={12} /> AI
                  </button>
                </div>
              </div>
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center text-muted-foreground">
            <div className="text-center">
              <MessageSquare size={32} className="mx-auto mb-2 opacity-30" />
              <p className="text-sm">Select a conversation</p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
