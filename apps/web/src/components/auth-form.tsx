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
    <form onSubmit={onSubmit}>
      <label htmlFor="email">Email</label>
      <input autoComplete="email" id="email" name="email" required type="email" />
      <label htmlFor="password">Password</label>
      <input
        autoComplete={isSignUp ? "new-password" : "current-password"}
        id="password"
        minLength={8}
        name="password"
        required
        type="password"
      />
      {error ? <p role="alert">{error}</p> : null}
      <button disabled={isSubmitting} type="submit">
        {isSubmitting ? "Please wait" : isSignUp ? "Create account" : "Sign in"}
      </button>
    </form>
  );
}
