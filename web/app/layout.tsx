import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "RepoLens — See the shape of any codebase",
    template: "%s | RepoLens",
  },
  description:
    "Map an unfamiliar repository in minutes. RepoLens turns source code into a traceable architecture guide, dependency graph, and practical onboarding docs.",
  icons: {
    icon: "/repolens-logo.png",
  },
  openGraph: {
    title: "RepoLens — See the shape of any codebase",
    description:
      "A local-first codebase intelligence CLI for understanding, navigating, and documenting software projects.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
