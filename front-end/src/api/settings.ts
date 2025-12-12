/**
 * Settings API - API Providers, Knowledge Bases, Prompt Templates
 */

import apiClient from './client';
import type {
  APIProvider,
  APIProviderCreate,
  APIProviderUpdate,
  APIProviderTestResult,
  KnowledgeBase,
  KnowledgeBaseCreate,
  KBDocument,
  PromptTemplate,
  PromptTemplateUpdate,
} from '../types';

// ============================================
// API Providers
// ============================================

export async function getAPIProviders(): Promise<APIProvider[]> {
  const response = await apiClient.get<APIProvider[]>('/settings/api-providers/');
  return response.data;
}

export async function createAPIProvider(data: APIProviderCreate): Promise<APIProvider> {
  const response = await apiClient.post<APIProvider>('/settings/api-providers/', data);
  return response.data;
}

export async function updateAPIProvider(
  providerId: number,
  data: APIProviderUpdate
): Promise<APIProvider> {
  const response = await apiClient.put<APIProvider>(`/settings/api-providers/${providerId}`, data);
  return response.data;
}

export async function deleteAPIProvider(providerId: number): Promise<void> {
  await apiClient.delete(`/settings/api-providers/${providerId}`);
}

export async function activateAPIProvider(providerId: number): Promise<APIProvider> {
  const response = await apiClient.post<APIProvider>(
    `/settings/api-providers/${providerId}/activate`
  );
  return response.data;
}

export async function testAPIProvider(providerId: number): Promise<APIProviderTestResult> {
  const response = await apiClient.post<APIProviderTestResult>(
    `/settings/api-providers/${providerId}/test`
  );
  return response.data;
}

export async function testAPIProviderEmbedding(providerId: number): Promise<APIProviderTestResult> {
  const response = await apiClient.post<APIProviderTestResult>(
    `/settings/api-providers/${providerId}/test-embedding`
  );
  return response.data;
}

// ============================================
// Knowledge Bases
// ============================================

export async function getKnowledgeBases(): Promise<KnowledgeBase[]> {
  const response = await apiClient.get<KnowledgeBase[]>('/settings/knowledge-bases/');
  return response.data;
}

export async function createKnowledgeBase(data: KnowledgeBaseCreate): Promise<KnowledgeBase> {
  const response = await apiClient.post<KnowledgeBase>('/settings/knowledge-bases/', data);
  return response.data;
}

export async function deleteKnowledgeBase(kbId: number): Promise<void> {
  await apiClient.delete(`/settings/knowledge-bases/${kbId}`);
}

export async function getKBDocuments(kbId: number): Promise<KBDocument[]> {
  const response = await apiClient.get<KBDocument[]>(`/settings/knowledge-bases/${kbId}/documents`);
  return response.data;
}

export async function uploadDocument(kbId: number, file: File): Promise<{ documents_created: number }> {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await apiClient.post<{ documents_created: number }>(
    `/settings/knowledge-bases/${kbId}/upload`,
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }
  );
  return response.data;
}

export async function embedAllDocuments(kbId: number): Promise<{ embedded_count: number }> {
  const response = await apiClient.post<{ embedded_count: number }>(
    `/settings/knowledge-bases/${kbId}/embed-all`
  );
  return response.data;
}

// ============================================
// Prompt Templates
// ============================================

export async function getPromptTemplates(): Promise<PromptTemplate[]> {
  const response = await apiClient.get<PromptTemplate[]>('/settings/prompt-templates/');
  return response.data;
}

export async function getPromptTemplate(key: string): Promise<PromptTemplate> {
  const response = await apiClient.get<PromptTemplate>(`/settings/prompt-templates/${key}`);
  return response.data;
}

export async function updatePromptTemplate(
  key: string,
  data: PromptTemplateUpdate
): Promise<PromptTemplate> {
  const response = await apiClient.put<PromptTemplate>(`/settings/prompt-templates/${key}`, data);
  return response.data;
}

export async function resetPromptTemplate(key: string): Promise<PromptTemplate> {
  const response = await apiClient.delete<PromptTemplate>(`/settings/prompt-templates/${key}`);
  return response.data;
}

