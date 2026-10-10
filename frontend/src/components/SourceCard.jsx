import {
  FileText,
  ChevronRight,
} from "lucide-react";

export default function SourceCard({ source }) {
  return (
    <div className="source-card">
      <div className="source-icon">
        <FileText size={15} />
      </div>

      <div className="source-content">
        <div className="source-name">
          {source.filename}
        </div>

        <div className="source-meta">
          Chunk {source.chunk_index}

          {typeof source.similarity === "number" && (
            <>
              <span>·</span>
              {(source.similarity * 100).toFixed(0)}% match
            </>
          )}
        </div>
      </div>

      <ChevronRight
        size={15}
        className="source-arrow"
      />
    </div>
  );
}
