import { useState } from 'react';

/**
 * Settings page - API providers, Knowledge Base, Prompt Templates
 */
export default function Settings() {
  const [activeTab, setActiveTab] = useState('api-providers');

  const tabs = [
    { id: 'api-providers', label: 'API Providers', icon: '🔌' },
    { id: 'knowledge-base', label: 'Knowledge Base', icon: '📚' },
    { id: 'prompt-templates', label: 'Prompt Templates', icon: '📝' },
  ];

  return (
    <div className="p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">Settings</h1>
          <p className="text-dark-400">
            Configure your LLM providers, knowledge bases, and prompt templates.
          </p>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6 border-b border-dark-700 pb-2">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 rounded-lg transition-colors ${
                activeTab === tab.id
                  ? 'bg-primary-600 text-white'
                  : 'text-dark-400 hover:text-white hover:bg-dark-800'
              }`}
            >
              <span className="mr-2">{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <div className="card">
          {activeTab === 'api-providers' && (
            <div>
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-white">API Providers</h2>
                <button className="btn-primary">+ Add Provider</button>
              </div>
              
              {/* Empty State */}
              <div className="text-center py-12 text-dark-500">
                <div className="text-4xl mb-3">🔌</div>
                <p className="mb-2">No API providers configured</p>
                <p className="text-sm">Add an OpenAI-compatible provider to start chatting</p>
              </div>
            </div>
          )}

          {activeTab === 'knowledge-base' && (
            <div>
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-white">Knowledge Bases</h2>
                <button className="btn-primary">+ Create KB</button>
              </div>
              
              {/* Empty State */}
              <div className="text-center py-12 text-dark-500">
                <div className="text-4xl mb-3">📚</div>
                <p className="mb-2">No knowledge bases created</p>
                <p className="text-sm">Create a KB and upload documents for RAG</p>
              </div>
            </div>
          )}

          {activeTab === 'prompt-templates' && (
            <div>
              <h2 className="text-xl font-semibold text-white mb-6">Prompt Templates</h2>
              
              {/* Template List */}
              <div className="space-y-3">
                {[
                  { key: 'global_system', title: 'Global System Prompt' },
                  { key: 'real_time', title: 'Real-world Time Prompt' },
                  { key: 'roleplay_meta', title: 'Role-play Meta Prompt' },
                  { key: 'dialogue_system', title: 'Dialogue System Prompt' },
                  { key: 'character_config', title: 'Character Config Prompt' },
                  { key: 'character_personality', title: 'Character Personality Prompt' },
                  { key: 'scene', title: 'Scene Prompt' },
                  { key: 'example_dialogues', title: 'Example Dialogues Prompt' },
                ].map((template) => (
                  <div
                    key={template.key}
                    className="flex items-center justify-between p-4 bg-dark-700 rounded-lg 
                               hover:bg-dark-600 transition-colors cursor-pointer"
                  >
                    <div>
                      <h3 className="font-medium text-white">{template.title}</h3>
                      <p className="text-sm text-dark-400">Using default template</p>
                    </div>
                    <button className="btn-secondary text-sm">Edit</button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

