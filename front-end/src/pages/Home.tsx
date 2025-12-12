import { Link } from 'react-router-dom';

/**
 * Home page - Welcome and quick actions
 */
export default function Home() {
  return (
    <div className="p-8">
      <div className="max-w-4xl mx-auto">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-white mb-4">
            Welcome to <span className="text-primary-400">RPGChat.AI</span>
          </h1>
          <p className="text-dark-300 text-lg max-w-2xl mx-auto">
            Your AI-powered roleplay companion. Create immersive conversations with 
            custom characters, powered by cutting-edge LLMs and RAG technology.
          </p>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          <Link to="/discover" className="card hover:border-primary-500 transition-colors group">
            <div className="text-3xl mb-3">🔍</div>
            <h3 className="text-lg font-semibold text-white group-hover:text-primary-400 mb-2">
              Discover Characters
            </h3>
            <p className="text-dark-400 text-sm">
              Browse official character cards and start chatting instantly.
            </p>
          </Link>

          <Link to="/characters" className="card hover:border-primary-500 transition-colors group">
            <div className="text-3xl mb-3">👤</div>
            <h3 className="text-lg font-semibold text-white group-hover:text-primary-400 mb-2">
              My Characters
            </h3>
            <p className="text-dark-400 text-sm">
              Manage your imported characters and create new ones.
            </p>
          </Link>

          <Link to="/settings" className="card hover:border-primary-500 transition-colors group">
            <div className="text-3xl mb-3">⚙️</div>
            <h3 className="text-lg font-semibold text-white group-hover:text-primary-400 mb-2">
              Configure API
            </h3>
            <p className="text-dark-400 text-sm">
              Set up your LLM provider and customize prompts.
            </p>
          </Link>
        </div>

        {/* Status Section */}
        <div className="card">
          <h2 className="text-lg font-semibold text-white mb-4">System Status</h2>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-dark-300">Backend API</span>
              <span className="text-green-400 flex items-center gap-2">
                <span className="w-2 h-2 bg-green-400 rounded-full"></span>
                Connected
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-dark-300">Database</span>
              <span className="text-green-400 flex items-center gap-2">
                <span className="w-2 h-2 bg-green-400 rounded-full"></span>
                Connected
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-dark-300">LLM Provider</span>
              <span className="text-yellow-400 flex items-center gap-2">
                <span className="w-2 h-2 bg-yellow-400 rounded-full"></span>
                Not Configured
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

