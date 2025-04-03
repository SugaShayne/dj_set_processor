# DJ Set Processor - Production Deployment Configuration

# This file contains the production deployment configuration for the DJ Set Processor application.
# It includes environment variables and build settings for Cloudflare Pages deployment.

# Build settings
[build]
  command = "npm run build"
  publish = ".next"
  environment = { NODE_VERSION = "18" }

# Environment variables
[environment]
  NEXT_PUBLIC_APP_URL = "https://dj-set-processor.pages.dev"
  
# Routes configuration
[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
