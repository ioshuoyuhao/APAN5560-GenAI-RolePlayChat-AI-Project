import { useState, useEffect } from 'react';
import {
  getAPIProviders,
  createAPIProvider,
  updateAPIProvider,
  deleteAPIProvider,
  activateAPIProvider,
  testAPIProvider,
  testAPIProviderEmbedding,
  getKnowledgeBases,
  createKnowledgeBase,
  deleteKnowledgeBase,
  uploadDocument,
  embedAllDocuments,
  getPromptTemplates,
  updatePromptTemplate,
  resetPromptTemplate,
} from '../api/settings';
import type {
  APIProvider,
  APIProviderCreate,
  KnowledgeBase,
  PromptTemplate,
  ProviderType,
} from '../types';

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
          {activeTab === 'api-providers' && <APIProvidersTab />}
          {activeTab === 'knowledge-base' && <KnowledgeBaseTab />}
          {activeTab === 'prompt-templates' && <PromptTemplatesTab />}
        </div>
      </div>
    </div>
  );
}

// ============================================
// API Providers Tab
// ============================================

function APIProvidersTab() {
  const [providers, setProviders] = useState<APIProvider[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [testing, setTesting] = useState<number | null>(null);

  const [formData, setFormData] = useState<APIProviderCreate>({
    name: '',
    provider_type: 'openai',
    base_url: 'https://api.siliconflow.cn/v1',
    api_key: '',
    chat_model_id: 'deepseek-ai/DeepSeek-V3',
    embedding_model_id: 'BAAI/bge-m3',
  });

  useEffect(() => {
    fetchProviders();
  }, []);

  const fetchProviders = async () => {
    try {
      setLoading(true);
      const data = await getAPIProviders();
      setProviders(data);
    } catch (err) {
      console.error('Failed to fetch providers:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingId) {
        await updateAPIProvider(editingId, formData);
      } else {
        await createAPIProvider(formData);
      }
      await fetchProviders();
      resetForm();
    } catch (err) {
      console.error('Failed to save provider:', err);
      alert('Failed to save provider.');
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Delete this provider?')) return;
    try {
      await deleteAPIProvider(id);
      await fetchProviders();
    } catch (err) {
      console.error('Failed to delete provider:', err);
    }
  };

  const handleActivate = async (id: number) => {
    try {
      await activateAPIProvider(id);
      await fetchProviders();
    } catch (err) {
      console.error('Failed to activate provider:', err);
    }
  };

  const handleTest = async (id: number) => {
    setTesting(id);
    try {
      const [chatResult, embeddingResult] = await Promise.all([
        testAPIProvider(id),
        testAPIProviderEmbedding(id),
      ]);
      alert(
        `Chat API: ${chatResult.success ? '✅' : '❌'} ${chatResult.message} (${chatResult.latency_ms}ms)\n\n` +
          `Embedding API: ${embeddingResult.success ? '✅' : '❌'} ${embeddingResult.message} (${embeddingResult.latency_ms}ms)`
      );
    } catch (err) {
      console.error('Test failed:', err);
      alert('Test failed. Check console for details.');
    } finally {
      setTesting(null);
    }
  };

  const resetForm = () => {
    setShowForm(false);
    setEditingId(null);
    setFormData({
      name: '',
      provider_type: 'openai',
      base_url: 'https://api.siliconflow.cn/v1',
      api_key: '',
      chat_model_id: 'deepseek-ai/DeepSeek-V3',
      embedding_model_id: 'BAAI/bge-m3',
    });
  };

  const startEdit = (provider: APIProvider) => {
    setEditingId(provider.id);
    setFormData({
      name: provider.name,
      provider_type: provider.provider_type || 'openai',
      base_url: provider.base_url,
      api_key: '', // Don't populate for security
      chat_model_id: provider.chat_model_id,
      embedding_model_id: provider.embedding_model_id,
    });
    setShowForm(true);
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-white">API Providers</h2>
        <button className="btn-primary" onClick={() => setShowForm(true)}>
          + Add Provider
        </button>
      </div>

      {/* Provider Form */}
      {showForm && (
        <form onSubmit={handleSubmit} className="mb-6 p-4 bg-dark-700 rounded-lg space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-dark-300 mb-1">Provider Name</label>
              <input
                type="text"
                required
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="e.g., SiliconFlow DeepSeek"
                className="w-full bg-dark-800 border border-dark-600 rounded px-3 py-2 text-white"
              />
            </div>
            <div>
              <label className="block text-sm text-dark-300 mb-1">Provider Type</label>
              <select
                value={formData.provider_type || 'openai'}
                onChange={(e) => {
                  const newType = e.target.value as ProviderType;
                  // Auto-fill defaults based on provider type
                  if (newType === 'huggingface') {
                    setFormData({
                      ...formData,
                      provider_type: newType,
                      base_url: 'https://ot1bh06tglp35kdk.us-east-1.aws.endpoints.huggingface.cloud',
                      chat_model_id: 'Jingzong/APAN5560',
                      embedding_model_id: '',
                    });
                  } else {
                    setFormData({
                      ...formData,
                      provider_type: newType,
                      base_url: 'https://api.siliconflow.cn/v1',
                      chat_model_id: 'deepseek-ai/DeepSeek-V3',
                      embedding_model_id: 'BAAI/bge-m3',
                    });
                  }
                }}
                className="w-full bg-dark-800 border border-dark-600 rounded px-3 py-2 text-white"
              >
                <option value="openai">OpenAI-compatible</option>
                <option value="huggingface">HuggingFace Inference</option>
              </select>
            </div>
            <div className="col-span-2">
              <label className="block text-sm text-dark-300 mb-1">Base URL</label>
              <input
                type="url"
                required
                value={formData.base_url}
                onChange={(e) => setFormData({ ...formData, base_url: e.target.value })}
                className="w-full bg-dark-800 border border-dark-600 rounded px-3 py-2 text-white"
              />
            </div>
            <div className="col-span-2">
              <label className="block text-sm text-dark-300 mb-1">
                API Key {editingId && '(leave blank to keep existing)'}
              </label>
              <input
                type="password"
                required={!editingId}
                value={formData.api_key}
                onChange={(e) => setFormData({ ...formData, api_key: e.target.value })}
                placeholder={formData.provider_type === 'huggingface' ? 'hf_...' : 'sk-...'}
                className="w-full bg-dark-800 border border-dark-600 rounded px-3 py-2 text-white"
              />
            </div>
            <div>
              <label className="block text-sm text-dark-300 mb-1">Chat Model ID</label>
              <input
                type="text"
                required
                value={formData.chat_model_id}
                onChange={(e) => setFormData({ ...formData, chat_model_id: e.target.value })}
                className="w-full bg-dark-800 border border-dark-600 rounded px-3 py-2 text-white"
              />
            </div>
            <div>
              <label className="block text-sm text-dark-300 mb-1">
                Embedding Model ID <span className="text-dark-500">(optional)</span>
              </label>
              <input
                type="text"
                value={formData.embedding_model_id || ''}
                onChange={(e) => setFormData({ ...formData, embedding_model_id: e.target.value })}
                placeholder="Leave empty if not using RAG"
                className="w-full bg-dark-800 border border-dark-600 rounded px-3 py-2 text-white"
              />
              <p className="text-xs text-dark-500 mt-1">
                Required for Knowledge Base RAG. Self fine-tuned models don't support embeddings.
              </p>
            </div>
          </div>
          <div className="flex gap-2">
            <button type="submit" className="btn-primary">
              {editingId ? 'Update' : 'Create'}
            </button>
            <button type="button" className="btn-secondary" onClick={resetForm}>
              Cancel
            </button>
          </div>
        </form>
      )}

      {/* Provider List */}
      {loading ? (
        <div className="text-center py-8 text-dark-400">Loading...</div>
      ) : providers.length === 0 ? (
        <div className="text-center py-12 text-dark-500">
          <div className="text-4xl mb-3">🔌</div>
          <p className="mb-2">No API providers configured</p>
          <p className="text-sm">Add an OpenAI-compatible provider to start chatting</p>
        </div>
      ) : (
        <div className="space-y-3">
          {providers.map((provider) => (
            <div
              key={provider.id}
              className={`p-4 rounded-lg border ${
                provider.is_active ? 'bg-primary-900/20 border-primary-500' : 'bg-dark-700 border-dark-600'
              }`}
            >
              <div className="flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="font-medium text-white">{provider.name}</h3>
                    {provider.is_active && (
                      <span className="px-2 py-0.5 bg-primary-600 rounded text-xs">Active</span>
                    )}
                    <span className={`px-2 py-0.5 rounded text-xs ${
                      provider.provider_type === 'huggingface' 
                        ? 'bg-yellow-600/30 text-yellow-400' 
                        : 'bg-green-600/30 text-green-400'
                    }`}>
                      {provider.provider_type === 'huggingface' ? 'HuggingFace' : 'OpenAI'}
                    </span>
                  </div>
                  <p className="text-sm text-dark-400 mt-1">{provider.base_url}</p>
                  <p className="text-xs text-dark-500 mt-0.5">
                    Chat: {provider.chat_model_id} | Embedding: {provider.embedding_model_id || '(not set)'}
                  </p>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleTest(provider.id)}
                    disabled={testing === provider.id}
                    className="btn-secondary text-sm"
                  >
                    {testing === provider.id ? '...' : '🧪 Test'}
                  </button>
                  {!provider.is_active && (
                    <button
                      onClick={() => handleActivate(provider.id)}
                      className="btn-secondary text-sm"
                    >
                      Activate
                    </button>
                  )}
                  <button onClick={() => startEdit(provider)} className="btn-secondary text-sm">
                    Edit
                  </button>
                  <button
                    onClick={() => handleDelete(provider.id)}
                    className="btn-secondary text-sm text-red-400"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ============================================
// Knowledge Base Tab
// ============================================

function KnowledgeBaseTab() {
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBase[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [newKBName, setNewKBName] = useState('');
  const [uploading, setUploading] = useState<number | null>(null);
  const [embedding, setEmbedding] = useState<number | null>(null);

  useEffect(() => {
    fetchKBs();
  }, []);

  const fetchKBs = async () => {
    try {
      setLoading(true);
      const data = await getKnowledgeBases();
      setKnowledgeBases(data);
    } catch (err) {
      console.error('Failed to fetch KBs:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateKB = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newKBName.trim()) return;
    try {
      await createKnowledgeBase({ name: newKBName.trim() });
      await fetchKBs();
      setNewKBName('');
      setShowForm(false);
    } catch (err) {
      console.error('Failed to create KB:', err);
      alert('Failed to create knowledge base.');
    }
  };

  const handleDeleteKB = async (id: number) => {
    if (!confirm('Delete this knowledge base and all its documents?')) return;
    try {
      await deleteKnowledgeBase(id);
      await fetchKBs();
    } catch (err) {
      console.error('Failed to delete KB:', err);
    }
  };

  const handleFileUpload = async (kbId: number, file: File) => {
    setUploading(kbId);
    try {
      const result = await uploadDocument(kbId, file);
      alert(`Uploaded and created ${result.documents_created} document chunks.`);
      await fetchKBs();
    } catch (err) {
      console.error('Failed to upload:', err);
      alert('Failed to upload document.');
    } finally {
      setUploading(null);
    }
  };

  const handleEmbedAll = async (kbId: number) => {
    setEmbedding(kbId);
    try {
      const result = await embedAllDocuments(kbId);
      alert(`Embedded ${result.embedded_count} documents.`);
    } catch (err) {
      console.error('Failed to embed:', err);
      alert('Failed to embed documents. Make sure an API provider is active.');
    } finally {
      setEmbedding(null);
    }
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-white">Knowledge Bases</h2>
        <button className="btn-primary" onClick={() => setShowForm(true)}>
          + Create KB
        </button>
      </div>

      {/* Create Form */}
      {showForm && (
        <form onSubmit={handleCreateKB} className="mb-6 p-4 bg-dark-700 rounded-lg flex gap-3">
          <input
            type="text"
            value={newKBName}
            onChange={(e) => setNewKBName(e.target.value)}
            placeholder="Knowledge base name"
            className="flex-1 bg-dark-800 border border-dark-600 rounded px-3 py-2 text-white"
          />
          <button type="submit" className="btn-primary">Create</button>
          <button type="button" className="btn-secondary" onClick={() => setShowForm(false)}>
            Cancel
          </button>
        </form>
      )}

      {/* Embedding Model Reminder */}
      <div className="mb-4 p-3 bg-yellow-900/20 border border-yellow-600/30 rounded-lg">
        <p className="text-sm text-yellow-400">
          ⚠️ <strong>Important:</strong> To use Knowledge Base RAG, ensure your active API provider has an 
          <strong> Embedding Model ID</strong> configured. Self fine-tuned models (e.g., HuggingFace GPT-2) 
          do not support embeddings — use a 3rd party API like SiliconFlow or OpenAI instead.
        </p>
      </div>

      {/* KB List */}
      {loading ? (
        <div className="text-center py-8 text-dark-400">Loading...</div>
      ) : knowledgeBases.length === 0 ? (
        <div className="text-center py-12 text-dark-500">
          <div className="text-4xl mb-3">📚</div>
          <p className="mb-2">No knowledge bases created</p>
          <p className="text-sm">Create a KB and upload documents for RAG</p>
        </div>
      ) : (
        <div className="space-y-3">
          {knowledgeBases.map((kb) => (
            <div key={kb.id} className="p-4 bg-dark-700 rounded-lg">
              <div className="flex items-center justify-between mb-3">
                <div>
                  <h3 className="font-medium text-white">{kb.name}</h3>
                  <p className="text-xs text-dark-400">
                    Created: {new Date(kb.created_at).toLocaleDateString()}
                  </p>
                </div>
                <button
                  onClick={() => handleDeleteKB(kb.id)}
                  className="text-red-400 hover:text-red-300 text-sm"
                >
                  Delete
                </button>
              </div>
              <div className="flex gap-2">
                <label className="btn-secondary text-sm cursor-pointer">
                  {uploading === kb.id ? 'Uploading...' : '📄 Upload Document'}
                  <input
                    type="file"
                    accept=".txt,.md,.pdf"
                    className="hidden"
                    disabled={uploading === kb.id}
                    onChange={(e) => {
                      const file = e.target.files?.[0];
                      if (file) handleFileUpload(kb.id, file);
                    }}
                  />
                </label>
                <button
                  onClick={() => handleEmbedAll(kb.id)}
                  disabled={embedding === kb.id}
                  className="btn-secondary text-sm"
                >
                  {embedding === kb.id ? 'Embedding...' : '🧠 Embed All'}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ============================================
// Prompt Templates Tab
// ============================================

function PromptTemplatesTab() {
  const [templates, setTemplates] = useState<PromptTemplate[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingKey, setEditingKey] = useState<string | null>(null);
  const [editValue, setEditValue] = useState('');

  useEffect(() => {
    fetchTemplates();
  }, []);

  const fetchTemplates = async () => {
    try {
      setLoading(true);
      const data = await getPromptTemplates();
      setTemplates(data);
    } catch (err) {
      console.error('Failed to fetch templates:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!editingKey) return;
    try {
      await updatePromptTemplate(editingKey, { custom_prompt: editValue || null });
      await fetchTemplates();
      setEditingKey(null);
    } catch (err) {
      console.error('Failed to save template:', err);
      alert('Failed to save template.');
    }
  };

  const handleReset = async (key: string) => {
    if (!confirm('Reset to default prompt?')) return;
    try {
      await resetPromptTemplate(key);
      await fetchTemplates();
    } catch (err) {
      console.error('Failed to reset template:', err);
    }
  };

  const startEdit = (template: PromptTemplate) => {
    setEditingKey(template.key);
    setEditValue(template.custom_prompt || template.default_prompt);
  };

  if (loading) {
    return <div className="text-center py-8 text-dark-400">Loading...</div>;
  }

  return (
    <div>
      <h2 className="text-xl font-semibold text-white mb-6">Prompt Templates</h2>

      {/* Edit Modal */}
      {editingKey && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="card max-w-2xl w-full mx-4 max-h-[80vh] overflow-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-white">
                {templates.find((t) => t.key === editingKey)?.title}
              </h3>
              <button
                onClick={() => setEditingKey(null)}
                className="text-dark-400 hover:text-white"
              >
                ✕
              </button>
            </div>
            <textarea
              value={editValue}
              onChange={(e) => setEditValue(e.target.value)}
              rows={15}
              className="w-full bg-dark-700 border border-dark-600 rounded px-3 py-2 text-white 
                         font-mono text-sm resize-none focus:outline-none focus:border-primary-500"
            />
            <p className="text-xs text-dark-400 mt-2">
              Use {`{{char}}`} for character name, {`{{user}}`} for user name, {`{{date}}`} for
              current date.
            </p>
            <div className="flex gap-2 mt-4">
              <button onClick={handleSave} className="btn-primary">
                Save
              </button>
              <button
                onClick={() => {
                  const t = templates.find((t) => t.key === editingKey);
                  if (t) setEditValue(t.default_prompt);
                }}
                className="btn-secondary"
              >
                Copy Default
              </button>
              <button onClick={() => setEditingKey(null)} className="btn-secondary">
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Template List */}
      <div className="space-y-3">
        {templates.map((template) => (
          <div
            key={template.key}
            className="flex items-center justify-between p-4 bg-dark-700 rounded-lg 
                       hover:bg-dark-600 transition-colors"
          >
            <div className="flex-1">
              <h3 className="font-medium text-white">{template.title}</h3>
              <p className="text-sm text-dark-400 mt-0.5">{template.description}</p>
              <p className="text-xs text-dark-500 mt-1">
                {template.custom_prompt ? '✨ Using custom prompt' : 'Using default template'}
              </p>
            </div>
            <div className="flex gap-2">
              <button onClick={() => startEdit(template)} className="btn-secondary text-sm">
                Edit
              </button>
              {template.custom_prompt && (
                <button
                  onClick={() => handleReset(template.key)}
                  className="btn-secondary text-sm text-yellow-400"
                >
                  Reset
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
