/**
 * Discover API - Browse and import official characters
 */

import apiClient from './client';
import type { OfficialCharacter, ImportResponse } from '../types';

/**
 * Get all official characters available for import
 */
export async function getOfficialCharacters(): Promise<OfficialCharacter[]> {
  const response = await apiClient.get<OfficialCharacter[]>('/discover/characters');
  return response.data;
}

/**
 * Get a single official character by ID
 */
export async function getOfficialCharacter(charId: string): Promise<OfficialCharacter> {
  const response = await apiClient.get<OfficialCharacter>(`/discover/characters/${charId}`);
  return response.data;
}

/**
 * Import an official character and start a new conversation
 * Returns the new character_id and conversation_id
 */
export async function importOfficialCharacter(charId: string): Promise<ImportResponse> {
  const response = await apiClient.post<ImportResponse>(`/discover/characters/${charId}/import`);
  return response.data;
}

/**
 * Get avatar URL for an official character
 */
export function getAvatarUrl(charId: string): string {
  return `http://127.0.0.1:8000/api/discover/characters/${charId}/avatar`;
}

/**
 * Download character card JSON
 */
export async function downloadCharacterCard(charId: string): Promise<Blob> {
  const response = await apiClient.get(`/discover/characters/${charId}/download`, {
    responseType: 'blob',
  });
  return response.data;
}

