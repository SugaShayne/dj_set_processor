import { NextRequest } from 'next/server';
import { DatabaseService } from '@/lib/database';
import { processDJSet } from '@/lib/processor';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function POST(request: NextRequest, { params }: { params: { id: string } }) {
  try {
    const projectId = parseInt(params.id);
    if (isNaN(projectId)) {
      return Response.json({ error: 'Invalid project ID' }, { status: 400 });
    }

    // Get project from database
    const db = new DatabaseService(process.env.DB as any);
    const project = await db.getProject(projectId);

    if (!project) {
      return Response.json({ error: 'Project not found' }, { status: 404 });
    }

    // Update project status to processing
    await db.updateProject(projectId, { status: 'processing' });

    // Create processing jobs for each step
    await db.createProcessingJob({
      project_id: projectId,
      job_type: 'tracklist_generation',
      status: 'pending'
    });

    await db.createProcessingJob({
      project_id: projectId,
      job_type: 'youtube_check',
      status: 'pending'
    });

    await db.createProcessingJob({
      project_id: projectId,
      job_type: 'video_editing',
      status: 'pending'
    });

    await db.createProcessingJob({
      project_id: projectId,
      job_type: 'thumbnail_generation',
      status: 'pending'
    });

    // Start processing in the background
    processDJSet(project.original_video_path, projectId)
      .then(async (result) => {
        // Update project with processed video path
        await db.updateProject(projectId, {
          processed_video_path: result.editedVideoPath,
          status: 'completed'
        });

        // Update processing jobs
        const jobs = await db.getProcessingJobsForProject(projectId);
        
        // Update tracklist generation job
        const tracklistJob = jobs.find(job => job.job_type === 'tracklist_generation');
        if (tracklistJob) {
          await db.updateProcessingJob(tracklistJob.id, {
            status: 'completed',
            result: result.tracklistPath
          });
        }

        // Update YouTube check job
        const youtubeJob = jobs.find(job => job.job_type === 'youtube_check');
        if (youtubeJob) {
          await db.updateProcessingJob(youtubeJob.id, {
            status: 'completed',
            result: result.compatibilityPath
          });
        }

        // Update video editing job
        const videoJob = jobs.find(job => job.job_type === 'video_editing');
        if (videoJob) {
          await db.updateProcessingJob(videoJob.id, {
            status: 'completed',
            result: result.editedVideoPath
          });
        }

        // Update thumbnail generation job
        const thumbnailJob = jobs.find(job => job.job_type === 'thumbnail_generation');
        if (thumbnailJob) {
          await db.updateProcessingJob(thumbnailJob.id, {
            status: 'completed',
            result: JSON.stringify(result.thumbnailPaths)
          });
        }

        // Save thumbnails to database
        for (const thumbnailPath of result.thumbnailPaths) {
          await db.createThumbnail({
            project_id: projectId,
            path: thumbnailPath,
            selected: false
          });
        }

        // Load tracklist data and save tracks to database
        const fs = require('fs');
        const tracklist = JSON.parse(fs.readFileSync(result.tracklistPath, 'utf8'));
        
        if (tracklist.tracks) {
          for (const track of tracklist.tracks) {
            // Load compatibility data
            const compatibility = JSON.parse(fs.readFileSync(result.compatibilityPath, 'utf8'));
            const trackCompatibility = compatibility.find((t: any) => 
              t.track.artist === track.artist && t.track.title === track.title
            );

            await db.createTrack({
              project_id: projectId,
              track_name: track.track_name || `${track.artist} - ${track.title}`,
              artist: track.artist,
              title: track.title,
              start_time: track.start_time,
              end_time: track.end_time,
              confidence: track.confidence,
              youtube_status: trackCompatibility?.status || 'unknown',
              youtube_reason: trackCompatibility?.reason
            });
          }
        }
      })
      .catch(async (error) => {
        console.error('Error processing DJ set:', error);
        
        // Update project status to failed
        await db.updateProject(projectId, { status: 'failed' });
        
        // Update processing jobs
        const jobs = await db.getProcessingJobsForProject(projectId);
        for (const job of jobs) {
          if (job.status === 'pending' || job.status === 'processing') {
            await db.updateProcessingJob(job.id, {
              status: 'failed',
              error: error.message
            });
          }
        }
      });

    return Response.json({ 
      success: true, 
      message: 'Processing started',
      projectId
    });
  } catch (error) {
    console.error('Error starting processing:', error);
    return Response.json({ error: 'Failed to start processing' }, { status: 500 });
  }
}
