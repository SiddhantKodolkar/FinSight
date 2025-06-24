// src/app/layout.tsx

import "./globals.css";
import { ReactNode } from "react";
import { UserProvider } from "./components/UserContext";

export const metadata = {
  title: "FinSight",
  description: "Financial insights dashboard",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <UserProvider>
          {children}
        </UserProvider>
      </body>
    </html>
  );
}
