"use client";

import { useCallback, useEffect, useState } from "react";

import { type SourcePayload } from "@/lib/api/assistant";
import { apiFetch } from "@/lib/api/client";
import { isSettledState, sha256Hex, type DocumentSummary } from "@/lib/api/documents";
import { ChatPanel } from "@/components/chat-panel";
import { DocumentLibrary } from "@/components/document-library";
import { SignOutButton } from "@/components/sign-out-button";
import { SourcePanel } from "@/components/source-panel";
import { ThemeToggle } from "@/components/theme-toggle";

type SourcePanelState = { source: SourcePayload; citationIndex: number } | null;

type WorkspaceProps = {
  userEmail: string | null;
};

const POLL_INTERVAL_MS = 3000;

export function Workspace({ userEmail }: WorkspaceProps) {
  const [documents, setDocuments] = useState<DocumentSummary[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [panelState, setPanelState] = useState<SourcePanelState>(null);

  const refreshDocuments = useCallback(async () => {
    const response = await apiFetch("/v1/documents");
    if (!response.ok) return;
    const payload = (await response.json()) as { documents: DocumentSummary[] };
    setDocuments(payload.documents);
  }, []);

  useEffect(() => {
    void refreshDocuments();
  }, [refreshDocuments]);

  useEffect(() => {
    if (documents.every((document) => isSettledState(document.state))) return;
    const poll = setInterval(() => void refreshDocuments(), POLL_INTERVAL_MS);
    return () => clearInterval(poll);
  }, [documents, refreshDocuments]);

  async function uploadDocument(file: File) {
    setUploadError(null);
    setUploading(true);
    try {
      if (file.size <= 0 || file.size > 52_428_800) {
        throw new Error("Choose a file between 1 byte and 50 MB.");
      }
      const checksum = await sha256Hex(await file.arrayBuffer());
      const initiate = await apiFetch("/v1/documents/uploads", {
        method: "POST",
        body: JSON.stringify({
          filename: file.name,
          mime_type: file.type,
          size_bytes: file.size,
          checksum_sha256: checksum,
        }),
      });
      if (!initiate.ok) {
        throw new Error(
          initiate.status === 422
            ? "That file type or size is not accepted. Use PDF, DOCX, or TXT up to 50 MB."
            : `Upload could not start (${initiate.status}).`,
        );
      }
      const target = (await initiate.json()) as {
        document_id: string;
        signed_upload_url: string;
        signed_upload_token: string;
      };
      const objectUrl = new URL(target.signed_upload_url);
      objectUrl.searchParams.set("token", target.signed_upload_token);
      const upload = await fetch(objectUrl, {
        method: "POST",
        headers: {
          "content-type": file.type || "application/octet-stream",
          "cache-control": "3600",
        },
        body: file,
      });
      if (!upload.ok) {
        throw new Error(`The file upload failed (${upload.status}).`);
      }
      const confirm = await apiFetch(`/v1/documents/${target.document_id}/upload-complete`, {
        method: "POST",
      });
      if (!confirm.ok) {
        throw new Error(`The upload could not be confirmed (${confirm.status}).`);
      }
      await refreshDocuments();
    } catch (uploadFailure) {
      setUploadError(uploadFailure instanceof Error ? uploadFailure.message : "The upload failed.");
    } finally {
      setUploading(false);
    }
  }

  function inspectSource(source: SourcePayload, citationIndex: number) {
    setPanelState({ source, citationIndex });
  }

  return (
    <div className="mx-auto flex h-screen max-w-6xl flex-col lg:py-6">
      <header className="flex items-center justify-between gap-4 border-b hairline px-4 py-3 lg:rounded-t-xl lg:border-b lg:bg-[var(--paper-raised)] lg:px-5">
        <div className="flex items-baseline gap-3">
          <p className="font-display text-xl">
            Sift<span className="text-[var(--ink-soft)]">.</span>
          </p>
          <p className="font-data hidden text-xs text-[var(--ink-soft)] sm:block">
            {userEmail ?? "signed in"}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <ThemeToggle />
          <SignOutButton />
        </div>
      </header>
      <div className="grid min-h-0 flex-1 grid-rows-[auto_1fr] lg:grid-cols-[272px_1fr] lg:grid-rows-1">
        <aside className="order-1 border-b hairline pt-3 lg:order-none lg:row-span-1 lg:rounded-bl-xl lg:border-b-0 lg:border-r lg:pt-4">
          <DocumentLibrary
            documents={documents}
            onUpload={uploadDocument}
            uploadError={uploadError}
            uploading={uploading}
          />
        </aside>
        <main className="order-2 flex min-h-0 flex-col lg:order-none" id="main">
          <ChatPanel documents={documents} onInspectSource={inspectSource} />
        </main>
      </div>
      <SourcePanel
        onClose={() => setPanelState(null)}
        open={panelState !== null}
        title={
          panelState
            ? `Source ${panelState.citationIndex + 1} · page ${panelState.source.page_number ?? "?"}`
            : "Source evidence"
        }
      >
        {panelState ? (
          <figure className="flex flex-col gap-3">
            <blockquote className="rounded-lg border-l-4 border-[var(--highlight)] bg-[var(--paper)] px-4 py-3 text-sm leading-relaxed">
              <span className="evidence-mark">{panelState.source.content}</span>
            </blockquote>
            <figcaption className="font-data flex flex-col gap-1 text-xs text-[var(--ink-soft)]">
              <span>document {panelState.source.document_id.slice(0, 8)}…</span>
              <span>chunk {panelState.source.chunk_id.slice(0, 8)}…</span>
              <span>relevance {panelState.source.score.toFixed(3)}</span>
            </figcaption>
          </figure>
        ) : null}
      </SourcePanel>
    </div>
  );
}
