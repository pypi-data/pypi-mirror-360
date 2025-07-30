import type { Metadata } from "next";
import { Geist_Mono } from "next/font/google";
import localFont from "next/font/local";
import "./globals.css";
import { Providers } from "@/lib/providers";
import { Toaster } from "@/components/ui/sonner";

const copernicus = localFont({
  variable: "--font-copernicus",
  src: [
    {
      path: "../../public/fonts/CopernicusTrial-Book-BF66160450c2e92.ttf",
      weight: "400",
      style: "normal",
    },
    {
      path: "../../public/fonts/CopernicusTrial-BookItalic-BF661604511b981.ttf",
      weight: "400",
      style: "italic",
    },
    {
      path: "../../public/fonts/CopernicusTrial-Medium-BF66160450d988d.ttf",
      weight: "500",
      style: "normal",
    },
    {
      path: "../../public/fonts/CopernicusTrial-MediumItalic-BF6616045177c71.ttf",
      weight: "500",
      style: "italic",
    },
    {
      path: "../../public/fonts/CopernicusTrial-Bold-BF6616045097aac.ttf",
      weight: "700",
      style: "normal",
    },
    {
      path: "../../public/fonts/CopernicusTrial-BoldItalic-BF6616045093ed8.ttf",
      weight: "700",
      style: "italic",
    },
  ],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Doc81",
  description: "Build your knowledge on top of established building blocks",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${copernicus.variable} ${geistMono.variable} antialiased`}
      >
        <Providers>{children}</Providers>
        <Toaster position="top-right" />
      </body>
    </html>
  );
}
