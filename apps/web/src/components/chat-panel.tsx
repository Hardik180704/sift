"use client";

import { useRef, useState } from "react";

import { apiFetch } from "@/lib/api/client";
import { type AnswerPayload, createSseAccumulator, type SourcePayload } from "@/lib/api/assistant";
import { documentStateChip, type DocumentSummary } from "@/lib/api/documents";

type CitationPayload = AnswerPayload["citations"][number];

type ChatMessage = {
  role: "user" | "assistant";
  text: string;
  citations: CitationPayload[];
  sources: SourcePayload[];
  insufficient: boolean;
  failed: boolean;
};

type ChatPanelProps = {
  documents: DocumentSummary[];
  onInspectSource: (source: SourcePayload, citationIndex: number) => void;
};

function readyDocuments(documents: DocumentSummary[]): DocumentSummary[] {
  return documents.filter((document) => document.state === "READY");
}

export function ChatPanel({ documents, onInspectSource }: ChatPanelProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [question, setQuestion] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const listRef = useRef<HTMLOListElement | null>(null);

  const available = readyDocuments(documents);

  async function sendQuestion(event: React.FormEvent) {
    event.preventDefault();
    const prompt = question.trim();
    if (!prompt || isStreaming) return;
    if (available.length === 0) {
      setError("Add at least one document marked Ready before asking questions.");
      return;
    }

    setError(null);
    setQuestion("");
    setIsStreaming(true);
    setMessages((current) => [
      ...current,
      {
        role: "user",
        text: prompt,
        citations: [],
        sources: [],
        insufficient: false,
        failed: false,
      },
      {
        role: "assistant",
        text: "",
        citations: [],
        sources: [],
        insufficient: false,
        failed: false,
      },
    ]);

    function patchAssistant(
      patch: Partial<ChatMessage> | ((last: ChatMessage) => Partial<ChatMessage>),
    ) {
      setMessages((current) => {
        const next = [...current];
        const last = next[next.length - 1];
        next[next.length - 1] = { ...last, ...(typeof patch === "function" ? patch(last) : patch) };
        return next;
      });
    }

    try {
      const response = await apiFetch("/v1/assistant/stream", {
        method: "POST",
        body: JSON.stringify({ question: prompt }),
      });
      if (!response.ok || response.body === null) {
        const detail = response.ok ? "empty response" : `${response.status}`;
        throw new Error(`The assistant could not answer (${detail}).`);
      }
      const handleChunk = createSseAccumulator({
        onDelta: (text) => patchAssistant((last) => ({ text: last.text + text })),
        onAnswer: (payload) =>
          patchAssistant({
            text: payload.answer,
            citations: payload.citations,
            sources: payload.sources,
            insufficient: payload.insufficient_evidence,
          }),
      });
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      for (;;) {
        const { done, value } = await reader.read();
        if (done) break;
        handleChunk(decoder.decode(value, { stream: true }));
      }
      patchAssistant((last) => (last.text === "" ? { ...last, failed: true } : last));
    } catch (streamError) {
      patchAssistant({ failed: true });
      setError(
        streamError instanceof Error ? streamError.message : "The assistant could not answer.",
      );
    } finally {
      setIsStreaming(false);
      requestAnimationFrame(() => listRef.current?.scrollTo({ top: listRef.current.scrollHeight }));
    }
  }

  return (
    <section aria-label="Ask your documents" className="flex min-h-0 flex-1 flex-col">
      <ol className="flex min-h-0 flex-1 flex-col gap-4 overflow-y-auto p-4" ref={listRef}>
        {messages.length === 0 ? (
          <li className="m-auto max-w-md text-center">
            <p className="font-display text-2xl">
              Ask your documents a <span className="evidence-mark">question</span>
            </p>
            <p className="mt-2 text-sm text-[var(--ink-soft)]">
              Answers draw only on the documents listed as Ready, and every claim links to its page.
            </p>
          </li>
        ) : null}
        {messages.map((message, index) => (
          <li
            className={message.role === "user" ? "flex justify-end animate-enter" : "animate-enter"}
            key={index}
          >
            {message.role === "user" ? (
              <p className="max-w-[80%] rounded-xl bg-[var(--ink)] px-4 py-2.5 text-sm leading-relaxed text-[var(--paper-raised)]">
                {message.text}
              </p>
            ) : (
              <div className="max-w-[92%] rounded-xl border hairline bg-[var(--paper-raised)] px-4 py-3">
                {message.failed ? (
                  <p className="text-sm text-[var(--danger)]">
                    The assistant could not answer. Try again in a moment.
                  </p>
                ) : message.insufficient ? (
                  <p className="text-sm text-[var(--ink-soft)]">{message.text}</p>
                ) : (
                  <p className="whitespace-pre-wrap text-sm leading-relaxed">{message.text}</p>
                )}
                {message.citations.length > 0 ? (
                  <div className="mt-3 flex flex-wrap gap-1.5">
                    {message.citations.map((citation, citationIndex) => (
                      <button
                        aria-label={`Show source, page ${citation.page_number ?? "unknown"}`}
                        className="font-data rounded-md border hairline bg-[var(--paper)] px-2 py-0.5 text-xs transition-colors hover:bg-[var(--highlight)] hover:text-[var(--highlight-ink)]"
                        key={citation.chunk_id}
                        onClick={() =>
                          onInspectSource(message.sources[citationIndex], citationIndex)
                        }
                        type="button"
                      >
                        {citationIndex + 1} · p.{citation.page_number ?? "?"}
                      </button>
                    ))}
                  </div>
                ) : null}
              </div>
            )}
          </li>
        ))}
      </ol>
      {error ? (
        <p
          className="mx-4 mb-2 rounded-md border border-[var(--danger)] px-3 py-2 text-sm text-[var(--danger)]"
          role="alert"
        >
          {error}
        </p>
      ) : null}
      <form className="border-t hairline p-3" onSubmit={sendQuestion}>
        <div className="flex gap-2">
          <label className="sr-only" htmlFor="question">
            Question about your documents
          </label>
          <textarea
            className="min-h-11 flex-1 resize-none rounded-lg border hairline bg-[var(--paper-raised)] px-3 py-2.5 text-sm"
            id="question"
            maxLength={4000}
            onChange={(event) => setQuestion(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                void sendQuestion(event);
              }
            }}
            placeholder={
              available.length === 0
                ? "Upload a document to begin"
                : "e.g. When does my lease renewal window close?"
            }
            rows={1}
            value={question}
          />
          <button
            className="rounded-lg bg-[var(--ink)] px-4 py-2 text-sm font-medium text-[var(--paper-raised)] transition-opacity disabled:opacity-40"
            disabled={isStreaming || question.trim() === ""}
            type="submit"
          >
            {isStreaming ? "Reading…" : "Ask"}
          </button>
        </div>
      </form>
    </section>
  );
}

export function documentLabel(document: DocumentSummary) {
  const chip = documentStateChip(document.state);
  return `${document.original_filename} — ${chip.label}`;
}
