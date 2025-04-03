import { NextRequest } from 'next/server';
import { writeFile } from 'fs/promises';
import { join } from 'path';
import { ensureDirectories, getUploadPath } from '@/lib/processor';
import { DatabaseService } from '@/lib/database';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function POST(request: NextRequest) {
  try {
    // Ensure upload directory exists
    await ensureDirectories();

    const formData = await request.formData();
    const file = formData.get('file') as File;
    const name = formData.get('name') as string;
    const description = formData.get('description') as string;

    if (!file) {
      return Response.json({ error: 'No file uploaded' }, { status: 400 });
    }

    // Generate a unique filename
    const timestamp = Date.now();
    const originalFilename = file.name;
    const fileExtension = originalFilename.split('.').pop();
    const filename = `${timestamp}_${originalFilename}`;
    const filePath = getUploadPath(filename);

    // Convert file to buffer and save it
    const buffer = Buffer.from(await file.arrayBuffer());
    await writeFile(filePath, buffer);

    // Create project in database
    const db = new DatabaseService(process.env.DB as any);
    const projectId = await db.createProject({
      name: name || originalFilename,
      description,
      original_video_path: filePath,
      status: 'pending'
    });

    // Create initial processing job for tracklist generation
    await db.createProcessingJob({
      project_id: projectId,
      job_type: 'tracklist_generation',
      status: 'pending'
    });

    return Response.json({ 
      success: true, 
      projectId,
      message: 'File uploaded successfully',
      filePath
    });
  } catch (error) {
    console.error('Error uploading file:', error);
    return Response.json({ error: 'Failed to upload file' }, { status: 500 });
  }
}
