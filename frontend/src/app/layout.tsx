import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "OSINT OMÉGA AI",
  description:
    "Plateforme d'investigation OSINT modulaire — usage légal et éthique uniquement.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="fr">
      <body className="min-h-screen antialiased">{children}</body>
    </html>
  );
}
