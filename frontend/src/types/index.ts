export interface Wreck {
  id: string
  name: string | null
  latitude: number
  longitude: number
  depth: number | null
  depth_precision: string | null
  ship_info: string | null
  object_condition: string | null
  sinking_circumstances: string | null
  object_length: number | null
  position_precision: number | null
  object_type: string | null
  inspire_id: string | null
  distance_nm?: number
  bearing?: number
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

export interface InspectorEvent {
  type: 'agent_call' | 'agent_result' | 'tool_call' | 'tool_result' | 'decision' | 'warning' | 'error' | 'thinking'
  agent: string | null
  title: string
  content: string
  metadata: Record<string, unknown> | null
  timestamp: string
}
