import React from 'react';
import './globals.css';

export const metadata = {
  title: 'DJ Set Processor',
  description: 'Process DJ sets for YouTube compatibility',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <header className="border-b">
          <div className="container mx-auto py-4 px-4 flex justify-between items-center">
            <a href="/" className="text-xl font-bold">DJ Set Processor</a>
            <nav className="flex gap-6">
              <a href="/" className="hover:text-blue-600">Home</a>
              <a href="/upload" className="hover:text-blue-600">Upload</a>
              <a href="/projects" className="hover:text-blue-600">Projects</a>
            </nav>
          </div>
        </header>
        
        <main className="flex-1">
          {children}
        </main>
        
        <footer className="border-t py-6">
          <div className="container mx-auto text-center text-sm text-gray-500">
            <p>DJ Set Processor - Process your DJ sets for YouTube compatibility</p>
            <p className="mt-1">© {new Date().getFullYear()} DJ Set Processor</p>
          </div>
        </footer>
      </body>
    </html>
  );
}
