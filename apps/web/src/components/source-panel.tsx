"use client";

import { useEffect, useRef, type ReactNode } from "react";

type SourcePanelProps = {
  onClose: () => void;
  open: boolean;
  children: ReactNode;
  title: string;
};

export function SourcePanel({ onClose, open, children, title }: SourcePanelProps) {
  const closeRef = useRef<HTMLButtonElement | null>(null);

  useEffect(() => {
    if (!open) return;
    closeRef.current?.focus();
    function onKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") onClose();
    }
    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-end lg:items-stretch">
      <button
        aria-label="Close source panel"
        className="absolute inset-0 cursor-default bg-black/30"
        onClick={onClose}
        tabIndex={-1}
        type="button"
      />
      <aside
        aria-label="Source evidence"
        aria-modal="true"
        className="workspace-shadow relative flex max-h-[80vh] w-full flex-col overflow-y-auto rounded-t-xl border-t hairline bg-[var(--paper-raised)] p-5 animate-enter lg:static lg:my-6 lg:mr-6 lg:max-h-none lg:w-96 lg:rounded-xl lg:border"
        role="dialog"
      >
        <header className="mb-4 flex items-center justify-between gap-3">
          <p className="font-data text-xs uppercase tracking-widest text-[var(--ink-soft)]">
            {title}
          </p>
          <button
            className="rounded-md border hairline px-2 py-1 text-sm"
            onClick={onClose}
            ref={closeRef}
            type="button"
          >
            Close
          </button>
        </header>
        {children}
      </aside>
    </div>
  );
}
