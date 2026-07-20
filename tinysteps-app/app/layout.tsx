import type { Metadata } from "next";
import "./globals.css";

// Root layout owns only the document shell. App chrome (header, bottom nav) lives in
// the (app) group so marketing pages can present a full-width sales page without a
// navigation bar pointing at screens a signed-out visitor cannot reach.
export const metadata: Metadata = {
  title: "TinySteps",
  description: "English practice in small, practical steps.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="vi">
      <body>{children}</body>
    </html>
  );
}
