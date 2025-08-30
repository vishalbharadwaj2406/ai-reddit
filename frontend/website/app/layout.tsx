import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Header from "@/components/Header/Header";
import { AppLayout } from "@/components";
import "./globals.css";
import SessionWrapper from "@/components/providers/SessionWrapper";
import { ToastProvider } from "@/components/feedback/ToastProvider";
import AuthErrorBoundary from "@/components/auth/AuthErrorBoundary";
import ErrorBoundary from "@/components/error/ErrorBoundary";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "AI Social - Production Authentication System",
  description: "Professional-grade conversation platform with backend OAuth integration",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <ErrorBoundary>
          <SessionWrapper>
            <AuthErrorBoundary>
              <ToastProvider>
                <Header />
                <AppLayout>
                  {children}
                </AppLayout>
              </ToastProvider>
            </AuthErrorBoundary>
          </SessionWrapper>
        </ErrorBoundary>
      </body>
    </html>
  );
}
