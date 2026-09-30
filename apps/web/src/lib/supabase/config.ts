function requiredPublicEnvironment(
  name: "NEXT_PUBLIC_SUPABASE_URL" | "NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY",
) {
  const value = process.env[name];

  if (!value || value.startsWith("your-")) {
    throw new Error(`${name} must be configured before using Supabase.`);
  }

  return value;
}

export function getSupabasePublicConfig() {
  return {
    url: requiredPublicEnvironment("NEXT_PUBLIC_SUPABASE_URL"),
    publishableKey: requiredPublicEnvironment("NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY"),
  };
}
