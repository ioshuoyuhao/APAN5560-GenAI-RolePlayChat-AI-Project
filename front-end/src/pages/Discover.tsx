/**
 * Discover page - Browse official character cards
 */
export default function Discover() {
  // Placeholder character data
  const characters = [
    { id: 1, name: 'Lynae', tagline: 'Adventurous city explorer', avatar: '🧝‍♀️' },
    { id: 2, name: 'Moryne', tagline: 'Mysterious tavern keeper', avatar: '🧙‍♂️' },
    { id: 3, name: 'Coming Soon', tagline: 'More characters on the way', avatar: '❓' },
  ];

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

        {/* Character Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {characters.map((char) => (
            <div
              key={char.id}
              className="card hover:border-primary-500 transition-colors cursor-pointer group"
            >
              {/* Avatar */}
              <div className="w-full aspect-square bg-dark-700 rounded-lg mb-4 flex items-center justify-center text-6xl">
                {char.avatar}
              </div>
              
              {/* Info */}
              <h3 className="text-lg font-semibold text-white group-hover:text-primary-400 mb-1">
                {char.name}
              </h3>
              <p className="text-dark-400 text-sm mb-4">{char.tagline}</p>
              
              {/* Actions */}
              <div className="flex gap-2">
                <button className="btn-primary flex-1 text-sm">
                  Import & Chat
                </button>
                <button className="btn-secondary text-sm px-3">
                  ⬇️
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

