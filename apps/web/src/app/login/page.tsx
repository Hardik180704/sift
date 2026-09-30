import Link from "next/link";
import { Suspense } from "react";

import { AuthForm } from "@/components/auth-form";

export default function LoginPage() {
  return (
    <main>
      <h1>Sign in to Sift</h1>
      <Suspense fallback={<p>Loading sign-in form...</p>}>
        <AuthForm mode="login" />
      </Suspense>
      <p>
        New to Sift? <Link href="/sign-up">Create an account</Link>.
      </p>
    </main>
  );
}
