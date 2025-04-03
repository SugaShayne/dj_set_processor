import React from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';

export default function UploadPage() {
  return (
    <div className="container mx-auto py-10">
      <div className="flex flex-col items-center justify-center space-y-6">
        <h1 className="text-3xl font-bold tracking-tight">Upload DJ Set</h1>
        <p className="text-muted-foreground max-w-[600px] text-center">
          Upload your DJ set video to process it. We'll identify tracks, check YouTube compatibility, 
          edit out blocked content, and generate thumbnails.
        </p>
        
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle>Upload Form</CardTitle>
            <CardDescription>
              Supported formats: MP4, MOV, AVI, MKV, WEBM
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form action="/api/upload" method="POST" encType="multipart/form-data" className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name">Project Name</Label>
                <Input id="name" name="name" placeholder="My Awesome DJ Set" required />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="description">Description (Optional)</Label>
                <Textarea id="description" name="description" placeholder="Description of your DJ set" />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="file">Video File</Label>
                <Input id="file" name="file" type="file" accept="video/*" required />
              </div>
            
              <Button type="submit" className="w-full">Upload and Process</Button>
            </form>
          </CardContent>
          <CardFooter className="text-sm text-muted-foreground">
            <p>Maximum file size: 2GB. Processing may take some time depending on the length of your video.</p>
          </CardFooter>
        </Card>
      </div>
    </div>
  );
}
