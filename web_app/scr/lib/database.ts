import { D1Database } from '@cloudflare/workers-types';

// Database types
export interface Project {
  id: number;
  name: string;
  description?: string;
  original_video_path: string;
  processed_video_path?: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  created_at: string;
  updated_at: string;
}

export interface Track {
  id: number;
  project_id: number;
  track_name?: string;
  artist?: string;
  title?: string;
  start_time?: number;
  end_time?: number;
  confidence?: number;
  youtube_status?: 'available' | 'restricted' | 'blocked' | 'unknown';
  youtube_reason?: string;
}

export interface Thumbnail {
  id: number;
  project_id: number;
  path: string;
  timestamp?: number;
  selected: boolean;
  created_at: string;
}

export interface ProcessingJob {
  id: number;
  project_id: number;
  job_type: 'tracklist_generation' | 'youtube_check' | 'video_editing' | 'thumbnail_generation';
  status: 'pending' | 'processing' | 'completed' | 'failed';
  result?: string;
  error?: string;
  created_at: string;
  updated_at: string;
}

// Database service
export class DatabaseService {
  constructor(private db: D1Database) {}

  // Project methods
  async createProject(project: Omit<Project, 'id' | 'created_at' | 'updated_at'>): Promise<number> {
    const result = await this.db
      .prepare(
        'INSERT INTO projects (name, description, original_video_path, processed_video_path, status) VALUES (?, ?, ?, ?, ?)'
      )
      .bind(
        project.name,
        project.description || null,
        project.original_video_path,
        project.processed_video_path || null,
        project.status
      )
      .run();

    return result.meta.last_row_id as number;
  }

  async getProject(id: number): Promise<Project | null> {
    const result = await this.db
      .prepare('SELECT * FROM projects WHERE id = ?')
      .bind(id)
      .first<Project>();

    return result || null;
  }

  async updateProject(id: number, updates: Partial<Omit<Project, 'id' | 'created_at' | 'updated_at'>>): Promise<boolean> {
    const sets: string[] = [];
    const values: any[] = [];

    if (updates.name !== undefined) {
      sets.push('name = ?');
      values.push(updates.name);
    }

    if (updates.description !== undefined) {
      sets.push('description = ?');
      values.push(updates.description);
    }

    if (updates.original_video_path !== undefined) {
      sets.push('original_video_path = ?');
      values.push(updates.original_video_path);
    }

    if (updates.processed_video_path !== undefined) {
      sets.push('processed_video_path = ?');
      values.push(updates.processed_video_path);
    }

    if (updates.status !== undefined) {
      sets.push('status = ?');
      values.push(updates.status);
    }

    sets.push('updated_at = CURRENT_TIMESTAMP');

    if (sets.length === 0) {
      return false;
    }

    const query = `UPDATE projects SET ${sets.join(', ')} WHERE id = ?`;
    values.push(id);

    const result = await this.db.prepare(query).bind(...values).run();
    return result.success;
  }

  async getAllProjects(): Promise<Project[]> {
    const result = await this.db
      .prepare('SELECT * FROM projects ORDER BY created_at DESC')
      .all<Project>();

    return result.results;
  }

  // Track methods
  async createTrack(track: Omit<Track, 'id'>): Promise<number> {
    const result = await this.db
      .prepare(
        'INSERT INTO tracks (project_id, track_name, artist, title, start_time, end_time, confidence, youtube_status, youtube_reason) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'
      )
      .bind(
        track.project_id,
        track.track_name || null,
        track.artist || null,
        track.title || null,
        track.start_time || null,
        track.end_time || null,
        track.confidence || null,
        track.youtube_status || null,
        track.youtube_reason || null
      )
      .run();

    return result.meta.last_row_id as number;
  }

  async getTracksForProject(projectId: number): Promise<Track[]> {
    const result = await this.db
      .prepare('SELECT * FROM tracks WHERE project_id = ? ORDER BY start_time')
      .bind(projectId)
      .all<Track>();

    return result.results;
  }

