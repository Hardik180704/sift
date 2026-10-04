import Link from "next/link";

export default function HomePage() {
  return (
    <main className="mx-auto flex min-h-screen max-w-5xl flex-col px-6 py-8 lg:px-10 lg:py-12">
      <header className="flex items-center justify-between">
        <p className="font-display text-xl leading-none">
          Sift<span className="text-[var(--ink-soft)]">.</span>
        </p>
        <div className="flex items-center gap-2 font-data text-sm">
          <Link
            className="rounded-md border hairline px-3 py-1.5 transition-colors hover:bg-black/5 dark:hover:bg-white/10"
            href="/login"
          >
            Sign in
          </Link>
          <Link
            className="rounded-md bg-[var(--ink)] px-3 py-1.5 text-[var(--paper-raised)] transition-opacity hover:opacity-90"
            href="/sign-up"
          >
            Create account
          </Link>
        </div>
      </header>

      <section className="mt-20 max-w-3xl lg:mt-28">
        <p className="font-data text-xs uppercase tracking-widest text-[var(--ink-soft)]">
          Document intelligence
        </p>
        <h1 className="font-display mt-5 text-5xl leading-[1.05] sm:text-6xl lg:text-7xl">
          The paperwork you avoid reading, <span className="evidence-mark">read</span>.
        </h1>
        <p className="mt-6 max-w-xl text-base leading-relaxed text-[var(--ink-soft)] sm:text-lg">
          Upload a lease, policy, warranty, or invoice. Ask a question. Sift answers from your
          document — and shows you the exact page it came from.
        </p>
        <div className="mt-8 flex flex-wrap items-center gap-3">
          <Link
            className="rounded-md bg-[var(--ink)] px-5 py-2.5 text-sm font-medium text-[var(--paper-raised)] transition-opacity hover:opacity-90"
            href="/sign-up"
          >
            Start reading
          </Link>
          <Link
            className="font-data text-sm text-[var(--ink-soft)] underline-offset-4 hover:underline"
            href="/login"
          >
            I already have an account
          </Link>
        </div>
      </section>

      <section className="mt-16 max-w-2xl lg:mt-24">
        <figure className="rounded-xl border hairline bg-[var(--paper-raised)] p-5 lg:p-6">
          <blockquote className="text-sm leading-relaxed sm:text-base">
            “If the tenant neither renews nor vacates, rent continues{" "}
            <span className="evidence-mark">month to month after the renewal deadline</span> of 31
            January 2027.”
          </blockquote>
          <figcaption className="font-data mt-4 text-xs text-[var(--ink-soft)]">
            lease.pdf · page 12 · citation 1
          </figcaption>
        </figure>
      </section>

      <footer className="font-data mt-auto flex flex-wrap gap-x-6 gap-y-2 py-6 text-xs text-[var(--ink-soft)]">
        <span>Answers carry page-level citations.</span>
        <span>Insufficient evidence is stated, not invented.</span>
        <span>Action suggestions wait for your confirmation.</span>
      </footer>
    </main>
  );
}
