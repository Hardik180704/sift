import { redirect } from "next/navigation";

import { createClient } from "@/lib/supabase/server";

export default async function ApplicationHomePage() {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) {
    redirect("/login");
  }

  return (
    <main>
      <h1>Your documents</h1>
      <p>Authenticated as {user.email ?? "your Sift account"}.</p>
    </main>
  );
}
