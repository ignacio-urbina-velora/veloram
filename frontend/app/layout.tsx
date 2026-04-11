import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Velora Studio | Create Cinematic AI Videos",
  description: "Professional AI video generation platform. Create stunning 15-minute videos with multi-shot director workflow, avatar consistency, and GPU-powered rendering.",
  other: {
    "cryptomus": "2e91150b"
  }
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body suppressHydrationWarning>
        {children}
      </body>
    </html>
  );
}
