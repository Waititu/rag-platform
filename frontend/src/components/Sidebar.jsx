import {
  MessageSquare,
  Plus,
  Clock,
} from "lucide-react";

export default function Sidebar({
  conversations,
  activeConversationId,
  onNewConversation,
  onSelectConversation,
}) {
  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-mark">R</div>

        <div>
          <div className="brand-name">
            RAG Platform
          </div>

          <div className="brand-subtitle">
            Knowledge assistant
          </div>
        </div>
      </div>

      <button
        className="new-chat-button"
        onClick={onNewConversation}
      >
        <Plus size={17} />
        New conversation
      </button>

      <div className="sidebar-heading">
        <Clock size={14} />
        Conversations
      </div>

      <div className="conversation-list">
        {conversations.length === 0 && (
          <div className="sidebar-empty">
            No conversations yet.
          </div>
        )}

        {conversations.map((conversation) => (
          <button
            key={conversation.id}
            className={`conversation-item ${
              conversation.id === activeConversationId
                ? "active"
                : ""
            }`}
            onClick={() =>
              onSelectConversation(conversation.id)
            }
          >
            <MessageSquare size={15} />

            <span>
              {conversation.title ||
                "New conversation"}
            </span>
          </button>
        ))}
      </div>
    </aside>
  );
}
