/**
 * Characters API - Manage imported characters
 */

import apiClient from './client';
import type { Character, CharacterSummary } from '../types';

/**
 * Get all imported characters
 */
export async function getCharacters(favoriteOnly: boolean = false): Promise<CharacterSummary[]> {
  const params = favoriteOnly ? { favorite_only: true } : {};
  const response = await apiClient.get<CharacterSummary[]>('/characters/', { params });
  return response.data;
}

/**
 * Get a single character by ID
 */
export async function getCharacter(characterId: number): Promise<Character> {
  const response = await apiClient.get<Character>(`/characters/${characterId}`);
  return response.data;
}

/**
 * Update a character
 */
export async function updateCharacter(
  characterId: number,
  data: Partial<Character>
): Promise<Character> {
  const response = await apiClient.put<Character>(`/characters/${characterId}`, data);
  return response.data;
}

/**
 * Delete a character
 */
export async function deleteCharacter(characterId: number): Promise<void> {
  await apiClient.delete(`/characters/${characterId}`);
}

/**
 * Toggle favorite status for a character
 */
export async function toggleFavorite(characterId: number): Promise<Character> {
  const response = await apiClient.post<Character>(`/characters/${characterId}/favorite`);
  return response.data;
}

