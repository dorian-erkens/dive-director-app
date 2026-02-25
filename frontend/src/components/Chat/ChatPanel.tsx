import { useEffect, useRef, useState } from 'react'
import { Send, Anchor, AlertCircle } from 'lucide-react'
import type { ChatMessage } from '../../types'

interface Props {
  messages: ChatMessage[]
  isStreaming: boolean
  connectionError: string | null
  onSend: (message: string) => void
}

export default function ChatPanel({ messages, isStreaming, connectionError, onSend }: Props) {
  const [input, setInput] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSubmit = () => {
    const trimmed = input.trim()
    if (!trimmed || isStreaming) return
    onSend(trimmed)
    setInput('')
    inputRef.current?.focus()
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  return (
    <div className="flex flex-col h-full bg-slate-900 text-white">
      {/* Header */}
      <div className="flex items-center gap-2 px-4 py-3 border-b border-slate-700/50 bg-slate-900/80 backdrop-blur">
        <Anchor className="w-5 h-5 text-cyan-400" />
        <h2 className="font-semibold text-sm tracking-wide">Dive Director</h2>
      </div>

      {/* Connection error */}
      {connectionError && (
        <div className="mx-3 mt-2 flex items-center gap-2 px-3 py-2 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-xs">
          <AlertCircle className="w-3.5 h-3.5 shrink-0" />
          {connectionError}
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
        {messages.length === 0 && !connectionError && (
          <div className="flex flex-col items-center justify-center h-full text-slate-500 text-sm text-center px-4 gap-3">
            <Anchor className="w-10 h-10 text-slate-600" />
            <p>Assistant Directeur de Plongee</p>
            <p className="text-xs text-slate-600">
              Posez une question sur les epaves, marees, meteo, reglementation...
            </p>
          </div>
        )}

        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[85%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed whitespace-pre-wrap ${
                msg.role === 'user'
                  ? 'bg-cyan-600 text-white rounded-br-md'
                  : 'bg-slate-800 text-slate-100 rounded-bl-md border border-slate-700/50'
              }`}
            >
              {msg.content}
              {msg.role === 'assistant' && isStreaming && i === messages.length - 1 && (
                <span className="inline-block w-2 h-4 bg-cyan-400 ml-1 animate-pulse rounded-sm" />
              )}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-3 border-t border-slate-700/50">
        <div className="flex items-end gap-2 bg-slate-800 rounded-xl border border-slate-700/50 px-3 py-2 focus-within:border-cyan-500/50 transition-colors">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ex: Epaves a moins de 5 NM de Ouistreham..."
            rows={1}
            className="flex-1 bg-transparent text-sm text-white placeholder-slate-500 resize-none outline-none max-h-32"
            style={{ minHeight: '24px' }}
          />
          <button
            onClick={handleSubmit}
            disabled={!input.trim() || isStreaming}
            className="p-1.5 rounded-lg text-cyan-400 hover:bg-cyan-400/10 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  )
}
