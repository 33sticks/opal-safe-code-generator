import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api, {
  getGeneratedCodes,
  reviewGeneratedCode,
  getCodeConversation,
  deleteGeneratedCode,
} from '@/lib/api'
import type {
  Brand,
  BrandCreate,
  BrandUpdate,
  Template,
  TemplateCreate,
  TemplateUpdate,
  DOMSelector,
  DOMSelectorCreate,
  DOMSelectorUpdate,
  CodeRule,
  CodeRuleCreate,
  CodeRuleUpdate,
  GeneratedCode,
  CodeStatus,
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

// Templates
export function useTemplates() {
  return useQuery<Template[]>({
    queryKey: ['templates'],
    queryFn: async () => {
      const { data } = await api.get<Template[]>('/templates/')
      return data
    },
  })
}

export function useTemplate(id: number) {
  return useQuery<Template>({
    queryKey: ['templates', id],
    queryFn: async () => {
      const { data } = await api.get<Template>(`/templates/${id}`)
      return data
    },
    enabled: !!id,
  })
}

export function useCreateTemplate() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (template: TemplateCreate) => api.post<Template>('/templates/', template).then(res => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['templates'] })
    },
  })
}

export function useUpdateTemplate() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, ...update }: { id: number } & TemplateUpdate) => 
      api.put<Template>(`/templates/${id}`, update).then(res => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['templates'] })
    },
  })
}

export function useDeleteTemplate() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => api.delete(`/templates/${id}`).then(() => undefined),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['templates'] })
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

