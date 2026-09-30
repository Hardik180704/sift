import { describe, expect, it } from "vitest";

import { GET } from "./route";

describe("GET /api/health", () => {
  it("returns the web service health payload", async () => {
    const response = GET();

    await expect(response.json()).resolves.toEqual({ status: "ok", service: "web" });
  });
});
