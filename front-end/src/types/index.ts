/**
 * TypeScript interfaces for RPGChat.AI
 * These match the Pydantic schemas from the backend
 */

// ============================================
// Character Types
// ============================================

export interface OfficialCharacter {
  id: string;
  name: string;
  avatar_url: string | null;
  description: string | null;
  tags: string[] | null;
  first_message: string | null;
}

export interface Character {
  id: number;
  name: string;
  avatar_url: string | null;
  description: string | null;
  first_message: string | null;
  personality_prompt: string | null;
  scenario_prompt: string | null;
  example_dialogues_prompt: string | null;
  system_prompt: string | null;
  tags: string[] | null;
  is_favorite: boolean;
  created_at: string;
}

export interface CharacterSummary {
  id: number;
  name: string;
  avatar_url: string | null;
  description: string | null;
  tags: string[] | null;
  is_favorite: boolean;
}

// ============================================
// Conversation Types
// ============================================

export interface Conversation {
  id: number;
  character_id: number | null;
  api_provider_id: number | null;
  title: string | null;
  similarity_threshold: number | null;
  top_k: number | null;
  created_at: string;
  updated_at: string;
  character_name: string | null;
  character_avatar: string | null;
}

export interface ConversationSummary {
  id: number;
  character_id: number | null;
  title: string | null;
  updated_at: string;
  character_name: string | null;
  character_avatar: string | null;
  last_message_preview: string | null;
}

export interface ConversationCreate {
  character_id: number;
  api_provider_id?: number | null;
  title?: string | null;
  similarity_threshold?: number;
  top_k?: number;
}

// ============================================
// Message Types
// ============================================

export type MessageRole = 'user' | 'assistant' | 'system';

export interface Message {
  id: number;
  conversation_id: number;
  role: MessageRole;
  content: string;
  created_at: string;
}

export interface ChatRequest {
  content: string;
  kb_ids?: number[] | null;
}

export interface ChatResponse {
  user_message: Message;
  assistant_message: Message;
  rag_snippets_used: number;
}

// ============================================
// API Provider Types
// ============================================

export type ProviderType = 'openai' | 'huggingface';

export interface APIProvider {
  id: number;
  name: string;
  provider_type: ProviderType;
  base_url: string;
  api_key_masked: string;
  chat_model_id: string;
  embedding_model_id: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface APIProviderCreate {
  name: string;
  provider_type?: ProviderType;
  base_url: string;
  api_key: string;
  chat_model_id: string;
  embedding_model_id?: string;
}

export interface APIProviderUpdate {
  name?: string;
  provider_type?: ProviderType;
  base_url?: string;
  api_key?: string;
  chat_model_id?: string;
  embedding_model_id?: string;
}

export interface APIProviderTestResult {
  success: boolean;
  message: string;
  latency_ms: number | null;
  model_response: string | null;
}

// ============================================
// Knowledge Base Types
// ============================================

export interface KnowledgeBase {
  id: number;
  name: string;
  description: string | null;
  created_at: string;
}

export interface KnowledgeBaseCreate {
  name: string;
  description?: string | null;
}

export interface KBDocument {
  id: number;
  kb_id: number;
  source_filename: string | null;
  chunk_index: number | null;
  chunk_text: string;
  has_embedding: boolean;
  created_at: string;
}

// ============================================
// Prompt Template Types
// ============================================

export interface PromptTemplate {
  key: string;
  title: string;
  description: string;
  default_prompt: string;
  custom_prompt: string | null;
}

export interface PromptTemplateUpdate {
  custom_prompt: string | null;
}

// ============================================
// Import Response Types
// ============================================

export interface ImportResponse {
  character_id: number;
  conversation_id: number;
  message: string;
}

