"use client";

import { useEffect, useState } from "react";

export function ThemeToggle() {
  const [theme, setTheme] = useState<"light" | "dark">("light");

  useEffect(() => {
    const current = document.documentElement.getAttribute("data-theme");
    setTheme(current === "dark" ? "dark" : "light");
  }, []);

  function toggle() {
    const next = theme === "dark" ? "light" : "dark";
    setTheme(next);
    document.documentElement.setAttribute("data-theme", next);
    localStorage.setItem("sift-theme", next);
  }

  return (
    <button
      aria-label={theme === "dark" ? "Switch to light theme" : "Switch to dark theme"}
      className="rounded-md border hairline px-2.5 py-1.5 text-sm transition-colors hover:bg-black/5 dark:hover:bg-white/10"
      onClick={toggle}
      type="button"
    >
      {theme === "dark" ? "Light" : "Dark"}
    </button>
  );
}
