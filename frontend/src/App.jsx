import { useEffect, useState } from "react";
import {
  AlertCircle,
  Database,
} from "lucide-react";

import Sidebar from "./components/Sidebar";
import DocumentUpload from "./components/DocumentUpload";
import DocumentList from "./components/DocumentList";
import Chat from "./components/Chat";

import {
  createConversation,
  getConversation,
  listConversations,
  listDocuments,
} from "./lib/api";

export default function App() {
  const [documents, setDocuments] = useState([]);
  const [documentsLoading, setDocumentsLoading] =
    useState(true);

  const [conversations, setConversations] =
    useState([]);

  const [conversation, setConversation] =
    useState(null);

  const [appError, setAppError] = useState("");

  async function loadDocuments() {
    setDocumentsLoading(true);

    try {
      const data = await listDocuments();

      setDocuments(
        Array.isArray(data)
          ? data
          : data.documents || [],
      );
    } catch (error) {
      setAppError(error.message);
    } finally {
      setDocumentsLoading(false);
    }
  }

  async function loadConversations() {
    try {
      const data = await listConversations();

      setConversations(
        Array.isArray(data)
          ? data
          : data.conversations || [],
      );
    } catch (error) {
      setAppError(error.message);
    }
  }

  async function selectConversation(id) {
    try {
      const data = await getConversation(id);
      setConversation(data);
    } catch (error) {
      setAppError(error.message);
    }
  }

  async function handleNewConversation() {
    try {
      const data = await createConversation(
        "New conversation",
      );

      setConversations((current) => [
        data,
        ...current,
      ]);

      setConversation({
        ...data,
        messages: [],
      });
    } catch (error) {
      setAppError(error.message);
    }
  }

  async function refreshConversation() {
    if (!conversation?.id) {
      return;
    }

    try {
      const data = await getConversation(
        conversation.id,
      );

      setConversation(data);
    } catch (error) {
      setAppError(error.message);
    }

    await loadConversations();
  }

  useEffect(() => {
    async function initialize() {
      await Promise.all([
        loadDocuments(),
        loadConversations(),
      ]);
    }

    initialize();
  }, []);

  useEffect(() => {
    if (
      !conversation &&
      conversations.length > 0
    ) {
      selectConversation(
        conversations[0].id,
      );
    }
  }, [conversations, conversation]);

  return (
    <div className="app">
      <Sidebar
        conversations={conversations}
        activeConversationId={conversation?.id}
        onNewConversation={handleNewConversation}
        onSelectConversation={selectConversation}
      />

      <section className="workspace">
        <div className="library-bar">
          <div className="library-title">
            <Database size={17} />
            <span>Knowledge library</span>
          </div>

          <DocumentUpload
            onUploaded={loadDocuments}
          />
        </div>

        <div className="workspace-body">
          <div className="document-column">
            <DocumentList
              documents={documents}
              loading={documentsLoading}
              onRefresh={loadDocuments}
            />
          </div>

          <Chat
            conversation={conversation}
            onConversationUpdated={
              refreshConversation
            }
          />
        </div>
      </section>

      {appError && (
        <div className="global-error">
          <AlertCircle size={16} />
          {appError}
        </div>
      )}
    </div>
  );
}
