import Link from "next/link";
import { Suspense } from "react";

import { AuthForm } from "@/components/auth-form";

export default function SignUpPage() {
  return (
    <main>
      <h1>Create your Sift account</h1>
      <Suspense fallback={<p>Loading account form...</p>}>
        <AuthForm mode="sign-up" />
      </Suspense>
      <p>
        Already have an account? <Link href="/login">Sign in</Link>.
      </p>
    </main>
  );
}
