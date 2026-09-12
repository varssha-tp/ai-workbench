import { useRef, useState } from "react";
import { uploadFiles } from "../api";
import type { FileMeta } from "../types";

const TYPE_LABEL: Record<string, string> = { pdf: "PDF", csv: "CSV", excel: "Excel" };

interface DropzoneProps {
  files: FileMeta[];
  onFilesAdded: (files: FileMeta[]) => void;
}

export function Dropzone({ files, onFilesAdded }: DropzoneProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  async function handleFiles(fileList: FileList | null) {
    if (!fileList || fileList.length === 0) return;
    setError(null);
    setIsUploading(true);
    try {
      const uploaded = await uploadFiles(Array.from(fileList));
      onFilesAdded(uploaded);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Upload failed");
    } finally {
      setIsUploading(false);
      if (inputRef.current) inputRef.current.value = "";
    }
  }

  return (
    <div>
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setIsDragging(false);
          handleFiles(e.dataTransfer.files);
        }}
        onClick={() => inputRef.current?.click()}
        className={`cursor-pointer rounded-xl border-2 border-dashed p-8 text-center transition-colors ${
          isDragging
            ? "border-purple-400 bg-purple-900/30"
            : "border-line bg-surface-2/40 hover:border-purple-500 hover:bg-purple-900/10"
        }`}
      >
        <input
          ref={inputRef}
          type="file"
          multiple
          accept=".pdf,.csv,.xlsx,.xls"
          className="hidden"
          onChange={(e) => handleFiles(e.target.files)}
        />
        <p className="text-sm font-medium text-ink">
          {isUploading ? "Uploading…" : "Drop your files here"}
        </p>
        <p className="mt-1 text-xs text-ink-muted">PDF · CSV · Excel</p>
      </div>

      {error && <p className="mt-2 text-sm text-red-400">{error}</p>}

      {files.length > 0 && (
        <ul className="mt-3 flex flex-wrap gap-2">
          {files.map((f) => (
            <li
              key={f.file_id}
              className="flex items-center gap-1.5 rounded-full bg-purple-900/40 px-3 py-1 text-xs text-purple-200"
            >
              <span className="font-medium">{f.filename}</span>
              <span className="text-purple-400">{TYPE_LABEL[f.file_type] ?? f.file_type}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
