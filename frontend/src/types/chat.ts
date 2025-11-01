// Chat types
export enum ConversationStatus {
  ACTIVE = 'active',
  COMPLETED = 'completed',
  ABANDONED = 'abandoned',
}

export type MessageRole = 'user' | 'assistant'

export interface Message {
  id: number
  role: MessageRole
  content: string
  created_at: string
  generated_code_id?: number | null
}

export interface Conversation {
  id: string
  user_id: number
  brand_id: number | null
  status: ConversationStatus
  created_at: string
  updated_at: string
}

export interface ConversationPreview {
  id: string
  preview: string
  last_message: string | null
  created_at: string
  updated_at: string
  status: ConversationStatus
}

export interface ChatMessageRequest {
  message: string
  conversation_id?: string | null
}

export interface ChatMessageResponse {
  conversation_id: string
  message: string
  generated_code: GeneratedCode | null
  confidence_score: number | null
  status: 'gathering_info' | 'code_generated'
}

export interface ConversationHistoryResponse {
  conversation_id: string
  messages: Message[]
  generated_code: GeneratedCode | null
  status: ConversationStatus
  created_at: string
  updated_at: string
}

export interface ConversationForCodeResponse {
  conversation_id: string
  messages: Array<{
    role: MessageRole
    content: string
    created_at: string | null
  }>
  user: {
    id: number
    email: string
    name: string | null
  }
  brand: {
    id: number
    name: string
    domain: string
  } | null
}

// GeneratedCode type (duplicated to avoid circular dependency)
export interface GeneratedCode {
  id: number
  brand_id: number
  generated_code: string
  confidence_score?: number | null
  validation_status: string
  deployment_status: string
  created_at: string
  request_data?: Record<string, any> | null
  user_feedback?: string | null
  error_logs?: Record<string, any> | null
}

