import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'RM-KI Operator UI',
  description: 'Cross-Tenant Operator-Plattform für die RM-KI-Plattform',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="de" suppressHydrationWarning>
      <body className="min-h-screen antialiased">{children}</body>
    </html>
  );
}