  async updateTrack(id: number, updates: Partial<Omit<Track, 'id' | 'project_id'>>): Promise<boolean> {
    const sets: string[] = [];
    const values: any[] = [];

    if (updates.track_name !== undefined) {
      sets.push('track_name = ?');
      values.push(updates.track_name);
    }

    if (updates.artist !== undefined) {
      sets.push('artist = ?');
      values.push(updates.artist);
    }

    if (updates.title !== undefined) {
      sets.push('title = ?');
      values.push(updates.title);
    }

    if (updates.start_time !== undefined) {
      sets.push('start_time = ?');
      values.push(updates.start_time);
    }

    if (updates.end_time !== undefined) {
      sets.push('end_time = ?');
      values.push(updates.end_time);
    }

    if (updates.confidence !== undefined) {
      sets.push('confidence = ?');
      values.push(updates.confidence);
    }

    if (updates.youtube_status !== undefined) {
      sets.push('youtube_status = ?');
      values.push(updates.youtube_status);
    }

    if (updates.youtube_reason !== undefined) {
      sets.push('youtube_reason = ?');
      values.push(updates.youtube_reason);
    }

    if (sets.length === 0) {
      return false;
    }

    const query = `UPDATE tracks SET ${sets.join(', ')} WHERE id = ?`;
    values.push(id);

    const result = await this.db.prepare(query).bind(...values).run();
    return result.success;
  }

  // Thumbnail methods
  async createThumbnail(thumbnail: Omit<Thumbnail, 'id' | 'created_at'>): Promise<number> {
    const result = await this.db
      .prepare(
        'INSERT INTO thumbnails (project_id, path, timestamp, selected) VALUES (?, ?, ?, ?)'
      )
      .bind(
        thumbnail.project_id,
        thumbnail.path,
        thumbnail.timestamp || null,
        thumbnail.selected ? 1 : 0
      )
      .run();

    return result.meta.last_row_id as number;
  }

  async getThumbnailsForProject(projectId: number): Promise<Thumbnail[]> {
    const result = await this.db
      .prepare('SELECT * FROM thumbnails WHERE project_id = ? ORDER BY timestamp')
      .bind(projectId)
      .all<Thumbnail>();

    return result.results;
  }

  async updateThumbnailSelection(id: number, selected: boolean): Promise<boolean> {
    const result = await this.db
      .prepare('UPDATE thumbnails SET selected = ? WHERE id = ?')
      .bind(selected ? 1 : 0, id)
      .run();

    return result.success;
  }

  // Processing job methods
  async createProcessingJob(job: Omit<ProcessingJob, 'id' | 'created_at' | 'updated_at'>): Promise<number> {
    const result = await this.db
      .prepare(
        'INSERT INTO processing_jobs (project_id, job_type, status, result, error) VALUES (?, ?, ?, ?, ?)'
      )
      .bind(
        job.project_id,
        job.job_type,
        job.status,
        job.result || null,
        job.error || null
      )
      .run();

    return result.meta.last_row_id as number;
  }

  async getProcessingJobsForProject(projectId: number): Promise<ProcessingJob[]> {
    const result = await this.db
      .prepare('SELECT * FROM processing_jobs WHERE project_id = ? ORDER BY created_at DESC')
      .bind(projectId)
      .all<ProcessingJob>();

    return result.results;
  }

  async updateProcessingJob(id: number, updates: Partial<Omit<ProcessingJob, 'id' | 'project_id' | 'job_type' | 'created_at' | 'updated_at'>>): Promise<boolean> {
    const sets: string[] = [];
    const values: any[] = [];

    if (updates.status !== undefined) {
      sets.push('status = ?');
      values.push(updates.status);
    }

    if (updates.result !== undefined) {
      sets.push('result = ?');
      values.push(updates.result);
    }

    if (updates.error !== undefined) {
      sets.push('error = ?');
      values.push(updates.error);
    }

    sets.push('updated_at = CURRENT_TIMESTAMP');

    if (sets.length === 0) {
      return false;
    }

    const query = `UPDATE processing_jobs SET ${sets.join(', ')} WHERE id = ?`;
    values.push(id);

    const result = await this.db.prepare(query).bind(...values).run();
    return result.success;
  }
}
