/**
 * Characters page - Manage imported characters
 */
export default function Characters() {
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
          <button className="btn-primary">
            + Import Character
          </button>
        </div>

        {/* Empty State */}
        <div className="card text-center py-16">
          <div className="text-6xl mb-4">👤</div>
          <h3 className="text-xl font-semibold text-white mb-2">
            No Characters Yet
          </h3>
          <p className="text-dark-400 mb-6 max-w-md mx-auto">
            Import characters from the Discover page or upload your own 
            character card (JSON + PNG).
          </p>
          <div className="flex gap-4 justify-center">
            <button className="btn-primary">
              Browse Discover
            </button>
            <button className="btn-secondary">
              Upload Card
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

