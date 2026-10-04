export type CitationPayload = {
  chunk_id: string;
  document_id: string;
  page_number: number | null;
  quote: string;
};

export type SourcePayload = {
  chunk_id: string;
  document_id: string;
  page_number: number | null;
  section: string | null;
  content: string;
  score: number;
};

export type AnswerPayload = {
  conversation_id: string;
  answer: string;
  citations: CitationPayload[];
  insufficient_evidence: boolean;
  sources: SourcePayload[];
};

export type SseHandlers = {
  onDelta: (text: string) => void;
  onAnswer: (payload: AnswerPayload) => void;
};

function dispatchEvent(rawEvent: string, handlers: SseHandlers): void {
  let eventName = "message";
  let data = "";
  for (const line of rawEvent.split("\n")) {
    if (line.startsWith("event:")) {
      eventName = line.slice(6).trim();
    } else if (line.startsWith("data:")) {
      data += line.slice(5);
    }
  }
  if (!data) return;
  if (eventName === "delta") {
    handlers.onDelta((JSON.parse(data) as { text: string }).text);
  } else if (eventName === "answer") {
    handlers.onAnswer(JSON.parse(data) as AnswerPayload);
  }
}

export function createSseAccumulator(handlers: SseHandlers): (chunk: string) => void {
  let buffer = "";
  return (chunk: string) => {
    buffer += chunk;
    let boundary = buffer.indexOf("\n\n");
    while (boundary !== -1) {
      const rawEvent = buffer.slice(0, boundary);
      buffer = buffer.slice(boundary + 2);
      dispatchEvent(rawEvent, handlers);
      boundary = buffer.indexOf("\n\n");
    }
  };
}
