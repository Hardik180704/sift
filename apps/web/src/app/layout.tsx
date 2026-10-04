import type { Metadata } from "next";
import { IBM_Plex_Mono, IBM_Plex_Sans, Instrument_Serif } from "next/font/google";
import type { ReactNode } from "react";

import "./globals.css";

const display = Instrument_Serif({
  subsets: ["latin"],
  weight: "400",
  variable: "--font-display",
  display: "swap",
});

const body = IBM_Plex_Sans({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  variable: "--font-body",
  display: "swap",
});

const data = IBM_Plex_Mono({
  subsets: ["latin"],
  weight: ["400", "500"],
  variable: "--font-data",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Sift — read the paperwork you avoid",
  description:
    "Upload leases, policies, and warranties. Ask questions. Get answers with page-level citations.",
};

const themeScript = `(function(){try{var t=localStorage.getItem("sift-theme");var d=window.matchMedia("(prefers-color-scheme: dark)").matches;var theme=t==="dark"||t==="light"?t:(d?"dark":"light");document.documentElement.setAttribute("data-theme",theme);}catch(e){}})();`;

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="en" data-scroll-behavior="smooth" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeScript }} />
      </head>
      <body className={`${display.variable} ${body.variable} ${data.variable}`}>{children}</body>
    </html>
  );
}
