/**
 * Conversations API - Chat sessions and messages
 */

import apiClient from './client';
import type {
  Conversation,
  ConversationSummary,
  ConversationCreate,
  Message,
  ChatRequest,
  ChatResponse,
} from '../types';

/**
 * Get all conversations
 */
export async function getConversations(): Promise<ConversationSummary[]> {
  const response = await apiClient.get<ConversationSummary[]>('/conversations/');
  return response.data;
}

/**
 * Create a new conversation
 */
export async function createConversation(data: ConversationCreate): Promise<Conversation> {
  const response = await apiClient.post<Conversation>('/conversations/', data);
  return response.data;
}

/**
 * Get a single conversation by ID
 */
export async function getConversation(conversationId: number): Promise<Conversation> {
  const response = await apiClient.get<Conversation>(`/conversations/${conversationId}`);
  return response.data;
}

/**
 * Delete a conversation
 */
export async function deleteConversation(conversationId: number): Promise<void> {
  await apiClient.delete(`/conversations/${conversationId}`);
}

/**
 * Get all messages in a conversation
 */
export async function getMessages(conversationId: number): Promise<Message[]> {
  const response = await apiClient.get<Message[]>(`/conversations/${conversationId}/messages`);
  return response.data;
}

/**
 * Send a message and get AI response
 */
export async function sendMessage(
  conversationId: number,
  data: ChatRequest
): Promise<ChatResponse> {
  const response = await apiClient.post<ChatResponse>(
    `/conversations/${conversationId}/messages`,
    data
  );
  return response.data;
}

