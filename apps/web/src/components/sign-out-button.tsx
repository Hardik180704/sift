"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { createClient } from "@/lib/supabase/client";

export function SignOutButton() {
  const router = useRouter();
  const [isSigningOut, setIsSigningOut] = useState(false);

  async function signOut() {
    setIsSigningOut(true);
    const supabase = createClient();
    await supabase.auth.signOut();
    router.replace("/");
    router.refresh();
  }

  return (
    <button
      className="rounded-md border hairline px-2.5 py-1.5 text-sm text-[var(--ink-soft)] transition-colors hover:text-[var(--ink)] disabled:opacity-50"
      disabled={isSigningOut}
      onClick={signOut}
      type="button"
    >
      {isSigningOut ? "Signing out…" : "Sign out"}
    </button>
  );
}
