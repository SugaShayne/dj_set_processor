import { NextRequest } from 'next/server';
import { DatabaseService } from '@/lib/database';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function POST(request: NextRequest, { params }: { params: { id: string, thumbnailId: string } }) {
  try {
    const projectId = parseInt(params.id);
    const thumbnailId = parseInt(params.thumbnailId);
    
    if (isNaN(projectId) || isNaN(thumbnailId)) {
      return Response.json({ error: 'Invalid project ID or thumbnail ID' }, { status: 400 });
    }

    const db = new DatabaseService(process.env.DB as any);
    
    // First, unselect all thumbnails for this project
    const thumbnails = await db.getThumbnailsForProject(projectId);
    for (const thumbnail of thumbnails) {
      await db.updateThumbnailSelection(thumbnail.id, false);
    }
    
    // Then select the specified thumbnail
    const success = await db.updateThumbnailSelection(thumbnailId, true);

    if (!success) {
      return Response.json({ error: 'Failed to select thumbnail' }, { status: 500 });
    }

    return Response.json({ 
      success: true,
      message: 'Thumbnail selected successfully'
    });
  } catch (error) {
    console.error('Error selecting thumbnail:', error);
    return Response.json({ error: 'Failed to select thumbnail' }, { status: 500 });
  }
}
