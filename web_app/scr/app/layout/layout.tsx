import React from 'react';
import Link from 'next/link';

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b">
        <div className="container mx-auto py-4 flex justify-between items-center">
          <Link href="/" className="text-xl font-bold">DJ Set Processor</Link>
          <nav className="flex gap-6">
            <Link href="/" className="hover:text-primary">Home</Link>
            <Link href="/upload" className="hover:text-primary">Upload</Link>
            <Link href="/projects" className="hover:text-primary">Projects</Link>
          </nav>
        </div>
      </header>
      
      <main className="flex-1">
        {children}
      </main>
      
      <footer className="border-t py-6">
        <div className="container mx-auto text-center text-sm text-muted-foreground">
          <p>DJ Set Processor - Process your DJ sets for YouTube compatibility</p>
          <p className="mt-1">© {new Date().getFullYear()} DJ Set Processor</p>
        </div>
      </footer>
    </div>
  );
}
