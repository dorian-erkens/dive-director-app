import { useCallback, useEffect, useRef, useState } from 'react'
import { PanelLeftClose, PanelRightClose, PanelLeftOpen, PanelRightOpen } from 'lucide-react'
import WreckMap from './components/Map/WreckMap'
import ChatPanel from './components/Chat/ChatPanel'
import InspectorPanel from './components/Inspector/InspectorPanel'
import { useChat } from './hooks/useChat'
import { useWrecks } from './hooks/useWrecks'

export default function App() {
  const [chatOpen, setChatOpen] = useState(true)
  const [inspectorOpen, setInspectorOpen] = useState(true)

  const chat = useChat()
  const wreckState = useWrecks()

  // Debounced bounds change handler
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const handleBoundsChange = useCallback(
    (bounds: { minLat: number; maxLat: number; minLon: number; maxLon: number }) => {
      if (debounceRef.current) clearTimeout(debounceRef.current)
      debounceRef.current = setTimeout(() => {
        wreckState.fetchBbox(bounds.minLat, bounds.maxLat, bounds.minLon, bounds.maxLon)
      }, 600)
    },
    [wreckState.fetchBbox],
  )

  // Connect chat WebSocket on mount
  useEffect(() => {
    chat.connect()
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <div className="flex h-full w-full bg-slate-950">
      {/* Chat panel */}
      {chatOpen && (
        <div className="w-80 shrink-0 border-r border-slate-800">
          <ChatPanel
            messages={chat.messages}
            isStreaming={chat.isStreaming}
            connectionError={chat.connectionError}
            onSend={chat.sendMessage}
          />
        </div>
      )}

      {/* Center: Map + toggle buttons */}
      <div className="flex-1 relative">
        {/* Toggle buttons */}
        <div className="absolute top-3 left-3 z-[1000] flex gap-2">
          <button
            onClick={() => setChatOpen(!chatOpen)}
            className="p-2 rounded-lg bg-slate-900/90 border border-slate-700/50 text-slate-400 hover:text-white hover:border-slate-600 backdrop-blur transition-colors"
            title={chatOpen ? 'Masquer le chat' : 'Afficher le chat'}
          >
            {chatOpen ? <PanelLeftClose className="w-4 h-4" /> : <PanelLeftOpen className="w-4 h-4" />}
          </button>
        </div>

        <div className="absolute top-3 right-3 z-[1000] flex gap-2">
          <button
            onClick={() => setInspectorOpen(!inspectorOpen)}
            className="p-2 rounded-lg bg-slate-900/90 border border-slate-700/50 text-slate-400 hover:text-white hover:border-slate-600 backdrop-blur transition-colors"
            title={inspectorOpen ? "Masquer l'inspector" : "Afficher l'inspector"}
          >
            {inspectorOpen ? <PanelRightClose className="w-4 h-4" /> : <PanelRightOpen className="w-4 h-4" />}
          </button>
        </div>

        {/* Wreck counter */}
        <div className="absolute bottom-4 left-1/2 -translate-x-1/2 z-[1000]">
          <div className="px-3 py-1.5 rounded-full bg-slate-900/90 border border-slate-700/50 backdrop-blur text-xs text-slate-300 tabular-nums">
            {wreckState.loading ? (
              <span className="text-cyan-400 animate-pulse">Chargement...</span>
            ) : (
              <>
                <span className="text-cyan-400 font-semibold">{wreckState.wrecks.length}</span>
                {' '}epave{wreckState.wrecks.length !== 1 ? 's' : ''} affichee{wreckState.wrecks.length !== 1 ? 's' : ''}
              </>
            )}
          </div>
        </div>

        <WreckMap
          wrecks={wreckState.wrecks}
          selectedWreck={wreckState.selectedWreck}
          onSelectWreck={wreckState.setSelectedWreck}
          onBoundsChange={handleBoundsChange}
        />
      </div>

      {/* Inspector panel */}
      {inspectorOpen && (
        <div className="w-80 shrink-0 border-l border-slate-800">
          <InspectorPanel events={chat.inspectorEvents} />
        </div>
      )}
    </div>
  )
}
