import axios from 'axios'
import type {
  ChatMessageResponse,
  ConversationPreview,
  ConversationHistoryResponse,
  ConversationForCodeResponse,
} from '../types/chat'
import type { GeneratedCode, CodeStatus, Notification, UnreadCount, User } from '../types'

const API_BASE_URL = (import.meta.env.VITE_API_URL as string) || 'http://localhost:8000';

export const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
})

const TOKEN_KEY = 'auth_token'

// Request interceptor - add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem(TOKEN_KEY)
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    if (error.response) {
      // Handle 401 Unauthorized - clear token and redirect to login
      if (error.response.status === 401) {
        localStorage.removeItem(TOKEN_KEY)
        // Only redirect if we're not already on the login page
        if (window.location.pathname !== '/login') {
          window.location.href = '/login'
        }
      }
      
      // Server responded with error status
      const message = error.response.data?.detail || error.message || 'An error occurred'
      return Promise.reject(new Error(message))
    } else if (error.request) {
      // Request made but no response received
      return Promise.reject(new Error('Network error: Please check your connection'))
    } else {
      // Something else happened
      return Promise.reject(error)
    }
  }
)

export default api

// Chat API functions
export async function sendChatMessage(
  message: string,
  conversationId?: string | null
): Promise<ChatMessageResponse> {
  const response = await api.post<ChatMessageResponse>('/chat/message', {
    message,
    conversation_id: conversationId || null,
  })
  return response.data
}

export async function getConversations(): Promise<ConversationPreview[]> {
  const response = await api.get<ConversationPreview[]>('/chat/conversations')
  return response.data
}

export async function getConversation(
  conversationId: string
): Promise<ConversationHistoryResponse> {
  const response = await api.get<ConversationHistoryResponse>(
    `/chat/conversations/${conversationId}`
  )
  return response.data
}

// Generated Code API functions
export async function getGeneratedCodes(params?: {
  status?: CodeStatus
  brand_id?: number
  limit?: number
  offset?: number
}): Promise<GeneratedCode[]> {
  const response = await api.get<GeneratedCode[]>('/generated-code/', { params })
  return response.data
}

export async function reviewGeneratedCode(
  id: number,
  status: 'approved' | 'rejected',
  notes?: string
): Promise<GeneratedCode> {
  const response = await api.post<GeneratedCode>(`/generated-code/${id}/review`, {
    status,
    reviewer_notes: notes,
  })
  return response.data
}

export async function getCodeConversation(
  id: number
): Promise<ConversationForCodeResponse> {
  const response = await api.get<ConversationForCodeResponse>(
    `/generated-code/${id}/conversation`
  )
  return response.data
}

export async function deleteGeneratedCode(id: number): Promise<void> {
  await api.delete(`/generated-code/${id}`)
}

// Notification API functions
export async function getNotifications(
  unreadOnly?: boolean,
  limit?: number
): Promise<Notification[]> {
  const response = await api.get<Notification[]>('/notifications/', {
    params: { unread_only: unreadOnly, limit },
  })
  return response.data
}

export async function markNotificationAsRead(id: number): Promise<void> {
  await api.post(`/notifications/${id}/read`)
}

export async function getUnreadCount(): Promise<UnreadCount> {
  const response = await api.get<UnreadCount>('/notifications/unread-count')
  return response.data
}

// My Requests API functions
export async function getMyRequests(params?: {
  status?: string
  limit?: number
  offset?: number
}): Promise<GeneratedCode[]> {
  const response = await api.get<GeneratedCode[]>('/my-requests/', { params })
  return response.data
}

// User API functions
export async function createUser(userData: {
  email: string
  password: string
  name: string
  brand_id?: number
  brand_role: string
  role?: string
}): Promise<User> {
  const response = await api.post<User>('/users', userData)
  return response.data
}

