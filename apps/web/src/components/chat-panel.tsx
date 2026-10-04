"use client";

import { useEffect, useRef, useState } from "react";

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

const STARTER_QUESTIONS = [
  "What should I pay attention to?",
  "What dates or deadlines matter?",
  "Summarize the important terms.",
];

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

  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight, behavior: "smooth" });
  }, [messages]);

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

    let bufferedText = "";
    let receivedDelta = false;
    const completedAnswer = { payload: null as AnswerPayload | null };
    let revealFrame: number | null = null;
    let lastRevealAt = 0;
    let streamClosed = false;
    let resolveReveal: () => void = () => undefined;
    const revealComplete = new Promise<void>((resolve) => {
      resolveReveal = resolve;
    });

    function finishReveal() {
      if (revealFrame !== null || !streamClosed || bufferedText) return;
      resolveReveal();
    }

    function revealNext(timestamp: number) {
      revealFrame = null;
      const elapsed = lastRevealAt === 0 ? 16 : timestamp - lastRevealAt;
      lastRevealAt = timestamp;
      const characterCount = Math.min(bufferedText.length, Math.max(1, Math.floor(elapsed * 0.09)));
      const nextText = bufferedText.slice(0, characterCount);
      bufferedText = bufferedText.slice(characterCount);
      if (nextText) {
        patchAssistant((last) => ({ text: last.text + nextText }));
      }
      if (bufferedText) {
        revealFrame = requestAnimationFrame(revealNext);
        return;
      }
      finishReveal();
    }

    function startReveal() {
      if (revealFrame === null && bufferedText) {
        revealFrame = requestAnimationFrame(revealNext);
      }
    }

    try {
      const streamResponse = await apiFetch("/v1/assistant/stream", {
        method: "POST",
        body: JSON.stringify({ question: prompt }),
      });
      if (!streamResponse.ok || streamResponse.body === null) {
        const detail = streamResponse.ok ? "empty response" : `${streamResponse.status}`;
        throw new Error(`The assistant could not answer (${detail}).`);
      }
      const handleChunk = createSseAccumulator({
        onDelta: (text) => {
          receivedDelta = true;
          bufferedText += text;
          startReveal();
        },
        onAnswer: (payload) => {
          completedAnswer.payload = payload;
          if (!receivedDelta) {
            bufferedText += payload.answer;
            startReveal();
          }
        },
      });
      const reader = streamResponse.body.getReader();
      const decoder = new TextDecoder();
      for (;;) {
        const { done, value } = await reader.read();
        if (done) break;
        handleChunk(decoder.decode(value, { stream: true }));
      }
      streamClosed = true;
      finishReveal();
      await revealComplete;
      const completedPayload = completedAnswer.payload;
      if (completedPayload === null) {
        patchAssistant((last) => (last.text === "" ? { ...last, failed: true } : last));
      } else {
        patchAssistant({
          citations: completedPayload.citations,
          sources: completedPayload.sources,
          insufficient: completedPayload.insufficient_evidence,
        });
      }
    } catch (streamError) {
      if (revealFrame !== null) cancelAnimationFrame(revealFrame);
      patchAssistant({ failed: true });
      setError(
        streamError instanceof Error ? streamError.message : "The assistant could not answer.",
      );
    } finally {
      setIsStreaming(false);
    }
  }

  return (
    <section aria-label="Ask your documents" className="flex min-h-0 flex-1 flex-col">
      <ol
        className="flex min-h-0 flex-1 flex-col gap-6 overflow-y-auto px-4 py-6 sm:px-7"
        ref={listRef}
      >
        {messages.length === 0 ? (
          <li className="m-auto w-full max-w-xl text-center animate-enter">
            <p className="font-display text-3xl tracking-tight sm:text-4xl">
              What would you like to know?
            </p>
            <p className="mx-auto mt-3 max-w-md text-sm leading-relaxed text-[var(--ink-soft)]">
              Ask naturally. Sift answers from your ready documents and shows the pages behind each
              answer.
            </p>
            {available.length > 0 ? (
              <div className="mx-auto mt-7 grid max-w-lg gap-2 text-left sm:grid-cols-3">
                {STARTER_QUESTIONS.map((starter) => (
                  <button
                    className="rounded-xl border hairline bg-[var(--paper-raised)] px-3 py-3 text-left text-sm leading-snug transition hover:-translate-y-0.5 hover:border-[var(--ink-soft)] hover:shadow-sm"
                    key={starter}
                    onClick={() => setQuestion(starter)}
                    type="button"
                  >
                    {starter}
                  </button>
                ))}
              </div>
            ) : null}
          </li>
        ) : null}
        {messages.map((message, index) => (
          <li
            className={message.role === "user" ? "flex justify-end animate-enter" : "animate-enter"}
            key={index}
          >
            {message.role === "user" ? (
              <p className="max-w-[85%] rounded-2xl rounded-br-md bg-[var(--ink)] px-4 py-2.5 text-sm leading-relaxed text-[var(--paper-raised)] shadow-sm sm:max-w-[70%]">
                {message.text}
              </p>
            ) : (
              <div className="flex max-w-2xl gap-3 sm:gap-4">
                <span
                  aria-hidden="true"
                  className="font-display flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-[var(--highlight)] text-sm text-[var(--highlight-ink)] shadow-sm"
                >
                  S
                </span>
                <div className="min-w-0 pt-0.5">
                  <p className="font-data mb-1.5 text-[11px] font-medium uppercase tracking-[0.14em] text-[var(--ink-soft)]">
                    Sift
                  </p>
                  {message.failed ? (
                    <p className="text-sm text-[var(--danger)]">
                      The assistant could not answer. Try again in a moment.
                    </p>
                  ) : message.insufficient ? (
                    <p className="text-sm leading-relaxed text-[var(--ink-soft)]">{message.text}</p>
                  ) : message.text ? (
                    <p className="whitespace-pre-wrap text-[15px] leading-7">
                      {message.text}
                      {isStreaming && index === messages.length - 1 ? (
                        <span aria-hidden="true" className="chat-caret" />
                      ) : null}
                    </p>
                  ) : (
                    <span aria-label="Sift is thinking" className="chat-thinking" role="status">
                      <i />
                      <i />
                      <i />
                    </span>
                  )}
                  {message.citations.length > 0 ? (
                    <div className="mt-4 border-t hairline pt-3">
                      <p className="font-data mb-2 text-[10px] font-medium uppercase tracking-[0.14em] text-[var(--ink-soft)]">
                        Sources
                      </p>
                      <div className="flex flex-wrap gap-1.5">
                        {message.citations.map((citation, citationIndex) => {
                          const source =
                            message.sources.find((item) => item.chunk_id === citation.chunk_id) ??
                            message.sources[citationIndex];
                          return (
                            <button
                              aria-label={`Open source ${citationIndex + 1}, page ${citation.page_number ?? "unknown"}`}
                              className="rounded-lg border hairline bg-[var(--paper-raised)] px-2.5 py-1 text-xs text-[var(--ink-soft)] transition hover:border-[var(--ink-soft)] hover:bg-[var(--paper)] hover:text-[var(--ink)] disabled:cursor-not-allowed disabled:opacity-50"
                              disabled={source === undefined}
                              key={citation.chunk_id}
                              onClick={() => source && onInspectSource(source, citationIndex)}
                              type="button"
                            >
                              Source {citationIndex + 1} <span aria-hidden="true">·</span> page{" "}
                              {citation.page_number ?? "?"}
                            </button>
                          );
                        })}
                      </div>
                    </div>
                  ) : null}
                </div>
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
      <form
        className="border-t hairline bg-[color:var(--paper)]/70 px-4 py-3 backdrop-blur sm:px-7 sm:py-4"
        onSubmit={sendQuestion}
      >
        <div className="mx-auto flex max-w-2xl items-end gap-2 rounded-2xl border hairline bg-[var(--paper-raised)] p-2 shadow-sm transition focus-within:border-[var(--ink-soft)] focus-within:shadow-md">
          <label className="sr-only" htmlFor="question">
            Question about your documents
          </label>
          <textarea
            className="min-h-11 max-h-36 flex-1 resize-none bg-transparent px-2 py-2 text-sm leading-relaxed outline-none placeholder:text-[var(--ink-soft)]"
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
                : "Ask anything about your documents..."
            }
            rows={1}
            value={question}
          />
          <button
            aria-label="Send question"
            className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-[var(--ink)] text-[var(--paper-raised)] transition hover:opacity-85 disabled:opacity-35"
            disabled={isStreaming || question.trim() === ""}
            type="submit"
          >
            <span aria-hidden="true" className="text-lg leading-none">
              {isStreaming ? "…" : "↑"}
            </span>
          </button>
        </div>
        <p className="mx-auto mt-2 max-w-2xl px-2 text-center text-[11px] text-[var(--ink-soft)]">
          Sift answers from your documents. Press Enter to send, Shift + Enter for a new line.
        </p>
      </form>
    </section>
  );
}

export function documentLabel(document: DocumentSummary) {
  const chip = documentStateChip(document.state);
  return `${document.original_filename} — ${chip.label}`;
}
