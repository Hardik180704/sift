"use client";

import { useState, type FormEvent } from "react";
import { useRouter, useSearchParams } from "next/navigation";

import { createClient } from "@/lib/supabase/client";

type AuthFormProps = {
  mode: "login" | "sign-up";
};

function safeRedirectPath(value: string | null) {
  return value?.startsWith("/") && !value.startsWith("//") ? value : "/app";
}

export function AuthForm({ mode }: AuthFormProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [error, setError] = useState<string>();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const isSignUp = mode === "sign-up";

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(undefined);
    setIsSubmitting(true);

    const formData = new FormData(event.currentTarget);
    const email = String(formData.get("email") ?? "");
    const password = String(formData.get("password") ?? "");
    const supabase = createClient();
    const result = isSignUp
      ? await supabase.auth.signUp({
          email,
          password,
          options: { emailRedirectTo: `${window.location.origin}/auth/callback` },
        })
      : await supabase.auth.signInWithPassword({ email, password });

    setIsSubmitting(false);

    if (result.error) {
      setError(result.error.message);
      return;
    }

    if (isSignUp && !result.data.session) {
      setError("Check your email to confirm your account, then sign in.");
      return;
    }

    router.replace(safeRedirectPath(searchParams.get("next")));
    router.refresh();
  }

  return (
    <form className="mt-8 flex flex-col gap-5" onSubmit={onSubmit}>
      <div className="flex flex-col gap-1.5">
        <label className="text-sm text-[var(--ink-soft)]" htmlFor="email">
          Email
        </label>
        <input
          autoComplete="email"
          className="rounded-lg border hairline bg-[var(--paper)] px-3 py-2.5 text-sm"
          id="email"
          name="email"
          placeholder="you@example.com"
          required
          type="email"
        />
      </div>
      <div className="flex flex-col gap-1.5">
        <label className="text-sm text-[var(--ink-soft)]" htmlFor="password">
          Password
        </label>
        <input
          autoComplete={isSignUp ? "new-password" : "current-password"}
          className="rounded-lg border hairline bg-[var(--paper)] px-3 py-2.5 text-sm"
          id="password"
          minLength={8}
          name="password"
          placeholder="At least 8 characters"
          required
          type="password"
        />
      </div>
      {error ? (
        <p
          className="rounded-md border border-[var(--danger)] px-3 py-2 text-sm text-[var(--danger)]"
          role="alert"
        >
          {error}
        </p>
      ) : null}
      <button
        className="mt-1 rounded-lg bg-[var(--ink)] py-2.5 text-sm font-medium text-[var(--paper-raised)] transition-opacity hover:opacity-90 disabled:opacity-40"
        disabled={isSubmitting}
        type="submit"
      >
        {isSubmitting ? "Please wait" : isSignUp ? "Create account" : "Sign in"}
      </button>
    </form>
  );
}
