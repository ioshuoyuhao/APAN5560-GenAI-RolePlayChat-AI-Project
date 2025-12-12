import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getCharacters, toggleFavorite, deleteCharacter } from '../api';
import { createConversation } from '../api/conversations';
import type { CharacterSummary } from '../types';

/**
 * Characters page - Manage imported characters
 */
export default function Characters() {
  const navigate = useNavigate();
  const [characters, setCharacters] = useState<CharacterSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showFavoritesOnly, setShowFavoritesOnly] = useState(false);

  // Fetch characters
  const fetchCharacters = async () => {
    try {
      setLoading(true);
      const data = await getCharacters(showFavoritesOnly);
      setCharacters(data);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch characters:', err);
      setError('Failed to load characters.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCharacters();
  }, [showFavoritesOnly]);

  // Handle toggle favorite
  const handleToggleFavorite = async (characterId: number, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      const updated = await toggleFavorite(characterId);
      setCharacters((prev) =>
        prev.map((c) => (c.id === characterId ? { ...c, is_favorite: updated.is_favorite } : c))
      );
    } catch (err) {
      console.error('Failed to toggle favorite:', err);
    }
  };

  // Handle delete
  const handleDelete = async (characterId: number, charName: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm(`Delete "${charName}"? This will also delete all conversations with this character.`)) {
      return;
    }
    try {
      await deleteCharacter(characterId);
      setCharacters((prev) => prev.filter((c) => c.id !== characterId));
    } catch (err) {
      console.error('Failed to delete character:', err);
      alert('Failed to delete character.');
    }
  };

  // Handle start chat
  const handleStartChat = async (characterId: number) => {
    try {
      const conversation = await createConversation({ character_id: characterId });
      navigate(`/chat?conversation=${conversation.id}`);
    } catch (err) {
      console.error('Failed to create conversation:', err);
      alert('Failed to start conversation. Make sure an API provider is configured.');
    }
  };

  return (
    <div className="p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">My Characters</h1>
            <p className="text-dark-400">
              Manage your imported characters and favorites.
            </p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => setShowFavoritesOnly(!showFavoritesOnly)}
              className={`btn-secondary ${showFavoritesOnly ? 'bg-yellow-600/20 border-yellow-500' : ''}`}
            >
              {showFavoritesOnly ? '⭐ Favorites' : '☆ All'}
            </button>
            <button 
              className="btn-primary"
              onClick={() => navigate('/discover')}
            >
              + Import Character
            </button>
          </div>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="text-center py-16">
            <div className="text-4xl mb-4 animate-pulse">👤</div>
            <p className="text-dark-400">Loading characters...</p>
          </div>
        )}

        {/* Error State */}
        {error && !loading && (
          <div className="card text-center py-16 border-red-500/50">
            <div className="text-4xl mb-4">⚠️</div>
            <p className="text-red-400 mb-4">{error}</p>
            <button onClick={fetchCharacters} className="btn-secondary">
              Retry
            </button>
          </div>
        )}

        {/* Empty State */}
        {!loading && !error && characters.length === 0 && (
          <div className="card text-center py-16">
            <div className="text-6xl mb-4">👤</div>
            <h3 className="text-xl font-semibold text-white mb-2">
              {showFavoritesOnly ? 'No Favorite Characters' : 'No Characters Yet'}
            </h3>
            <p className="text-dark-400 mb-6 max-w-md mx-auto">
              {showFavoritesOnly
                ? 'Star some characters to add them to your favorites.'
                : 'Import characters from the Discover page or upload your own character card (JSON + PNG).'}
            </p>
            <div className="flex gap-4 justify-center">
              {showFavoritesOnly ? (
                <button 
                  className="btn-secondary"
                  onClick={() => setShowFavoritesOnly(false)}
                >
                  Show All
                </button>
              ) : (
                <>
                  <button 
                    className="btn-primary"
                    onClick={() => navigate('/discover')}
                  >
                    Browse Discover
                  </button>
                  <button className="btn-secondary" disabled>
                    Upload Card
                  </button>
                </>
              )}
            </div>
          </div>
        )}

        {/* Character Grid */}
        {!loading && !error && characters.length > 0 && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {characters.map((char) => (
              <div
                key={char.id}
                onClick={() => handleStartChat(char.id)}
                className="card hover:border-primary-500 transition-colors cursor-pointer group relative"
              >
                {/* Favorite Button */}
                <button
                  onClick={(e) => handleToggleFavorite(char.id, e)}
                  className="absolute top-3 right-3 text-2xl hover:scale-110 transition-transform z-10"
                  title={char.is_favorite ? 'Remove from favorites' : 'Add to favorites'}
                >
                  {char.is_favorite ? '⭐' : '☆'}
                </button>

                {/* Avatar */}
                <div className="w-full aspect-square bg-dark-700 rounded-lg mb-4 overflow-hidden">
                  {char.avatar_url ? (
                    <img
                      src={`http://127.0.0.1:8000${char.avatar_url}`}
                      alt={char.name}
                      className="w-full h-full object-cover"
                      onError={(e) => {
                        (e.target as HTMLImageElement).style.display = 'none';
                        (e.target as HTMLImageElement).parentElement!.innerHTML = 
                          '<div class="w-full h-full flex items-center justify-center text-6xl">🧝</div>';
                      }}
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-6xl">
                      🧝
                    </div>
                  )}
                </div>
                
                {/* Info */}
                <h3 className="text-lg font-semibold text-white group-hover:text-primary-400 mb-1 pr-8">
                  {char.name}
                </h3>
                <p className="text-dark-400 text-sm mb-2 line-clamp-2">
                  {char.description?.slice(0, 80) || 'A mysterious character...'}
                  {char.description && char.description.length > 80 && '...'}
                </p>
                
                {/* Tags */}
                {char.tags && char.tags.length > 0 && (
                  <div className="flex flex-wrap gap-1 mb-4">
                    {char.tags.slice(0, 3).map((tag) => (
                      <span 
                        key={tag} 
                        className="px-2 py-0.5 bg-dark-700 rounded text-xs text-dark-300"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                )}
                
                {/* Actions */}
                <div className="flex gap-2 mt-auto">
                  <button className="btn-primary flex-1 text-sm">
                    Start Chat
                  </button>
                  <button 
                    className="btn-secondary text-sm px-3 text-red-400 hover:bg-red-900/30"
                    onClick={(e) => handleDelete(char.id, char.name, e)}
                    title="Delete character"
                  >
                    🗑️
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
