import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api, {
  getGeneratedCodes,
  reviewGeneratedCode,
  getCodeConversation,
  deleteGeneratedCode,
  getNotifications,
  markNotificationAsRead,
  getUnreadCount,
  getMyRequests,
  createUser,
} from '@/lib/api'
import { useToast } from '@/hooks/use-toast'
import type {
  Brand,
  BrandCreate,
  BrandUpdate,
  BrandTemplate,
  PageTypeKnowledge,
  PageTypeKnowledgeCreate,
  PageTypeKnowledgeUpdate,
  DOMSelector,
  DOMSelectorCreate,
  DOMSelectorUpdate,
  CodeRule,
  CodeRuleCreate,
  CodeRuleUpdate,
  GeneratedCode,
  CodeStatus,
  Notification,
  UnreadCount,
} from '@/types'

// Brands
export function useBrands() {
  return useQuery<Brand[]>({
    queryKey: ['brands'],
    queryFn: async () => {
      const { data } = await api.get<Brand[]>('/brands/')
      return data
    },
  })
}

export function useBrand(id: number) {
  return useQuery<Brand>({
    queryKey: ['brands', id],
    queryFn: async () => {
      const { data } = await api.get<Brand>(`/brands/${id}`)
      return data
    },
    enabled: !!id,
  })
}

export function useCreateBrand() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (brand: BrandCreate) => api.post<Brand>('/brands/', brand).then(res => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['brands'] })
    },
  })
}

export function useUpdateBrand() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, ...update }: { id: number } & BrandUpdate) => 
      api.put<Brand>(`/brands/${id}`, update).then(res => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['brands'] })
    },
  })
}

export function useDeleteBrand() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => api.delete(`/brands/${id}`).then(() => undefined),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['brands'] })
    },
  })
}

// Brand Templates
export function useBrandTemplates() {
  return useQuery<BrandTemplate[]>({
    queryKey: ['brand-templates'],
    queryFn: async () => {
      const { data } = await api.get<BrandTemplate[]>('/brand-templates/')
      return data
    },
  })
}

export function useBrandTemplate(name: string) {
  return useQuery<Record<string, any>>({
    queryKey: ['brand-templates', name],
    queryFn: async () => {
      const { data } = await api.get<Record<string, any>>(`/brand-templates/${name}`)
      return data
    },
    enabled: !!name && name !== 'custom',
  })
}

// Page Type Knowledge
export function usePageTypeKnowledge() {
  return useQuery<PageTypeKnowledge[]>({
    queryKey: ['page-type-knowledge'],
    queryFn: async () => {
      const { data } = await api.get<PageTypeKnowledge[]>('/page-type-knowledge/')
      return data
    },
  })
}

export function usePageTypeKnowledgeItem(id: number) {
  return useQuery<PageTypeKnowledge>({
    queryKey: ['page-type-knowledge', id],
    queryFn: async () => {
      const { data } = await api.get<PageTypeKnowledge>(`/page-type-knowledge/${id}`)
      return data
    },
    enabled: !!id,
  })
}

export function useCreatePageTypeKnowledge() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (knowledge: PageTypeKnowledgeCreate) => api.post<PageTypeKnowledge>('/page-type-knowledge/', knowledge).then(res => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['page-type-knowledge'] })
    },
  })
}

export function useUpdatePageTypeKnowledge() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, ...update }: { id: number } & PageTypeKnowledgeUpdate) => 
      api.put<PageTypeKnowledge>(`/page-type-knowledge/${id}`, update).then(res => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['page-type-knowledge'] })
    },
  })
}

export function useDeletePageTypeKnowledge() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => api.delete(`/page-type-knowledge/${id}`).then(() => undefined),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['page-type-knowledge'] })
    },
  })
}

// Selectors
export function useSelectors() {
  return useQuery<DOMSelector[]>({
    queryKey: ['selectors'],
    queryFn: async () => {
      const { data } = await api.get<DOMSelector[]>('/selectors/')
      return data
    },
  })
}

