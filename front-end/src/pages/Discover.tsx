import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getOfficialCharacters, importOfficialCharacter, getAvatarUrl, downloadCharacterCard } from '../api';
import type { OfficialCharacter } from '../types';

/**
 * Discover page - Browse official character cards
 */
export default function Discover() {
  const navigate = useNavigate();
  const [characters, setCharacters] = useState<OfficialCharacter[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [importing, setImporting] = useState<string | null>(null);

  // Fetch official characters on mount
  useEffect(() => {
    async function fetchCharacters() {
      try {
        setLoading(true);
        const data = await getOfficialCharacters();
        setCharacters(data);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch characters:', err);
        setError('Failed to load characters. Is the backend running?');
      } finally {
        setLoading(false);
      }
    }
    fetchCharacters();
  }, []);

  // Handle import and start chat
  const handleImport = async (charId: string) => {
    try {
      setImporting(charId);
      const result = await importOfficialCharacter(charId);
      // Navigate to chat with the new conversation
      navigate(`/chat?conversation=${result.conversation_id}`);
    } catch (err) {
      console.error('Failed to import character:', err);
      alert('Failed to import character. Please try again.');
    } finally {
      setImporting(null);
    }
  };

  // Handle download
  const handleDownload = async (charId: string, charName: string) => {
    try {
      const blob = await downloadCharacterCard(charId);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${charName}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Failed to download character:', err);
      alert('Failed to download character card.');
    }
  };

  return (
    <div className="p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">Discover Characters</h1>
          <p className="text-dark-400">
            Browse official character cards. Click to import and start chatting!
          </p>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="text-center py-16">
            <div className="text-4xl mb-4 animate-pulse">🔍</div>
            <p className="text-dark-400">Loading characters...</p>
          </div>
        )}

        {/* Error State */}
        {error && !loading && (
          <div className="card text-center py-16 border-red-500/50">
            <div className="text-4xl mb-4">⚠️</div>
            <p className="text-red-400 mb-4">{error}</p>
            <button 
              onClick={() => window.location.reload()} 
              className="btn-secondary"
            >
              Retry
            </button>
          </div>
        )}

        {/* Empty State */}
        {!loading && !error && characters.length === 0 && (
          <div className="card text-center py-16">
            <div className="text-4xl mb-4">📭</div>
            <p className="text-dark-400">No official characters available yet.</p>
          </div>
        )}

        {/* Character Grid */}
        {!loading && !error && characters.length > 0 && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {characters.map((char) => (
              <div
                key={char.id}
                className="card hover:border-primary-500 transition-colors group"
              >
                {/* Avatar */}
                <div className="w-full aspect-square bg-dark-700 rounded-lg mb-4 overflow-hidden">
                  {char.avatar_url ? (
                    <img
                      src={getAvatarUrl(char.id)}
                      alt={char.name}
                      className="w-full h-full object-cover"
                      onError={(e) => {
                        // Fallback to emoji if image fails
                        (e.target as HTMLImageElement).style.display = 'none';
                        (e.target as HTMLImageElement).parentElement!.innerHTML = '<div class="w-full h-full flex items-center justify-center text-6xl">🧝</div>';
                      }}
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-6xl">
                      🧝
                    </div>
                  )}
                </div>
                
                {/* Info */}
                <h3 className="text-lg font-semibold text-white group-hover:text-primary-400 mb-1">
                  {char.name}
                </h3>
                <p className="text-dark-400 text-sm mb-2 line-clamp-2">
                  {char.description?.slice(0, 100) || 'A mysterious character...'}
                  {char.description && char.description.length > 100 && '...'}
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
                    {char.tags.length > 3 && (
                      <span className="px-2 py-0.5 text-xs text-dark-500">
                        +{char.tags.length - 3}
                      </span>
                    )}
                  </div>
                )}
                
                {/* Actions */}
                <div className="flex gap-2 mt-auto">
                  <button 
                    className="btn-primary flex-1 text-sm disabled:opacity-50"
                    onClick={() => handleImport(char.id)}
                    disabled={importing === char.id}
                  >
                    {importing === char.id ? 'Importing...' : 'Import & Chat'}
                  </button>
                  <button 
                    className="btn-secondary text-sm px-3"
                    onClick={() => handleDownload(char.id, char.name)}
                    title="Download character card"
                  >
                    ⬇️
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
