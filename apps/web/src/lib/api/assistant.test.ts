import { describe, expect, it } from "vitest";

import type { AnswerPayload, SseHandlers } from "@/lib/api/assistant";
import { createSseAccumulator } from "@/lib/api/assistant";

function freshHandlers(): { deltas: string[]; answers: AnswerPayload[] } & SseHandlers {
  const record = { deltas: [] as string[], answers: [] as AnswerPayload[] };
  return {
    ...record,
    onDelta(text: string) {
      record.deltas.push(text);
    },
    onAnswer(payload: AnswerPayload) {
      record.answers.push(payload);
    },
  };
}

describe("createSseAccumulator", () => {
  it("dispatches complete delta events", () => {
    const handlers = freshHandlers();
    const handle = createSseAccumulator(handlers);

    handle('event: delta\ndata: {"text":"Hello "}\n\n');

    expect(handlers.deltas).toEqual(["Hello "]);
  });

  it("buffers events split across chunks", () => {
    const handlers = freshHandlers();
    const handle = createSseAccumulator(handlers);

    handle('event: delta\ndata: {"text":');
    handle('"world"}\n\nevent: delta\ndata: {"text":"!"}\n\n');

    expect(handlers.deltas).toEqual(["world", "!"]);
  });

  it("dispatches the final answer payload", () => {
    const handlers = freshHandlers();
    const handle = createSseAccumulator(handlers);
    const payload: AnswerPayload = {
      conversation_id: "3f1a2b3c-0000-4000-8000-000000000000",
      answer: "done",
      citations: [],
      insufficient_evidence: false,
      sources: [],
    };

    handle(`event: answer\ndata: ${JSON.stringify(payload)}\n\n`);

    expect(handlers.answers).toEqual([payload]);
  });

  it("keeps a trailing partial event in the buffer", () => {
    const handlers = freshHandlers();
    const handle = createSseAccumulator(handlers);

    handle('event: delta\ndata: {"text":"par');

    expect(handlers.deltas).toEqual([]);
  });
});
