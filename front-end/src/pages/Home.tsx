import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { checkBackendHealth, checkDatabaseHealth } from '../api/client';
import { getAPIProviders } from '../api/settings';

type StatusType = 'loading' | 'connected' | 'disconnected' | 'configured' | 'not_configured';

interface SystemStatus {
  backend: StatusType;
  database: StatusType;
  llmProvider: StatusType;
  providerName?: string;
}

/**
 * Home page - Welcome and quick actions
 */
export default function Home() {
  const [status, setStatus] = useState<SystemStatus>({
    backend: 'loading',
    database: 'loading',
    llmProvider: 'loading',
  });

  // Check system status on mount
  useEffect(() => {
    async function checkStatus() {
      // Check backend health
      const backendOk = await checkBackendHealth();
      setStatus((prev) => ({
        ...prev,
        backend: backendOk ? 'connected' : 'disconnected',
      }));

      // Check database health
      const dbOk = await checkDatabaseHealth();
      setStatus((prev) => ({
        ...prev,
        database: dbOk ? 'connected' : 'disconnected',
      }));

      // Check LLM provider
      try {
        const providers = await getAPIProviders();
        const activeProvider = providers.find((p) => p.is_active);
        setStatus((prev) => ({
          ...prev,
          llmProvider: activeProvider ? 'configured' : 'not_configured',
          providerName: activeProvider?.name,
        }));
      } catch {
        setStatus((prev) => ({
          ...prev,
          llmProvider: 'not_configured',
        }));
      }
    }

    checkStatus();
  }, []);

  // Helper to render status badge
  const renderStatus = (type: StatusType, label?: string) => {
    switch (type) {
      case 'loading':
        return (
          <span className="text-dark-400 flex items-center gap-2">
            <span className="w-2 h-2 bg-dark-400 rounded-full animate-pulse"></span>
            Checking...
          </span>
        );
      case 'connected':
      case 'configured':
        return (
          <span className="text-green-400 flex items-center gap-2">
            <span className="w-2 h-2 bg-green-400 rounded-full"></span>
            {label || 'Connected'}
          </span>
        );
      case 'disconnected':
        return (
          <span className="text-red-400 flex items-center gap-2">
            <span className="w-2 h-2 bg-red-400 rounded-full"></span>
            Disconnected
          </span>
        );
      case 'not_configured':
        return (
          <span className="text-yellow-400 flex items-center gap-2">
            <span className="w-2 h-2 bg-yellow-400 rounded-full"></span>
            Not Configured
          </span>
        );
    }
  };

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
              {renderStatus(status.backend)}
            </div>
            <div className="flex items-center justify-between">
              <span className="text-dark-300">Database</span>
              {renderStatus(status.database)}
            </div>
            <div className="flex items-center justify-between">
              <span className="text-dark-300">LLM Provider</span>
              {renderStatus(
                status.llmProvider,
                status.providerName ? `${status.providerName} (Active)` : undefined
              )}
            </div>
          </div>

          {/* Quick Setup Hint */}
          {status.llmProvider === 'not_configured' && (
            <div className="mt-4 p-3 bg-yellow-900/20 border border-yellow-600/30 rounded-lg">
              <p className="text-yellow-300 text-sm">
                💡 <strong>Tip:</strong> Go to{' '}
                <Link to="/settings" className="underline hover:text-yellow-200">
                  Settings → API Providers
                </Link>{' '}
                to configure your LLM provider and start chatting!
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

