import { useEffect, useRef } from 'react'
import { Activity, Bot, Wrench, AlertTriangle, Brain, CheckCircle, XCircle } from 'lucide-react'
import type { InspectorEvent } from '../../types'

interface Props {
  events: InspectorEvent[]
}

const EVENT_CONFIG: Record<
  string,
  { icon: typeof Activity; color: string; bg: string }
> = {
  agent_call: { icon: Bot, color: 'text-violet-400', bg: 'bg-violet-500/10' },
  agent_result: { icon: CheckCircle, color: 'text-green-400', bg: 'bg-green-500/10' },
  tool_call: { icon: Wrench, color: 'text-cyan-400', bg: 'bg-cyan-500/10' },
  tool_result: { icon: CheckCircle, color: 'text-emerald-400', bg: 'bg-emerald-500/10' },
  decision: { icon: Brain, color: 'text-amber-400', bg: 'bg-amber-500/10' },
  warning: { icon: AlertTriangle, color: 'text-orange-400', bg: 'bg-orange-500/10' },
  error: { icon: XCircle, color: 'text-red-400', bg: 'bg-red-500/10' },
  thinking: { icon: Brain, color: 'text-slate-400', bg: 'bg-slate-500/10' },
}

function EventCard({ event }: { event: InspectorEvent }) {
  const config = EVENT_CONFIG[event.type] || EVENT_CONFIG.thinking
  const Icon = config.icon
  const time = new Date(event.timestamp).toLocaleTimeString('fr-FR', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })

  return (
    <div className={`rounded-lg border border-slate-700/50 ${config.bg} p-3`}>
      <div className="flex items-start gap-2">
        <Icon className={`w-4 h-4 mt-0.5 shrink-0 ${config.color}`} />
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between gap-2">
            <span className={`text-xs font-semibold ${config.color}`}>
              {event.title}
            </span>
            <span className="text-[10px] text-slate-600 tabular-nums shrink-0">
              {time}
            </span>
          </div>
          {event.agent && (
            <span className="inline-block mt-1 px-1.5 py-0.5 text-[10px] font-mono rounded bg-slate-800 text-slate-400 border border-slate-700/50">
              {event.agent}
            </span>
          )}
          <p className="mt-1 text-xs text-slate-300 leading-relaxed break-words whitespace-pre-wrap">
            {event.content}
          </p>
        </div>
      </div>
    </div>
  )
}

export default function InspectorPanel({ events }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [events])

  return (
    <div className="flex flex-col h-full bg-slate-950 text-white">
      {/* Header */}
      <div className="flex items-center gap-2 px-4 py-3 border-b border-slate-700/50 bg-slate-950/80 backdrop-blur">
        <Activity className="w-4 h-4 text-violet-400" />
        <h2 className="font-semibold text-sm tracking-wide">Inspector</h2>
        <span className="ml-auto text-[10px] text-slate-600 tabular-nums">
          {events.length} event{events.length !== 1 ? 's' : ''}
        </span>
      </div>

      {/* Events */}
      <div className="flex-1 overflow-y-auto px-3 py-3 space-y-2">
        {events.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-slate-600 text-xs text-center px-4 gap-2">
            <Activity className="w-8 h-8 text-slate-700" />
            <p>Les evenements IA apparaitront ici en temps reel</p>
            <p className="text-slate-700">
              Appels d'agents, requetes SHOM, decisions...
            </p>
          </div>
        )}

        {events.map((event, i) => (
          <EventCard key={i} event={event} />
        ))}
        <div ref={bottomRef} />
      </div>

      {/* Footer legend */}
      <div className="px-3 py-2 border-t border-slate-800 flex flex-wrap gap-x-3 gap-y-1">
        {[
          { label: 'Agent', color: 'bg-violet-400' },
          { label: 'Outil', color: 'bg-cyan-400' },
          { label: 'Resultat', color: 'bg-emerald-400' },
          { label: 'Erreur', color: 'bg-red-400' },
        ].map(({ label, color }) => (
          <span key={label} className="flex items-center gap-1 text-[10px] text-slate-500">
            <span className={`w-1.5 h-1.5 rounded-full ${color}`} />
            {label}
          </span>
        ))}
      </div>
    </div>
  )
}
