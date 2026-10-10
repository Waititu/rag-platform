import {
  FileText,
  RefreshCw,
} from "lucide-react";

export default function DocumentList({
  documents,
  loading,
  onRefresh,
}) {
  return (
    <div className="documents-panel">
      <div className="panel-heading">
        <div>
          <div className="panel-title">
            Documents
          </div>

          <div className="panel-subtitle">
            {documents.length} indexed
          </div>
        </div>

        <button
          className="icon-button"
          onClick={onRefresh}
          disabled={loading}
          title="Refresh documents"
        >
          <RefreshCw
            size={15}
            className={loading ? "spin" : ""}
          />
        </button>
      </div>

      <div className="document-list">
        {loading && documents.length === 0 && (
          <div className="empty-state">
            Loading documents...
          </div>
        )}

        {!loading && documents.length === 0 && (
          <div className="empty-state">
            <FileText size={24} />
            <span>No documents yet.</span>
          </div>
        )}

        {documents.map((document) => (
          <div
            className="document-item"
            key={document.id}
          >
            <div className="document-icon">
              <FileText size={15} />
            </div>

            <div className="document-info">
              <div className="document-name">
                {document.filename}
              </div>

              <div className="document-meta">
                {document.size_bytes
                  ? `${document.size_bytes} bytes`
                  : document.content_type}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
