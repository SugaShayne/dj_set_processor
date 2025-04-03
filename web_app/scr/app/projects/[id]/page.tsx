import React from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

export default function ProjectDetailPage({ params }: { params: { id: string } }) {
  const projectId = params.id;

  return (
    <div className="container mx-auto py-10">
      <div className="flex justify-between items-center mb-6">
        <div>
          <Link href="/projects" className="text-sm text-muted-foreground hover:underline mb-2 inline-block">
            ← Back to Projects
          </Link>
          <h1 className="text-3xl font-bold tracking-tight" id="project-title">Project Details</h1>
        </div>
        <div id="project-actions"></div>
      </div>

      <div id="project-status" className="mb-6"></div>
      
      <Tabs defaultValue="tracks" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="tracks">Tracklist</TabsTrigger>
          <TabsTrigger value="thumbnails">Thumbnails</TabsTrigger>
          <TabsTrigger value="video">Processed Video</TabsTrigger>
          <TabsTrigger value="jobs">Processing Jobs</TabsTrigger>
        </TabsList>
        
        <TabsContent value="tracks" className="py-4">
          <div id="tracks-container">
            <div className="text-center py-8 text-muted-foreground">
              Loading tracks...
            </div>
          </div>
        </TabsContent>
        
        <TabsContent value="thumbnails" className="py-4">
          <div id="thumbnails-container">
            <div className="text-center py-8 text-muted-foreground">
              Loading thumbnails...
            </div>
          </div>
        </TabsContent>
        
        <TabsContent value="video" className="py-4">
          <div id="video-container">
            <div className="text-center py-8 text-muted-foreground">
              Loading video...
            </div>
          </div>
        </TabsContent>
        
        <TabsContent value="jobs" className="py-4">
          <div id="jobs-container">
            <div className="text-center py-8 text-muted-foreground">
              Loading processing jobs...
            </div>
          </div>
        </TabsContent>
      </Tabs>

      <script dangerouslySetInnerHTML={{ __html: `
        // Fetch project details on page load
        document.addEventListener('DOMContentLoaded', async () => {
          try {
            const projectId = ${projectId};
            const response = await fetch(\`/api/projects/\${projectId}\`);
            const data = await response.json();
            
            if (data.error) {
              throw new Error(data.error);
            }
            
            // Update project title
            document.getElementById('project-title').textContent = data.project.name;
            
            // Update project status
            const statusColor = {
              'pending': 'bg-yellow-500',
              'processing': 'bg-blue-500',
              'completed': 'bg-green-500',
              'failed': 'bg-red-500'
            }[data.project.status] || 'bg-gray-500';
            
            document.getElementById('project-status').innerHTML = \`
              <div class="flex items-center gap-2">
                <span class="px-3 py-1 text-sm font-semibold rounded-full \${statusColor} text-white">
                  \${data.project.status.charAt(0).toUpperCase() + data.project.status.slice(1)}
                </span>
                <span class="text-sm text-muted-foreground">
                  Created: \${new Date(data.project.created_at).toLocaleString()}
                </span>
              </div>
              <p class="mt-2">\${data.project.description || 'No description'}</p>
            \`;
            
            // Update project actions
            if (data.project.status === 'pending') {
              document.getElementById('project-actions').innerHTML = \`
                <button id="start-processing" class="px-4 py-2 bg-primary text-primary-foreground rounded-md text-sm font-medium">
                  Start Processing
                </button>
              \`;
              
              document.getElementById('start-processing').addEventListener('click', async () => {
                try {
                  const response = await fetch(\`/api/projects/\${projectId}/process\`, {
                    method: 'POST'
                  });
                  const result = await response.json();
                  
                  if (result.success) {
                    window.location.reload();
                  } else {
                    alert('Failed to start processing: ' + (result.error || 'Unknown error'));
                  }
                } catch (error) {
                  console.error('Error starting processing:', error);
                  alert('Failed to start processing. Please try again later.');
                }
              });
            }
            
            // Update tracks tab
            const tracksContainer = document.getElementById('tracks-container');
            if (data.tracks && data.tracks.length > 0) {
              tracksContainer.innerHTML = \`
                <div class="overflow-x-auto">
                  <table class="w-full border-collapse">
                    <thead>
                      <tr class="border-b">
                        <th class="text-left py-3 px-4">Track</th>
                        <th class="text-left py-3 px-4">Artist</th>
                        <th class="text-left py-3 px-4">Title</th>
                        <th class="text-left py-3 px-4">Time</th>
                        <th class="text-left py-3 px-4">YouTube Status</th>
                      </tr>
                    </thead>
                    <tbody id="tracks-list"></tbody>
                  </table>
                </div>
              \`;
              
              const tracksList = document.getElementById('tracks-list');
              data.tracks.forEach(track => {
                const startTime = track.start_time ? formatTime(track.start_time) : 'N/A';
                const endTime = track.end_time ? formatTime(track.end_time) : 'N/A';
                const statusColor = {
                  'available': 'bg-green-500',
                  'restricted': 'bg-yellow-500',
                  'blocked': 'bg-red-500',
                  'unknown': 'bg-gray-500'
                }[track.youtube_status || 'unknown'];
                
                const row = document.createElement('tr');
                row.className = 'border-b hover:bg-muted/50';
                row.innerHTML = \`
                  <td class="py-3 px-4">\${track.track_name || 'Unknown'}</td>
                  <td class="py-3 px-4">\${track.artist || 'Unknown'}</td>
                  <td class="py-3 px-4">\${track.title || 'Unknown'}</td>
                  <td class="py-3 px-4">\${startTime} - \${endTime}</td>
                  <td class="py-3 px-4">
                    <span class="px-2 py-1 text-xs font-semibold rounded-full \${statusColor} text-white">
                      \${(track.youtube_status || 'unknown').charAt(0).toUpperCase() + (track.youtube_status || 'unknown').slice(1)}
                    </span>
                  </td>
                \`;
                tracksList.appendChild(row);
              });
            } else {
              tracksContainer.innerHTML = \`
                <div class="text-center py-8 text-muted-foreground">
                  No tracks found. Process the project to generate a tracklist.
                </div>
              \`;
            }
            
            // Update thumbnails tab
            const thumbnailsContainer = document.getElementById('thumbnails-container');
            if (data.thumbnails && data.thumbnails.length > 0) {
              thumbnailsContainer.innerHTML = \`
                <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4" id="thumbnails-grid"></div>
              \`;
              
              const thumbnailsGrid = document.getElementById('thumbnails-grid');
              data.thumbnails.forEach(thumbnail => {
                const card = document.createElement('div');
                card.className = 'border rounded-lg overflow-hidden ' + (thumbnail.selected ? 'ring-2 ring-primary' : '');
                card.innerHTML = \`
                  <img src="/\${thumbnail.path}" alt="Thumbnail" class="w-full aspect-video object-cover" />
                  <div class="p-2 flex justify-between items-center">
                    <span class="text-xs text-muted-foreground">\${thumbnail.timestamp ? formatTime(thumbnail.timestamp) : 'N/A'}</span>
                    <button class="select-thumbnail px-2 py-1 text-xs bg-primary text-primary-foreground rounded" data-id="\${thumbnail.id}">
                      \${thumbnail.selected ? 'Selected' : 'Select'}
                    </button>
                  </div>
                \`;
                thumbnailsGrid.appendChild(card);
              });
              
              // Add event listeners to select buttons
              document.querySelectorAll('.select-thumbnail').forEach(button => {
                button.addEventListener('click', async (e) => {
                  const thumbnailId = e.target.dataset.id;
                  try {
                    const response = await fetch(\`/api/projects/\${projectId}/thumbnails/\${thumbnailId}/select\`, {
                      method: 'POST'
                    });
                    const result = await response.json();
                    
                    if (result.success) {
                      window.location.reload();
                    } else {
                      alert('Failed to select thumbnail: ' + (result.error || 'Unknown error'));
                    }
                  } catch (error) {
                    console.error('Error selecting thumbnail:', error);
                    alert('Failed to select thumbnail. Please try again later.');
                  }
                });
              });
            } else {
              thumbnailsContainer.innerHTML = \`
                <div class="text-center py-8 text-muted-foreground">
                  No thumbnails found. Process the project to generate thumbnails.
                </div>
              \`;
            }
            
            // Update video tab
            const videoContainer = document.getElementById('video-container');
            if (data.project.processed_video_path) {
              videoContainer.innerHTML = \`
                <div class="aspect-video bg-black rounded-lg overflow-hidden">
                  <video controls class="w-full h-full">
                    <source src="/\${data.project.processed_video_path}" type="video/mp4">
                    Your browser does not support the video tag.
                  </video>
                </div>
                <div class="mt-4 flex justify-end">
                  <a href="/\${data.project.processed_video_path}" download class="px-4 py-2 bg-primary text-primary-foreground rounded-md text-sm font-medium">
                    Download Video
                  </a>
                </div>
              \`;
            } else {
              videoContainer.innerHTML = \`
                <div class="text-center py-8 text-muted-foreground">
                  No processed video available. Process the project to generate an edited video.
                </div>
              \`;
            }
            
            // Update jobs tab
            const jobsContainer = document.getElementById('jobs-container');
            if (data.jobs && data.jobs.length > 0) {
              jobsContainer.innerHTML = \`
                <div class="space-y-4" id="jobs-list"></div>
              \`;
              
              const jobsList = document.getElementById('jobs-list');
              data.jobs.forEach(job => {
                const statusColor = {
                  'pending': 'bg-yellow-500',
                  'processing': 'bg-blue-500',
                  'completed': 'bg-green-500',
                  'failed': 'bg-red-500'
                }[job.status] || 'bg-gray-500';
                
                const jobType = {
                  'tracklist_generation': 'Tracklist Generation',
                  'youtube_check': 'YouTube Compatibility Check',
                  'video_editing': 'Video Editing',
                  'thumbnail_generation': 'Thumbnail Generation'
                }[job.job_type] || job.job_type;
                
                const card = document.createElement('div');
                card.className = 'border rounded-lg p-4';
                card.innerHTML = \`
                  <div class="flex justify-between items-start">
                    <div>
                      <h3 class="font-semibold">\${jobType}</h3>
                      <p class="text-sm text-muted-foreground">Created: \${new Date(job.created_at).toLocaleString()}</p>
                      <p class="text-sm text-muted-foreground">Updated: \${new Date(job.updated_at).toLocaleString()}</p>
                    </div>
                    <span class="px-2 py-1 text-xs font-semibold rounded-full \${statusColor} text-white">
                      \${job.status.charAt(0).toUpperCase() + job.status.slice(1)}
                    </span>
                  </div>
                  \${job.error ? \`<div class="mt-2 p-2 bg-red-50 text-red-500 rounded text-sm">\${job.error}</div>\` : ''}
                \`;
                jobsList.appendChild(card);
              });
            } else {
              jobsContainer.innerHTML = \`
                <div class="text-center py-8 text-muted-foreground">
                  No processing jobs found.
                </div>
              \`;
            }
          } catch (error) {
            console.error('Error fetching project details:', error);
            document.getElementById('project-status').innerHTML = \`
              <div class="text-center py-8 text-red-500">
                Error loading project details. Please try again later.
              </div>
            \`;
          }
        });
        
        // Helper function to format time in HH:MM:SS
        function formatTime(seconds) {
          const hours = Math.floor(seconds / 3600);
          const minutes = Math.floor((seconds % 3600) / 60);
          const secs = Math.floor(seconds % 60);
          
          return [
            hours.toString().padStart(2, '0'),
            minutes.toString().padStart(2, '0'),
            secs.toString().padStart(2, '0')
          ].join(':');
        }
      `}} />
    </div>
  );
}
