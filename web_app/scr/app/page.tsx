import React from 'react';

export default function HomePage() {
  return (
    <div className="container mx-auto py-10 px-4">
      <h1 className="text-3xl font-bold mb-6">DJ Set Processor</h1>
      
      <div className="max-w-2xl mx-auto bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-xl font-semibold mb-4">Process your DJ sets for YouTube compatibility</h2>
        
        <p className="mb-4">
          Welcome to the DJ Set Processor! This application helps you:
        </p>
        
        <ul className="list-disc pl-6 mb-6 space-y-2">
          <li>Generate tracklists from your DJ sets</li>
          <li>Check tracks for YouTube compatibility</li>
          <li>Edit videos to remove blocked content</li>
          <li>Create thumbnails for YouTube uploads</li>
        </ul>
        
        <div className="flex justify-center">
          <a href="/upload" className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors">
            Get Started
          </a>
        </div>
      </div>
    </div>
  );
}
