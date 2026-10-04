const missingEnvironment = (name: string): never => {
  throw new Error(
    `${name} must be configured before using Supabase. Add it to apps/web/.env.local.`,
  );
};

export function getSupabasePublicConfig() {
  const url =
    process.env.NEXT_PUBLIC_SUPABASE_URL ?? missingEnvironment("NEXT_PUBLIC_SUPABASE_URL");
  const publishableKey =
    process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY ??
    missingEnvironment("NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY");

  if (url.startsWith("your-")) {
    missingEnvironment("NEXT_PUBLIC_SUPABASE_URL");
  }

  return { url, publishableKey };
}
