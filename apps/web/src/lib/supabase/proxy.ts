import { createServerClient } from "@supabase/ssr";
import { type NextRequest, NextResponse } from "next/server";

import { getSupabasePublicConfig } from "./config";

export async function updateSession(request: NextRequest) {
  let response = NextResponse.next({ request });
  const { publishableKey, url } = getSupabasePublicConfig();
  const supabase = createServerClient(url, publishableKey, {
    cookies: {
      getAll() {
        return request.cookies.getAll();
      },
      setAll(cookiesToSet) {
        cookiesToSet.forEach(({ name, value }) => request.cookies.set(name, value));
        response = NextResponse.next({ request });
        cookiesToSet.forEach(({ name, options, value }) =>
          response.cookies.set(name, value, options),
        );
      },
    },
  });

  const {
    data: { user },
  } = await supabase.auth.getUser();
  const pathname = request.nextUrl.pathname;
  const isAuthPage = pathname === "/login" || pathname === "/sign-up";

  if (!user && !isAuthPage) {
    const redirectUrl = request.nextUrl.clone();
    redirectUrl.pathname = "/login";
    redirectUrl.searchParams.set("next", pathname);
    return NextResponse.redirect(redirectUrl);
  }

  if (user && isAuthPage) {
    const redirectUrl = request.nextUrl.clone();
    redirectUrl.pathname = "/app";
    redirectUrl.search = "";
    return NextResponse.redirect(redirectUrl);
  }

  return response;
}
