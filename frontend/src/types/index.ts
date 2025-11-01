// User and auth types
export interface User {
  id: number
  email: string
  name: string | null
  role: 'admin' | 'user'
  brand_id: number | null
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

// Brand types
export interface Brand {
  id: number
  name: string
  domain: string
  status: BrandStatus
  config: Record<string, any>
  created_at: string
  updated_at: string
}

export interface BrandCreate {
  name: string
  domain: string
  status?: BrandStatus
  config?: Record<string, any>
}

export interface BrandUpdate {
  name?: string
  domain?: string
  status?: BrandStatus
  config?: Record<string, any>
}

// Template types
export interface Template {
  id: number
  brand_id: number
  test_type: TestType
  template_code: string
  description?: string
  version: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface TemplateCreate {
  brand_id: number
  test_type: TestType
  template_code: string
  description?: string
  version?: string
  is_active?: boolean
}

export interface TemplateUpdate {
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

// Generated Code types
export interface GeneratedCode {
  id: number
  brand_id: number
  request_data?: Record<string, any>
  generated_code: string
  confidence_score?: number
  validation_status: ValidationStatus
  user_feedback?: string
  deployment_status: DeploymentStatus
  error_logs?: Record<string, any>
  created_at: string
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
