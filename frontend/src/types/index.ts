// User and auth types
export type BrandRole = 'super_admin' | 'brand_admin' | 'brand_user'

export interface User {
  id: number
  email: string
  name: string | null
  role: 'admin' | 'user'
  brand_id: number | null
  brand_role: BrandRole
  brand_name?: string
}

export interface LoginResponse {
  token: string
  expires_at: string
  user: User
}

// Enums
export enum BrandStatus {
  ACTIVE = 'active',
  INACTIVE = 'inactive',
  ARCHIVED = 'archived',
}

export enum TestType {
  PDP = 'pdp',
  CART = 'cart',
  CHECKOUT = 'checkout',
  HOME = 'home',
  CATEGORY = 'category',
}

export enum PageType {
  PDP = 'pdp',
  CART = 'cart',
  CHECKOUT = 'checkout',
  HOME = 'home',
  CATEGORY = 'category',
  SEARCH = 'search',
}

export enum RuleType {
  FORBIDDEN_PATTERN = 'forbidden_pattern',
  REQUIRED_PATTERN = 'required_pattern',
  MAX_LENGTH = 'max_length',
  MIN_LENGTH = 'min_length',
}

export enum ValidationStatus {
  PENDING = 'pending',
  VALID = 'valid',
  INVALID = 'invalid',
  WARNING = 'warning',
}

export enum DeploymentStatus {
  PENDING = 'pending',
  DEPLOYED = 'deployed',
  FAILED = 'failed',
  ROLLED_BACK = 'rolled_back',
}

export enum SelectorStatus {
  ACTIVE = 'active',
  INACTIVE = 'inactive',
  DEPRECATED = 'deprecated',
}

export type CodeStatus = 'generated' | 'reviewed' | 'approved' | 'rejected' | 'deployed'

// Brand types
export interface Brand {
  id: number
  name: string
  domain: string
  status: BrandStatus
  code_template: Record<string, any>
  created_at: string
  updated_at: string
}

export interface BrandCreate {
  name: string
  domain: string
  status?: BrandStatus
  code_template?: Record<string, any>
}

export interface BrandUpdate {
  name?: string
  domain?: string
  status?: BrandStatus
  code_template?: Record<string, any>
}

// Brand Template types
export interface BrandTemplate {
  name: string
  description: string
  platform: string
}

// Page Type Knowledge types
export interface PageTypeKnowledge {
  id: number
  brand_id: number
  test_type: TestType
  template_code: string
  description?: string
  version: string
  is_active: boolean
  created_at: string
  updated_at: string
  brand_name?: string
}

export interface PageTypeKnowledgeCreate {
  brand_id: number
  test_type: TestType
  template_code: string
  description?: string
  version?: string
  is_active?: boolean
}

export interface PageTypeKnowledgeUpdate {
  brand_id?: number
  test_type?: TestType
  template_code?: string
  description?: string
  version?: string
  is_active?: boolean
}

// DOM Selector types
export interface DOMSelector {
  id: number
  brand_id: number
  page_type: PageType
  selector: string
  description?: string
  status: SelectorStatus
  created_at: string
  updated_at: string
  brand_name?: string
}

export interface DOMSelectorCreate {
  brand_id: number
  page_type: PageType
  selector: string
  description?: string
  status?: SelectorStatus
}

export interface DOMSelectorUpdate {
  brand_id?: number
  page_type?: PageType
  selector?: string
  description?: string
  status?: SelectorStatus
}

// Code Rule types
export interface CodeRule {
  id: number
  brand_id: number
  rule_type: RuleType
  rule_content: string
  priority: number
  created_at: string
  updated_at: string
  brand_name?: string
}

export interface CodeRuleCreate {
  brand_id: number
  rule_type: RuleType
  rule_content: string
  priority?: number
}

export interface CodeRuleUpdate {
  brand_id?: number
  rule_type?: RuleType
  rule_content?: string
  priority?: number
}

// Confidence Breakdown types
export interface ConfidenceBreakdown {
  overall_score: number
  template_score: number
  rule_score: number
  selector_score: number
  rule_violations: string[]
  invalid_selectors: string[]
  is_valid: boolean
  validation_status: 'passed' | 'failed' | 'warning'
  recommendation: 'safe_to_use' | 'review_carefully' | 'needs_fixes'
}

// Generated Code types
export interface GeneratedCode {
  id: number
  brand_id: number
  conversation_id?: string | null
  user_id?: number | null
  request_data?: Record<string, any>
  generated_code: string
  confidence_score?: number | null
  validation_status: ValidationStatus
  user_feedback?: string | null
  deployment_status: DeploymentStatus
  error_logs?: Record<string, any>
  status: CodeStatus
  reviewer_id?: number | null
  reviewed_at?: string | null
  reviewer_notes?: string | null
  approved_at?: string | null
  rejection_reason?: string | null
  created_at: string
  // Enhanced fields from API
  brand_name?: string
  user_email?: string
  conversation_preview?: string
  reviewer_email?: string
  confidence_breakdown?: ConfidenceBreakdown
  // Selector validation fields
  requires_review?: boolean
  selector_source?: 'database' | 'user_provided'
  selector_metadata?: {
    selector_used: string
    selector_source: string
    requires_review: boolean
    selector_validated: boolean
  }
}

export interface GeneratedCodeCreate {
  brand_id: number
  request_data?: Record<string, any>
  generated_code: string
  confidence_score?: number
  validation_status?: ValidationStatus
  user_feedback?: string
  deployment_status?: DeploymentStatus
  error_logs?: Record<string, any>
}

export interface GeneratedCodeUpdate {
  brand_id?: number
  request_data?: Record<string, any>
  generated_code?: string
  confidence_score?: number
  validation_status?: ValidationStatus
  user_feedback?: string
  deployment_status?: DeploymentStatus
  error_logs?: Record<string, any>
}

// Notification types
export interface Notification {
  id: number
  type: string
  title: string
  message: string
  read: boolean
  read_at: string | null
  created_at: string
  generated_code_id?: number | null
  user_id: number
}

export interface UnreadCount {
  count: number
}

// DOM Analysis types
export interface DomSelector {
  selector: string
  description: string
  stability_score: number
  element_type: string
  parent: string | null
  children: string[]
  siblings: string[]
}

export interface DomRelationships {
  containers: string[]
  interactive: string[]
  content: string[]
}

export interface DomAnalysisResult {
  selectors: DomSelector[]
  relationships: DomRelationships
  patterns: string[]
  recommendations: string[]
  warnings: string[]
}
