// Database schema for the DJ Set Processor application
// This file will be used to initialize the D1 database

DROP TABLE IF EXISTS projects;
DROP TABLE IF EXISTS tracks;
DROP TABLE IF EXISTS thumbnails;
DROP TABLE IF EXISTS processing_jobs;

-- Projects table to store information about DJ set processing projects
CREATE TABLE projects (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  description TEXT,
  original_video_path TEXT NOT NULL,
  processed_video_path TEXT,
  status TEXT NOT NULL DEFAULT 'pending', -- pending, processing, completed, failed
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Tracks table to store information about tracks identified in DJ sets
CREATE TABLE tracks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL,
  track_name TEXT,
  artist TEXT,
  title TEXT,
  start_time REAL,
  end_time REAL,
  confidence REAL,
  youtube_status TEXT, -- available, restricted, blocked, unknown
  youtube_reason TEXT,
  FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Thumbnails table to store information about generated thumbnails
CREATE TABLE thumbnails (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL,
  path TEXT NOT NULL,
  timestamp REAL,
  selected BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Processing jobs table to store information about background processing jobs
CREATE TABLE processing_jobs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL,
  job_type TEXT NOT NULL, -- tracklist_generation, youtube_check, video_editing, thumbnail_generation
  status TEXT NOT NULL DEFAULT 'pending', -- pending, processing, completed, failed
  result TEXT,
  error TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Create indexes for faster queries
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_tracks_project_id ON tracks(project_id);
CREATE INDEX idx_thumbnails_project_id ON thumbnails(project_id);
CREATE INDEX idx_processing_jobs_project_id ON processing_jobs(project_id);
CREATE INDEX idx_processing_jobs_status ON processing_jobs(status);
