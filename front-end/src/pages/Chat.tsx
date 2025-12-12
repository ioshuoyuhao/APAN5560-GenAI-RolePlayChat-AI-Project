import { useState, useEffect, useRef } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import {
  getConversations,
  getMessages,
  sendMessage,
  deleteConversation,
} from '../api/conversations';
import { getCharacters } from '../api/characters';
import { createConversation } from '../api/conversations';
import type { ConversationSummary, Message, CharacterSummary } from '../types';

/**
 * Chat page - Conversation interface
 */
export default function Chat() {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // State
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [characters, setCharacters] = useState<CharacterSummary[]>([]);
  const [selectedConversation, setSelectedConversation] = useState<number | null>(null);
  const [messageInput, setMessageInput] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [showNewChatModal, setShowNewChatModal] = useState(false);

  // Get conversation ID from URL
  const conversationIdFromUrl = searchParams.get('conversation');

  // Scroll to bottom when messages change
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Fetch conversations on mount
  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        const [convos, chars] = await Promise.all([
          getConversations(),
          getCharacters(),
        ]);
        setConversations(convos);
        setCharacters(chars);

        // Auto-select conversation from URL or first one
        if (conversationIdFromUrl) {
          const id = parseInt(conversationIdFromUrl);
          if (convos.find((c) => c.id === id)) {
            setSelectedConversation(id);
          }
        } else if (convos.length > 0) {
          setSelectedConversation(convos[0].id);
        }
      } catch (err) {
        console.error('Failed to fetch conversations:', err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  // Fetch messages when conversation changes
  useEffect(() => {
    if (!selectedConversation) {
      setMessages([]);
      return;
    }

    async function fetchMessages() {
      try {
        const msgs = await getMessages(selectedConversation!);
        setMessages(msgs);
      } catch (err) {
        console.error('Failed to fetch messages:', err);
      }
    }
    fetchMessages();

    // Update URL
    setSearchParams({ conversation: selectedConversation.toString() });
  }, [selectedConversation]);

  // Handle send message
  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!messageInput.trim() || !selectedConversation || sending) return;

    const userInput = messageInput.trim();
    setMessageInput('');
    setSending(true);

    // Optimistically add user message
    const tempUserMsg: Message = {
      id: Date.now(),
      conversation_id: selectedConversation,
      role: 'user',
      content: userInput,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMsg]);

    try {
      const response = await sendMessage(selectedConversation, { content: userInput });
      
      // Replace temp message with real ones
      setMessages((prev) => [
        ...prev.filter((m) => m.id !== tempUserMsg.id),
        response.user_message,
        response.assistant_message,
      ]);

      // Update conversation list preview
      setConversations((prev) =>
        prev.map((c) =>
          c.id === selectedConversation
            ? { ...c, last_message_preview: response.assistant_message.content.slice(0, 100) }
            : c
        )
      );
    } catch (err) {
      console.error('Failed to send message:', err);
      // Remove temp message on error
      setMessages((prev) => prev.filter((m) => m.id !== tempUserMsg.id));
      alert('Failed to send message. Make sure an API provider is configured and active.');
    } finally {
      setSending(false);
    }
  };

  // Handle new conversation
  const handleNewConversation = async (characterId: number) => {
    try {
      const conversation = await createConversation({ character_id: characterId });
      setConversations((prev) => [
        {
          id: conversation.id,
          character_id: conversation.character_id,
          title: conversation.title,
          updated_at: conversation.updated_at,
          character_name: conversation.character_name,
          character_avatar: conversation.character_avatar,
          last_message_preview: null,
        },
        ...prev,
      ]);
      setSelectedConversation(conversation.id);
      setShowNewChatModal(false);
    } catch (err) {
      console.error('Failed to create conversation:', err);
      alert('Failed to create conversation.');
    }
  };

  // Handle delete conversation
  const handleDeleteConversation = async (convId: number, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm('Delete this conversation?')) return;

    try {
      await deleteConversation(convId);
      setConversations((prev) => prev.filter((c) => c.id !== convId));
      if (selectedConversation === convId) {
        setSelectedConversation(conversations.find((c) => c.id !== convId)?.id || null);
      }
    } catch (err) {
      console.error('Failed to delete conversation:', err);
    }
  };

  // Get current conversation details
  const currentConversation = conversations.find((c) => c.id === selectedConversation);

  return (
    <div className="h-screen flex">
      {/* Conversation List Sidebar */}
      <div className="w-80 bg-dark-900 border-r border-dark-700 flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-dark-700 flex items-center justify-between">
          <h2 className="font-semibold text-white">Conversations</h2>
          <button
            className="btn-secondary text-sm px-3 py-1"
            onClick={() => setShowNewChatModal(true)}
          >
            + New
          </button>
        </div>

        {/* Conversation List */}
        <div className="flex-1 overflow-y-auto">
          {loading ? (
            <div className="text-center py-8 text-dark-500">
              <p className="text-sm">Loading...</p>
            </div>
          ) : conversations.length === 0 ? (
            <div className="text-center py-8 text-dark-500">
              <p className="text-sm">No conversations yet</p>
              <p className="text-xs mt-1">Import a character to start</p>
            </div>
          ) : (
            <div className="p-2 space-y-1">
              {conversations.map((conv) => (
                <div
                  key={conv.id}
                  onClick={() => setSelectedConversation(conv.id)}
                  className={`p-3 rounded-lg cursor-pointer group transition-colors ${
                    selectedConversation === conv.id
                      ? 'bg-primary-600/20 border border-primary-500/50'
                      : 'hover:bg-dark-800'
                  }`}
                >
                  <div className="flex items-start gap-3">
                    {/* Avatar */}
                    <div className="w-10 h-10 rounded-full bg-dark-700 flex-shrink-0 overflow-hidden">
                      {conv.character_avatar ? (
                        <img
                          src={`http://127.0.0.1:8000${conv.character_avatar}`}
                          alt=""
                          className="w-full h-full object-cover"
                          onError={(e) => {
                            (e.target as HTMLImageElement).style.display = 'none';
                          }}
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center text-lg">
                          🧝
                        </div>
                      )}
                    </div>
                    
                    {/* Info */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <h3 className="font-medium text-white text-sm truncate">
                          {conv.character_name || 'Unknown'}
                        </h3>
                        <button
                          onClick={(e) => handleDeleteConversation(conv.id, e)}
                          className="opacity-0 group-hover:opacity-100 text-dark-500 hover:text-red-400 text-xs"
                        >
                          ✕
                        </button>
                      </div>
                      <p className="text-xs text-dark-400 truncate mt-0.5">
                        {conv.last_message_preview || conv.title || 'New conversation'}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 flex flex-col bg-dark-850">
        {/* Chat Header */}
        <div className="h-16 bg-dark-900 border-b border-dark-700 flex items-center px-6">
          {currentConversation ? (
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-dark-700 overflow-hidden">
                {currentConversation.character_avatar ? (
                  <img
                    src={`http://127.0.0.1:8000${currentConversation.character_avatar}`}
                    alt=""
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-lg">🧝</div>
                )}
              </div>
              <div>
                <h3 className="font-semibold text-white">
                  {currentConversation.character_name || 'Unknown'}
                </h3>
                <p className="text-xs text-dark-400">{currentConversation.title}</p>
              </div>
            </div>
          ) : (
            <span className="text-dark-400">Select a conversation to start chatting</span>
          )}
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-6">
          {!selectedConversation ? (
            <div className="h-full flex items-center justify-center">
              <div className="text-center text-dark-500">
                <div className="text-6xl mb-4">💬</div>
                <h3 className="text-xl font-semibold text-white mb-2">Start a Conversation</h3>
                <p className="max-w-md">
                  Select an existing conversation from the sidebar or create a new one with an
                  imported character.
                </p>
                <button
                  className="btn-primary mt-4"
                  onClick={() => setShowNewChatModal(true)}
                >
                  + New Conversation
                </button>
              </div>
            </div>
          ) : messages.length === 0 ? (
            <div className="h-full flex items-center justify-center">
              <div className="text-center text-dark-500">
                <div className="text-4xl mb-4">👋</div>
                <p>Start the conversation by sending a message!</p>
              </div>
            </div>
          ) : (
            <div className="space-y-4 max-w-4xl mx-auto">
              {messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                      msg.role === 'user'
                        ? 'bg-primary-600 text-white'
                        : 'bg-dark-700 text-white'
                    }`}
                  >
                    <p className="whitespace-pre-wrap">{msg.content}</p>
                    <p
                      className={`text-xs mt-1 ${
                        msg.role === 'user' ? 'text-primary-200' : 'text-dark-400'
                      }`}
                    >
                      {new Date(msg.created_at).toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              ))}
              {sending && (
                <div className="flex justify-start">
                  <div className="bg-dark-700 rounded-2xl px-4 py-3">
                    <div className="flex gap-1">
                      <span className="w-2 h-2 bg-dark-400 rounded-full animate-bounce" />
                      <span
                        className="w-2 h-2 bg-dark-400 rounded-full animate-bounce"
                        style={{ animationDelay: '0.1s' }}
                      />
                      <span
                        className="w-2 h-2 bg-dark-400 rounded-full animate-bounce"
                        style={{ animationDelay: '0.2s' }}
                      />
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="p-4 border-t border-dark-700 bg-dark-900">
          <form onSubmit={handleSendMessage} className="flex gap-3 max-w-4xl mx-auto">
            <input
              type="text"
              value={messageInput}
              onChange={(e) => setMessageInput(e.target.value)}
              placeholder={selectedConversation ? 'Type your message...' : 'Select a conversation first'}
              disabled={!selectedConversation || sending}
              className="flex-1 bg-dark-800 border border-dark-600 rounded-lg px-4 py-3 
                         text-white placeholder-dark-500 focus:outline-none focus:border-primary-500
                         disabled:opacity-50 disabled:cursor-not-allowed"
            />
            <button
              type="submit"
              disabled={!selectedConversation || !messageInput.trim() || sending}
              className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {sending ? '...' : 'Send'}
            </button>
          </form>
        </div>
      </div>

      {/* New Chat Modal */}
      {showNewChatModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="card max-w-md w-full mx-4">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-white">New Conversation</h2>
              <button
                onClick={() => setShowNewChatModal(false)}
                className="text-dark-400 hover:text-white"
              >
                ✕
              </button>
            </div>

            {characters.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-dark-400 mb-4">No characters imported yet.</p>
                <button
                  className="btn-primary"
                  onClick={() => {
                    setShowNewChatModal(false);
                    navigate('/discover');
                  }}
                >
                  Browse Discover
                </button>
              </div>
            ) : (
              <div className="space-y-2 max-h-96 overflow-y-auto">
                <p className="text-dark-400 text-sm mb-3">Select a character to chat with:</p>
                {characters.map((char) => (
                  <button
                    key={char.id}
                    onClick={() => handleNewConversation(char.id)}
                    className="w-full p-3 rounded-lg bg-dark-700 hover:bg-dark-600 
                               transition-colors flex items-center gap-3 text-left"
                  >
                    <div className="w-10 h-10 rounded-full bg-dark-600 flex-shrink-0 overflow-hidden">
                      {char.avatar_url ? (
                        <img
                          src={`http://127.0.0.1:8000${char.avatar_url}`}
                          alt=""
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center">🧝</div>
                      )}
                    </div>
                    <div>
                      <h3 className="font-medium text-white">{char.name}</h3>
                      <p className="text-xs text-dark-400 truncate">
                        {char.description?.slice(0, 50) || 'Start a conversation'}
                      </p>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
