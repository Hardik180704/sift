import Link from "next/link";
import { Suspense } from "react";

import { AuthForm } from "@/components/auth-form";

export default function SignUpPage() {
  return (
    <main className="flex min-h-screen items-center justify-center px-4">
      <div className="workspace-shadow w-full max-w-sm rounded-2xl border hairline bg-[var(--paper-raised)] p-8">
        <p className="font-data text-xs uppercase tracking-widest text-[var(--ink-soft)]">
          Get started
        </p>
        <h1 className="font-display mt-3 text-3xl">
          Create your <span className="evidence-mark">Sift</span> account
        </h1>
        <p className="mt-2 text-sm text-[var(--ink-soft)]">
          One account holds all your documents, answers, and citations.
        </p>
        <Suspense>
          <AuthForm mode="sign-up" />
        </Suspense>
        <p className="mt-6 text-sm text-[var(--ink-soft)]">
          Already have an account?{" "}
          <Link className="underline-offset-4 hover:underline" href="/login">
            Sign in
          </Link>
        </p>
      </div>
    </main>
  );
}
