import React from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

export default function ProjectsPage() {
  return (
    <div className="container mx-auto py-10">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold tracking-tight">Your Projects</h1>
        <Link href="/upload">
          <Button>Upload New DJ Set</Button>
        </Link>
      </div>
      
      <div className="grid gap-6" id="projects-container">
        {/* Projects will be loaded here via client-side JavaScript */}
        <div className="text-center py-8 text-muted-foreground">
          Loading projects...
        </div>
      </div>

      <script dangerouslySetInnerHTML={{ __html: `
        // Fetch projects on page load
        document.addEventListener('DOMContentLoaded', async () => {
          try {
            const response = await fetch('/api/projects');
            const data = await response.json();
            const projectsContainer = document.getElementById('projects-container');
            
            if (data.projects && data.projects.length > 0) {
              projectsContainer.innerHTML = '';
              
              data.projects.forEach(project => {
                const statusColor = {
                  'pending': 'bg-yellow-500',
                  'processing': 'bg-blue-500',
                  'completed': 'bg-green-500',
                  'failed': 'bg-red-500'
                }[project.status] || 'bg-gray-500';
                
                const card = document.createElement('div');
                card.innerHTML = \`
                  <div class="border rounded-lg overflow-hidden shadow-sm">
                    <div class="p-6">
                      <div class="flex justify-between items-start">
                        <div>
                          <h3 class="text-xl font-semibold">\${project.name}</h3>
                          <p class="text-sm text-muted-foreground">\${new Date(project.created_at).toLocaleString()}</p>
                        </div>
                        <span class="px-2 py-1 text-xs font-semibold rounded-full \${statusColor} text-white">
                          \${project.status.charAt(0).toUpperCase() + project.status.slice(1)}
                        </span>
                      </div>
                      <p class="mt-2">\${project.description || 'No description'}</p>
                      <div class="mt-4 flex justify-end">
                        <a href="/projects/\${project.id}" class="px-4 py-2 bg-primary text-primary-foreground rounded-md text-sm font-medium">
                          View Details
                        </a>
                      </div>
                    </div>
                  </div>
                \`;
                projectsContainer.appendChild(card);
              });
            } else {
              projectsContainer.innerHTML = \`
                <div class="text-center py-12">
                  <h3 class="text-xl font-semibold mb-2">No projects yet</h3>
                  <p class="text-muted-foreground mb-4">Upload your first DJ set to get started</p>
                  <a href="/upload" class="px-4 py-2 bg-primary text-primary-foreground rounded-md text-sm font-medium">
                    Upload DJ Set
                  </a>
                </div>
              \`;
            }
          } catch (error) {
            console.error('Error fetching projects:', error);
            const projectsContainer = document.getElementById('projects-container');
            projectsContainer.innerHTML = \`
              <div class="text-center py-8 text-red-500">
                Error loading projects. Please try again later.
              </div>
            \`;
          }
        });
      `}} />
    </div>
  );
}
