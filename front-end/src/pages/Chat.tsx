/**
 * Chat page - Conversation interface
 */
export default function Chat() {
  return (
    <div className="h-screen flex">
      {/* Conversation List Sidebar */}
      <div className="w-80 bg-dark-900 border-r border-dark-700 flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-dark-700 flex items-center justify-between">
          <h2 className="font-semibold text-white">Conversations</h2>
          <button className="btn-secondary text-sm px-3 py-1">+ New</button>
        </div>

        {/* Conversation List */}
        <div className="flex-1 overflow-y-auto p-2">
          {/* Empty State */}
          <div className="text-center py-8 text-dark-500">
            <p className="text-sm">No conversations yet</p>
            <p className="text-xs mt-1">Import a character to start</p>
          </div>
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Chat Header */}
        <div className="h-16 bg-dark-900 border-b border-dark-700 flex items-center px-6">
          <span className="text-dark-400">Select a conversation to start chatting</span>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-6 flex items-center justify-center">
          <div className="text-center text-dark-500">
            <div className="text-6xl mb-4">💬</div>
            <h3 className="text-xl font-semibold text-white mb-2">
              Start a Conversation
            </h3>
            <p className="max-w-md">
              Select an existing conversation from the sidebar or create a new one 
              with an imported character.
            </p>
          </div>
        </div>

        {/* Input Area */}
        <div className="p-4 border-t border-dark-700 bg-dark-900">
          <div className="flex gap-3">
            <input
              type="text"
              placeholder="Type your message..."
              disabled
              className="flex-1 bg-dark-800 border border-dark-600 rounded-lg px-4 py-3 
                         text-white placeholder-dark-500 focus:outline-none focus:border-primary-500
                         disabled:opacity-50 disabled:cursor-not-allowed"
            />
            <button disabled className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed">
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

