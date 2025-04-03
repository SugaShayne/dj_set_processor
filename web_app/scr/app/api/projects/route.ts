import { NextRequest } from 'next/server';
import { DatabaseService } from '@/lib/database';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function GET(request: NextRequest) {
  try {
    const db = new DatabaseService(process.env.DB as any);
    const projects = await db.getAllProjects();
    
    return Response.json({ projects });
  } catch (error) {
    console.error('Error fetching projects:', error);
    return Response.json({ error: 'Failed to fetch projects' }, { status: 500 });
  }
}
