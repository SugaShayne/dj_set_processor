import { NextRequest } from 'next/server';
import { DatabaseService } from '@/lib/database';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function GET(request: NextRequest, { params }: { params: { id: string } }) {
  try {
    const projectId = parseInt(params.id);
    if (isNaN(projectId)) {
      return Response.json({ error: 'Invalid project ID' }, { status: 400 });
    }

    const db = new DatabaseService(process.env.DB as any);
    const project = await db.getProject(projectId);

    if (!project) {
      return Response.json({ error: 'Project not found' }, { status: 404 });
    }

    // Get tracks for project
    const tracks = await db.getTracksForProject(projectId);

    // Get thumbnails for project
    const thumbnails = await db.getThumbnailsForProject(projectId);

    // Get processing jobs for project
    const jobs = await db.getProcessingJobsForProject(projectId);

    return Response.json({ 
      project,
      tracks,
      thumbnails,
      jobs
    });
  } catch (error) {
    console.error('Error fetching project details:', error);
    return Response.json({ error: 'Failed to fetch project details' }, { status: 500 });
  }
}
