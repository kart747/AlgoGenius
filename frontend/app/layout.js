import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import Navbar from "@/components/Navbar";
import { UserProvider } from "@/components/UserProvider";
import ToastViewport from "@/components/ToastViewport";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata = {
  title: "AlgoGenius - Master Algorithms",
  description: "Learn and practice algorithms with AlgoGenius",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <UserProvider>
          <Navbar />
          {children}
        </UserProvider>
        <ToastViewport />
      </body>
    </html>
  );
}
