"use client";

import { useRef } from "react";

import { documentStateChip, formatBytes, type DocumentSummary } from "@/lib/api/documents";

const UPLOADABLE_MIME_TYPES = ["application/pdf", "text/plain"];

type DocumentLibraryProps = {
  documents: DocumentSummary[];
  onUpload: (file: File) => Promise<void>;
  uploading: boolean;
  uploadError: string | null;
};

const chipToneClass: Record<DocumentSummaryStateChipTone, string> = {
  neutral: "border hairline text-[var(--ink-soft)]",
  working:
    "border border-[color:var(--line)] bg-[var(--paper)] text-[var(--ink-soft)] animate-pulse",
  done: "bg-[var(--highlight)] text-[var(--highlight-ink)] border border-transparent",
  error: "border border-[var(--danger)] text-[var(--danger)]",
};

type DocumentSummaryStateChipTone = "neutral" | "working" | "done" | "error";

export function DocumentLibrary({
  documents,
  onUpload,
  uploading,
  uploadError,
}: DocumentLibraryProps) {
  const inputRef = useRef<HTMLInputElement | null>(null);

  function selectFile(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (file) void onUpload(file);
  }

  return (
    <section aria-label="Your documents" className="flex min-h-0 flex-col">
      <div className="flex items-center justify-between gap-3 px-4 pb-3">
        <h1 className="font-display text-xl">Library</h1>
        <button
          className="font-data rounded-md border hairline px-3 py-1.5 text-sm transition-colors hover:bg-black/5 disabled:opacity-50 dark:hover:bg-white/10"
          disabled={uploading}
          onClick={() => inputRef.current?.click()}
          type="button"
        >
          {uploading ? "Uploading…" : "+ Upload"}
        </button>
        <input
          accept={UPLOADABLE_MIME_TYPES.concat(
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
          ).join(",")}
          className="sr-only"
          disabled={uploading}
          onChange={selectFile}
          ref={inputRef}
          type="file"
        />
      </div>
      {uploadError ? (
        <p
          className="mx-4 mb-3 rounded-md border border-[var(--danger)] px-3 py-2 text-sm text-[var(--danger)]"
          role="alert"
        >
          {uploadError}
        </p>
      ) : null}
      {documents.length === 0 ? (
        <p className="px-4 pb-4 text-sm text-[var(--ink-soft)]">
          No documents yet. Upload a lease, policy, or warranty and Sift will read each page.
        </p>
      ) : (
        <ul className="flex flex-col gap-2 px-4 pb-4">
          {documents.map((document) => {
            const chip = documentStateChip(document.state);
            return (
              <li
                className="rounded-lg border hairline bg-[var(--paper-raised)] px-3 py-2.5"
                key={document.id}
              >
                <p className="truncate text-sm font-medium">{document.original_filename}</p>
                <p className="font-data mt-1 flex items-center gap-2 text-xs text-[var(--ink-soft)]">
                  <span
                    className={`rounded-full px-2 py-0.5 ${chipToneClass[chip.tone]}`}
                    data-state={document.state}
                  >
                    {chip.label}
                  </span>
                  <span>{formatBytes(document.size_bytes)}</span>
                </p>
              </li>
            );
          })}
        </ul>
      )}
      <p className="font-data mt-auto border-t hairline px-4 py-3 text-xs text-[var(--ink-soft)]">
        PDF · DOCX · TXT — up to 50 MB
      </p>
    </section>
  );
}
