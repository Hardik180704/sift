import type { SupabaseClient } from "@supabase/supabase-js";

import { API_BASE_URL } from "@/lib/api/config";
import { createClient } from "@/lib/supabase/client";

export async function getAccessToken(): Promise<string> {
  const supabase: SupabaseClient = createClient();
  const {
    data: { session },
  } = await supabase.auth.getSession();
  if (!session?.access_token) {
    throw new Error("You are signed out. Sign in and try again.");
  }
  return session.access_token;
}

export async function apiFetch(path: string, init: RequestInit = {}): Promise<Response> {
  const token = await getAccessToken();
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
      ...init.headers,
    },
  });
  return response;
}
