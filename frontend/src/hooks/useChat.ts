import { useCallback, useRef, useState } from 'react'
import type { ChatMessage, InspectorEvent } from '../types'

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [isStreaming, setIsStreaming] = useState(false)
  const [conversationId, setConversationId] = useState<string | null>(null)
  const [inspectorEvents, setInspectorEvents] = useState<InspectorEvent[]>([])
  const wsRef = useRef<WebSocket | null>(null)
  const inspectorWsRef = useRef<WebSocket | null>(null)
  const streamBufferRef = useRef('')

  const connectInspector = useCallback((convId: string) => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const ws = new WebSocket(`${protocol}//${window.location.host}/ws/inspector/${convId}`)

    ws.onmessage = (event) => {
      const data: InspectorEvent = JSON.parse(event.data)
      setInspectorEvents((prev) => [...prev, data])
    }

    inspectorWsRef.current = ws
  }, [])

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const ws = new WebSocket(`${protocol}//${window.location.host}/ws/chat`)

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)

      switch (data.type) {
        case 'connected':
          setConversationId(data.conversation_id)
          connectInspector(data.conversation_id)
          break

        case 'stream_start':
          setIsStreaming(true)
          streamBufferRef.current = ''
          setMessages((prev) => [...prev, { role: 'assistant', content: '' }])
          break

        case 'stream_token':
          streamBufferRef.current += data.token
          setMessages((prev) => {
            const updated = [...prev]
            updated[updated.length - 1] = {
              role: 'assistant',
              content: streamBufferRef.current,
            }
            return updated
          })
          break

        case 'stream_end':
          setIsStreaming(false)
          break
      }
    }

    ws.onclose = () => {
      wsRef.current = null
    }

    wsRef.current = ws
  }, [connectInspector])

  const sendMessage = useCallback(
    (content: string) => {
      if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
        connect()
        // Retry after connection
        setTimeout(() => sendMessage(content), 500)
        return
      }

      setMessages((prev) => [...prev, { role: 'user', content }])
      wsRef.current.send(JSON.stringify({ message: content }))
    },
    [connect],
  )

  const clearInspector = useCallback(() => {
    setInspectorEvents([])
  }, [])

  return {
    messages,
    isStreaming,
    conversationId,
    inspectorEvents,
    connect,
    sendMessage,
    clearInspector,
  }
}
