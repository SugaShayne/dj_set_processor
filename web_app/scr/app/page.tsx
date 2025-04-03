import React from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';

export default function Home() {
  return (
    <div className="container mx-auto py-10">
      <div className="flex flex-col items-center justify-center space-y-6 text-center">
        <h1 className="text-4xl font-bold tracking-tight">DJ Set Processor</h1>
        <p className="text-xl text-muted-foreground max-w-[600px]">
          Process your DJ sets to create tracklists, check YouTube compatibility, 
          edit out blocked content, and generate thumbnails.
        </p>
        
        <div className="flex gap-4">
          <Link href="/upload">
            <Button size="lg">Upload DJ Set</Button>
          </Link>
          <Link href="/projects">
            <Button size="lg" variant="outline">View Projects</Button>
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mt-16">
        <Card>
          <CardHeader>
            <CardTitle>Tracklist Generation</CardTitle>
          </CardHeader>
          <CardContent>
            <p>Automatically identify tracks in your DJ set using audio fingerprinting technology.</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>YouTube Compatibility</CardTitle>
          </CardHeader>
          <CardContent>
            <p>Check if tracks in your mix would be blocked or restricted on YouTube.</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Video Editing</CardTitle>
          </CardHeader>
          <CardContent>
            <p>Automatically remove blocked content and add smooth transitions between clips.</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Thumbnail Generation</CardTitle>
          </CardHeader>
          <CardContent>
            <p>Create appealing thumbnails for your YouTube uploads from your video.</p>
          </CardContent>
        </Card>
      </div>

      <div className="mt-16">
        <h2 className="text-2xl font-bold mb-6 text-center">How It Works</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="flex flex-col items-center text-center">
            <div className="w-12 h-12 rounded-full bg-primary text-primary-foreground flex items-center justify-center mb-4">1</div>
            <h3 className="text-xl font-semibold mb-2">Upload Your DJ Set</h3>
            <p>Upload your DJ set video in any common format (MP4, MOV, AVI, etc.).</p>
          </div>
          
          <div className="flex flex-col items-center text-center">
            <div className="w-12 h-12 rounded-full bg-primary text-primary-foreground flex items-center justify-center mb-4">2</div>
            <h3 className="text-xl font-semibold mb-2">Automatic Processing</h3>
            <p>Our system identifies tracks, checks YouTube compatibility, edits the video, and generates thumbnails.</p>
          </div>
          
          <div className="flex flex-col items-center text-center">
            <div className="w-12 h-12 rounded-full bg-primary text-primary-foreground flex items-center justify-center mb-4">3</div>
            <h3 className="text-xl font-semibold mb-2">Download Results</h3>
            <p>Download your edited video and thumbnails, ready for YouTube upload.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
