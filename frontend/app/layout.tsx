import "./globals.css";

export const metadata = {
  title: "RepoQuest",
  description: "Turn any GitHub repo into a contribution adventure.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
