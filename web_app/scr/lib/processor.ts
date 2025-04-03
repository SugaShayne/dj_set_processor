import { spawn } from 'child_process';
import path from 'path';
import fs from 'fs';
import { promisify } from 'util';

const mkdir = promisify(fs.mkdir);
const writeFile = promisify(fs.writeFile);
const readFile = promisify(fs.readFile);
const exists = promisify(fs.exists);

// Base paths
const UPLOAD_DIR = path.join(process.cwd(), 'uploads');
const TEMP_DIR = path.join(process.cwd(), 'temp');
const OUTPUT_DIR = path.join(process.cwd(), 'output');

// Ensure directories exist
export async function ensureDirectories() {
  await mkdir(UPLOAD_DIR, { recursive: true });
  await mkdir(TEMP_DIR, { recursive: true });
  await mkdir(OUTPUT_DIR, { recursive: true });
}

// Path helpers
export function getUploadPath(filename: string): string {
  return path.join(UPLOAD_DIR, filename);
}

export function getTempPath(filename: string): string {
  return path.join(TEMP_DIR, filename);
}

export function getOutputPath(filename: string): string {
  return path.join(OUTPUT_DIR, filename);
}

// Execute a Python module
export async function executePythonModule(
  modulePath: string,
  scriptName: string,
  args: string[]
): Promise<{ stdout: string; stderr: string }> {
  return new Promise((resolve, reject) => {
    const process = spawn('python3', [
      '-m',
      `${modulePath}.${scriptName}`,
      ...args,
    ]);

    let stdout = '';
    let stderr = '';

    process.stdout.on('data', (data) => {
      stdout += data.toString();
    });

    process.stderr.on('data', (data) => {
      stderr += data.toString();
    });

    process.on('close', (code) => {
      if (code === 0) {
        resolve({ stdout, stderr });
      } else {
        reject(new Error(`Process exited with code ${code}: ${stderr}`));
      }
    });

    process.on('error', (err) => {
      reject(err);
    });
  });
}

// Tracklist generation
export async function generateTracklist(videoPath: string, outputPath: string): Promise<string> {
  await ensureDirectories();
  
  try {
    const result = await executePythonModule(
      'modules.tracklist_generator',
      'cli',
      ['identify', videoPath, '--output', outputPath]
    );
    
    return outputPath;
  } catch (error) {
    console.error('Error generating tracklist:', error);
    throw error;
  }
}

// YouTube compatibility check
export async function checkYouTubeCompatibility(
  tracklistPath: string,
  outputPath: string
): Promise<string> {
  await ensureDirectories();
  
  try {
    const result = await executePythonModule(
      'modules.youtube_checker',
      'cli',
      ['check-tracklist', tracklistPath, '--output', outputPath]
    );
    
    return outputPath;
  } catch (error) {
    console.error('Error checking YouTube compatibility:', error);
    throw error;
  }
}

// Video editing
export async function editVideo(
  videoPath: string,
  tracklistPath: string,
  outputPath: string
): Promise<string> {
  await ensureDirectories();
  
  try {
    const result = await executePythonModule(
      'modules.video_editor',
      'cli',
      ['edit-from-tracklist', videoPath, tracklistPath, '--output', outputPath]
    );
    
    return outputPath;
  } catch (error) {
    console.error('Error editing video:', error);
    throw error;
  }
}

// Thumbnail generation
export async function generateThumbnails(
  videoPath: string,
  tracklistPath: string,
  outputDir: string,
  count: number = 10
): Promise<string[]> {
  await ensureDirectories();
  
  try {
    const result = await executePythonModule(
      'modules.thumbnail_generator',
      'cli',
      [
        'generate-from-tracklist',
        videoPath,
        tracklistPath,
        '--output',
        outputDir,
        '--count',
        count.toString(),
      ]
    );
    
    // Parse output to get thumbnail paths
    const lines = result.stdout.split('\n');
    const thumbnailPaths: string[] = [];
    
    for (const line of lines) {
      if (line.includes('.jpg') || line.includes('.png')) {
        const path = line.trim().split(' ').pop();
        if (path) {
          thumbnailPaths.push(path);
        }
      }
    }
    
    return thumbnailPaths;
  } catch (error) {
    console.error('Error generating thumbnails:', error);
    throw error;
  }
}

// Process a DJ set video end-to-end
export async function processDJSet(
  videoPath: string,
  projectId: number
): Promise<{
  tracklistPath: string;
  compatibilityPath: string;
  editedVideoPath: string;
  thumbnailPaths: string[];
}> {
  await ensureDirectories();
  
  // Create project directories
  const projectDir = path.join(OUTPUT_DIR, `project_${projectId}`);
  await mkdir(projectDir, { recursive: true });
  
  // Step 1: Generate tracklist
  const tracklistPath = path.join(projectDir, 'tracklist.json');
  await generateTracklist(videoPath, tracklistPath);
  
  // Step 2: Check YouTube compatibility
  const compatibilityPath = path.join(projectDir, 'compatibility.json');
  await checkYouTubeCompatibility(tracklistPath, compatibilityPath);
  
  // Step 3: Edit video
  const videoFilename = path.basename(videoPath);
  const editedVideoPath = path.join(projectDir, `edited_${videoFilename}`);
  await editVideo(videoPath, compatibilityPath, editedVideoPath);
  
  // Step 4: Generate thumbnails
  const thumbnailsDir = path.join(projectDir, 'thumbnails');
  await mkdir(thumbnailsDir, { recursive: true });
  const thumbnailPaths = await generateThumbnails(
    videoPath,
    compatibilityPath,
    thumbnailsDir
  );
  
  return {
    tracklistPath,
    compatibilityPath,
    editedVideoPath,
    thumbnailPaths,
  };
}