export function useSelector(id: number) {
  return useQuery<DOMSelector>({
    queryKey: ['selectors', id],
    queryFn: async () => {
      const { data } = await api.get<DOMSelector>(`/selectors/${id}`)
      return data
    },
    enabled: !!id,
  })
}

export function useCreateSelector() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (selector: DOMSelectorCreate) => api.post<DOMSelector>('/selectors/', selector).then(res => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['selectors'] })
    },
  })
}

export function useUpdateSelector() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, ...update }: { id: number } & DOMSelectorUpdate) => 
      api.put<DOMSelector>(`/selectors/${id}`, update).then(res => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['selectors'] })
    },
  })
}

export function useDeleteSelector() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => api.delete(`/selectors/${id}`).then(() => undefined),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['selectors'] })
    },
  })
}

// Rules
export function useRules() {
  return useQuery<CodeRule[]>({
    queryKey: ['rules'],
    queryFn: async () => {
      const { data } = await api.get<CodeRule[]>('/rules/')
      return data
    },
  })
}

export function useRule(id: number) {
  return useQuery<CodeRule>({
    queryKey: ['rules', id],
    queryFn: async () => {
      const { data } = await api.get<CodeRule>(`/rules/${id}`)
      return data
    },
    enabled: !!id,
  })
}

export function useCreateRule() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (rule: CodeRuleCreate) => api.post<CodeRule>('/rules/', rule).then(res => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['rules'] })
    },
  })
}

export function useUpdateRule() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, ...update }: { id: number } & CodeRuleUpdate) => 
      api.put<CodeRule>(`/rules/${id}`, update).then(res => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['rules'] })
    },
  })
}

export function useDeleteRule() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => api.delete(`/rules/${id}`).then(() => undefined),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['rules'] })
    },
  })
}

// Generated Code (read-only)
export function useGeneratedCodes(params?: {
  status?: CodeStatus
  brand_id?: number
  limit?: number
  offset?: number
}) {
  return useQuery<GeneratedCode[]>({
    queryKey: ['generated-code', params],
    queryFn: () => getGeneratedCodes(params),
  })
}

export function useGeneratedCode(id: number) {
  return useQuery<GeneratedCode>({
    queryKey: ['generated-code', id],
    queryFn: async () => {
      const { data } = await api.get<GeneratedCode>(`/generated-code/${id}`)
      return data
    },
    enabled: !!id,
  })
}

export function useReviewGeneratedCode() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({
      id,
      status,
      notes,
    }: {
      id: number
      status: 'approved' | 'rejected'
      notes?: string
    }) => reviewGeneratedCode(id, status, notes),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['generated-code'] })
    },
  })
}

export function useCodeConversation(codeId: number | null) {
  return useQuery({
    queryKey: ['code-conversation', codeId],
    queryFn: () => getCodeConversation(codeId!),
    enabled: !!codeId,
  })
}

export function useDeleteGeneratedCode() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => deleteGeneratedCode(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['generated-code'] })
    },
  })
}

// Notifications
export function useNotifications(unreadOnly?: boolean) {
  return useQuery<Notification[]>({
    queryKey: ['notifications', { unreadOnly }],
    queryFn: () => getNotifications(unreadOnly, 20),
  })
}

export function useUnreadCount() {
  return useQuery<UnreadCount>({
    queryKey: ['notifications', 'unread-count'],
    queryFn: () => getUnreadCount(),
    refetchInterval: 30000, // Poll every 30 seconds
  })
}

export function useMarkAsRead() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => markNotificationAsRead(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] })
    },
  })
}

// My Requests
export function useMyRequests(status?: string) {
  return useQuery<GeneratedCode[]>({
    queryKey: ['my-requests', { status }],
    queryFn: () => getMyRequests({ status, limit: 50, offset: 0 }),
  })
}

// Users
export function useCreateUser() {
  const queryClient = useQueryClient()
  const { toast } = useToast()

  return useMutation({
    mutationFn: createUser,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] })
      toast({
        title: 'Success',
        description: 'User created successfully',
      })
    },
    onError: (error: any) => {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to create user',
        variant: 'destructive',
      })
    },
  })
}

