
import "./globals.css";

export const metadata = {
  title: "Monarch Dashboard (Local CSV)",
  description: "Upload your Monarch CSV and get fun, psychology-aware finance charts."
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen antialiased">{children}</body>
    </html>
  );
}
