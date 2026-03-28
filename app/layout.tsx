
import "./globals.css";

export const metadata = {
  title: "Flo-Fi",
  description: "AI-generated anime characters and original content."
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen antialiased">{children}</body>
    </html>
  );
}
