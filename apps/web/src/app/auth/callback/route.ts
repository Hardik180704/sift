import { type NextRequest, NextResponse } from "next/server";

import { createClient } from "@/lib/supabase/server";

function safeRedirectPath(value: string | null) {
  return value?.startsWith("/") && !value.startsWith("//") ? value : "/app";
}

export async function GET(request: NextRequest) {
  const requestUrl = new URL(request.url);
  const code = requestUrl.searchParams.get("code");
  const next = safeRedirectPath(requestUrl.searchParams.get("next"));

  if (code) {
    const supabase = await createClient();
    const { error } = await supabase.auth.exchangeCodeForSession(code);

    if (!error) {
      return NextResponse.redirect(new URL(next, requestUrl.origin));
    }
  }

  return NextResponse.redirect(new URL("/login?error=authentication_failed", requestUrl.origin));
}
