import { useEffect, useRef, useState } from "react";
import {
  Send,
  LoaderCircle,
  Sparkles,
} from "lucide-react";
import Message from "./Message";
import { streamMessage } from "../lib/api";

export default function Chat({
  conversation,
  onConversationUpdated,
}) {
  const [messages, setMessages] = useState(
    conversation?.messages || [],
  );

  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");

  const bottomRef = useRef(null);

  useEffect(() => {
    setMessages(conversation?.messages || []);
    setError("");
  }, [conversation?.id]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages]);

  async function handleSubmit(event) {
    event.preventDefault();

    const content = input.trim();

    if (!content || sending || !conversation) {
      return;
    }

    setInput("");
    setError("");
    setSending(true);

    const userMessage = {
      id: `user-${Date.now()}`,
      role: "user",
      content,
      created_at: new Date().toISOString(),
    };

    const assistantId = `assistant-${Date.now()}`;

    const assistantMessage = {
      id: assistantId,
      role: "assistant",
      content: "",
      created_at: new Date().toISOString(),
    };

    setMessages((current) => [
      ...current,
      userMessage,
      assistantMessage,
    ]);

    let assistantContent = "";

    try {
      await streamMessage(
        conversation.id,
        content,
        {
          topK: 5,

          onToken(token) {
            assistantContent += token;

            setMessages((current) =>
              current.map((message) =>
                message.id === assistantId
                  ? {
                      ...message,
                      content: assistantContent,
                    }
                  : message,
              ),
            );
          },

          onSources(sources) {
            setMessages((current) =>
              current.map((message) =>
                message.id === assistantId
                  ? {
                      ...message,
                      sources,
                    }
                  : message,
              ),
            );
          },

          onDone(data) {
            setMessages((current) =>
              current.map((message) =>
                message.id === assistantId
                  ? {
                      ...message,
                      id: data.message_id,
                    }
                  : message,
              ),
            );

            onConversationUpdated?.();
          },

          onError(streamError) {
            throw streamError;
          },
        },
      );
    } catch (err) {
      setError(err.message);

      setMessages((current) =>
        current.filter(
          (message) => message.id !== assistantId,
        ),
      );
    } finally {
      setSending(false);
    }
  }

  if (!conversation) {
    return (
      <main className="chat empty-chat">
        <Sparkles size={32} />

        <h2>Start a conversation</h2>

        <p>
          Ask questions about your indexed documents.
        </p>
      </main>
    );
  }

  return (
    <main className="chat">
      <header className="chat-header">
        <div>
          <div className="chat-title">
            {conversation.title}
          </div>

          <div className="chat-subtitle">
            Grounded in your document library
          </div>
        </div>
      </header>

      <div className="messages">
        {messages.length === 0 && (
          <div className="welcome">
            <div className="welcome-icon">
              <Sparkles size={24} />
            </div>

            <h2>Ask your documents</h2>

            <p>
              Your answers are generated from the
              documents indexed in the RAG system.
            </p>
          </div>
        )}

        {messages.map((message) => (
          <Message
            key={message.id}
            message={message}
            sources={message.sources || []}
            streaming={
              sending &&
              message.id ===
                messages[messages.length - 1]?.id &&
              message.role === "assistant"
            }
          />
        ))}

        {sending &&
          messages[messages.length - 1]?.content ===
            "" && (
            <div className="thinking">
              <LoaderCircle
                size={16}
                className="spin"
              />
              Generating...
            </div>
          )}

        <div ref={bottomRef} />
      </div>

      {error && (
        <div className="chat-error">
          {error}
        </div>
      )}

      <form
        className="composer"
        onSubmit={handleSubmit}
      >
        <input
          value={input}
          onChange={(event) =>
            setInput(event.target.value)
          }
          placeholder="Ask a question about your documents..."
          disabled={sending}
        />

        <button
          type="submit"
          disabled={!input.trim() || sending}
          title="Send message"
        >
          {sending ? (
            <LoaderCircle
              size={18}
              className="spin"
            />
          ) : (
            <Send size={18} />
          )}
        </button>
      </form>
    </main>
  );
}
