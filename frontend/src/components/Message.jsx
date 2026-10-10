import { Bot, User } from "lucide-react";
import SourceCard from "./SourceCard";

export default function Message({
  message,
  sources = [],
  streaming = false,
}) {
  const isUser = message.role === "user";

  return (
    <div
      className={`message-row ${
        isUser ? "message-user" : "message-assistant"
      }`}
    >
      <div className="message-avatar">
        {isUser ? (
          <User size={16} />
        ) : (
          <Bot size={16} />
        )}
      </div>

      <div className="message-body">
        <div className="message-role">
          {isUser ? "You" : "Assistant"}
        </div>

        <div className="message-content">
          {message.content}

          {streaming && (
            <span className="streaming-cursor" />
          )}
        </div>

        {!isUser && sources.length > 0 && (
          <div className="sources">
            <div className="sources-title">
              Sources
            </div>

            {sources.map((source) => (
              <SourceCard
                key={source.chunk_id}
                source={source}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
