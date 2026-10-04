import Link from "next/link";
import { Suspense } from "react";

import { AuthForm } from "@/components/auth-form";

export default function LoginPage() {
  return (
    <main className="flex min-h-screen items-center justify-center px-4">
      <div className="workspace-shadow w-full max-w-sm rounded-2xl border hairline bg-[var(--paper-raised)] p-8">
        <p className="font-data text-xs uppercase tracking-widest text-[var(--ink-soft)]">
          Welcome back
        </p>
        <h1 className="font-display mt-3 text-3xl">
          Sign in to <span className="evidence-mark">Sift</span>
        </h1>
        <Suspense>
          <AuthForm mode="login" />
        </Suspense>
        <p className="mt-6 text-sm text-[var(--ink-soft)]">
          New to Sift?{" "}
          <Link className="underline-offset-4 hover:underline" href="/sign-up">
            Create an account
          </Link>
        </p>
      </div>
    </main>
  );
}
