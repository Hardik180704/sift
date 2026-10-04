export const DOCUMENT_STATES = [
  "UPLOADED",
  "QUEUED",
  "PARSING",
  "EXTRACTING",
  "EMBEDDING",
  "READY",
  "FAILED",
] as const;

export type DocumentState = (typeof DOCUMENT_STATES)[number];

export type StateChip = { label: string; tone: "neutral" | "working" | "done" | "error" };

export type DocumentSummary = {
  id: string;
  original_filename: string;
  mime_type: string;
  size_bytes: number;
  state: DocumentState | string;
  created_at: string;
  updated_at: string;
};

export function documentStateChip(state: string): StateChip {
  switch (state) {
    case "READY":
      return { label: "Ready", tone: "done" };
    case "FAILED":
      return { label: "Failed", tone: "error" };
    case "QUEUED":
      return { label: "Queued", tone: "working" };
    case "PARSING":
      return { label: "Reading", tone: "working" };
    case "EXTRACTING":
      return { label: "Extracting", tone: "working" };
    case "EMBEDDING":
      return { label: "Indexing", tone: "working" };
    case "UPLOADED":
      return { label: "Finishing upload", tone: "working" };
    default:
      return { label: state, tone: "neutral" };
  }
}

export function isSettledState(state: string): boolean {
  return state === "READY" || state === "FAILED";
}

export function formatBytes(sizeBytes: number): string {
  if (sizeBytes < 1024) return `${sizeBytes} B`;
  if (sizeBytes < 1024 * 1024) return `${(sizeBytes / 1024).toFixed(0)} KB`;
  return `${(sizeBytes / (1024 * 1024)).toFixed(1)} MB`;
}

export async function sha256Hex(content: ArrayBuffer): Promise<string> {
  const digest = await crypto.subtle.digest("SHA-256", new Uint8Array(content));
  return Array.from(new Uint8Array(digest))
    .map((byte) => byte.toString(16).padStart(2, "0"))
    .join("");
}
