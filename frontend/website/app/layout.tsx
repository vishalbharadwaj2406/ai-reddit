import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Header from "@/components/Header/Header";
import { AppLayout } from "@/components";
import LoginModal from "@/components/LoginModal";
import "./globals.css";
import SessionWrapper from "@/components/providers/SessionWrapper";
import { ToastProvider } from "@/components/feedback/ToastProvider";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "AI Social - Connect through Conversations",
  description: "Join intelligent conversations powered by AI. Connect, share, and explore ideas with our community.",
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
        <SessionWrapper>
          <ToastProvider>
            <Header />
            <LoginModal />
            <AppLayout>
              {children}
            </AppLayout>
          </ToastProvider>
        </SessionWrapper>
      </body>
    </html>
  );
}
