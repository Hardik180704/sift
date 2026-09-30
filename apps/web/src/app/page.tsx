import Link from "next/link";

export default function HomePage() {
  return (
    <main>
      <h1>Sift</h1>
      <p>Document intelligence, built around evidence.</p>
      <Link href="/login">Sign in</Link>
    </main>
  );
}
