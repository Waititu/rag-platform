import { useRef, useState } from "react";
import {
  Upload,
  X,
} from "lucide-react";
import { uploadDocument } from "../lib/api";

export default function DocumentUpload({
  onUploaded,
}) {
  const inputRef = useRef(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");

  async function handleFile(file) {
    if (!file) {
      return;
    }

    setError("");
    setUploading(true);

    try {
      await uploadDocument(file);
      onUploaded?.();
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  }

  function handleChange(event) {
    handleFile(event.target.files?.[0]);
    event.target.value = "";
  }

  return (
    <div className="upload-section">
      <input
        ref={inputRef}
        type="file"
        accept=".txt,.md,.markdown,.pdf"
        hidden
        onChange={handleChange}
      />

      <button
        className="upload-button"
        onClick={() => inputRef.current?.click()}
        disabled={uploading}
      >
        <Upload size={16} />

        {uploading
          ? "Uploading..."
          : "Upload document"}
      </button>

      {error && (
        <div className="inline-error">
          <X size={14} />
          {error}
        </div>
      )}
    </div>
  );
}
