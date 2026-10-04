import { describe, expect, it } from "vitest";

import { documentStateChip, formatBytes, isSettledState, sha256Hex } from "@/lib/api/documents";

describe("documentStateChip", () => {
  it("marks settled states as done or error", () => {
    expect(documentStateChip("READY")).toEqual({ label: "Ready", tone: "done" });
    expect(documentStateChip("FAILED")).toEqual({ label: "Failed", tone: "error" });
  });

  it("marks every in-flight state as working", () => {
    for (const state of ["UPLOADED", "QUEUED", "PARSING", "EXTRACTING", "EMBEDDING"]) {
      expect(documentStateChip(state).tone).toBe("working");
    }
  });

  it("falls back to a neutral chip for unknown states", () => {
    expect(documentStateChip("MYSTERY")).toEqual({ label: "MYSTERY", tone: "neutral" });
  });
});

describe("isSettledState", () => {
  it("identifies terminal states", () => {
    expect(isSettledState("READY")).toBe(true);
    expect(isSettledState("FAILED")).toBe(true);
    expect(isSettledState("PARSING")).toBe(false);
  });
});

describe("formatBytes", () => {
  it("formats bytes, kilobytes, and megabytes", () => {
    expect(formatBytes(512)).toBe("512 B");
    expect(formatBytes(2048)).toBe("2 KB");
    expect(formatBytes(5 * 1024 * 1024)).toBe("5.0 MB");
  });
});

describe("sha256Hex", () => {
  it("hashes content to a 64-character hex digest", async () => {
    const digest = await sha256Hex(new TextEncoder().encode("lease").buffer as ArrayBuffer);

    expect(digest).toMatch(/^[a-f0-9]{64}$/);
  });
});
