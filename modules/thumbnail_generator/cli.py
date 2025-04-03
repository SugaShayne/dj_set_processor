"""
Command-line interface for the Thumbnail Generator module.
"""

import os
import sys
import json
import argparse
from thumbnail_generator import ThumbnailGenerator
from config import THUMBNAIL_CONFIG

def main():
    """
    Main entry point for the Thumbnail Generator CLI.
    """
    parser = argparse.ArgumentParser(description='Thumbnail Generator for DJ Sets')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Generate thumbnails command
    generate_parser = subparsers.add_parser('generate', help='Generate thumbnails from a video')
    generate_parser.add_argument('video', help='Path to the input video file')
    generate_parser.add_argument('--output', '-o', required=True, help='Directory to save the thumbnails')
    generate_parser.add_argument('--count', '-c', type=int, help='Number of thumbnails to generate')
    generate_parser.add_argument('--method', choices=['uniform', 'key_moments', 'random'], 
                               help='Frame extraction method')
    
    # Generate thumbnails from tracklist command
    tracklist_parser = subparsers.add_parser('generate-from-tracklist', 
                                           help='Generate thumbnails from a video based on a tracklist')
    tracklist_parser.add_argument('video', help='Path to the input video file')
    tracklist_parser.add_argument('tracklist', help='Path to the tracklist JSON file')
    tracklist_parser.add_argument('--output', '-o', required=True, help='Directory to save the thumbnails')
    tracklist_parser.add_argument('--count', '-c', type=int, help='Number of thumbnails to generate')
    
    args = parser.parse_args()
    
    # Create config with command line overrides
    config = THUMBNAIL_CONFIG.copy()
    
    if hasattr(args, 'method') and args.method:
        config['extraction_method'] = args.method
    
    # Initialize generator
    generator = ThumbnailGenerator(config)
    
    try:
        if args.command == 'generate':
            # Generate thumbnails
            thumbnail_paths = generator.generate_thumbnails(
                args.video, 
                args.output, 
                args.count
            )
            
            print(f"Generated {len(thumbnail_paths)} thumbnails:")
            for i, path in enumerate(thumbnail_paths):
                print(f"  {i+1}. {path}")
        
        elif args.command == 'generate-from-tracklist':
            # Generate thumbnails from tracklist
            thumbnail_paths = generator.generate_thumbnails_from_tracklist(
                args.video, 
                args.tracklist, 
                args.output, 
                args.count
            )
            
            print(f"Generated {len(thumbnail_paths)} thumbnails based on tracklist:")
            for i, path in enumerate(thumbnail_paths):
                print(f"  {i+1}. {path}")
        
        else:
            parser.print_help()
            return 1
        
        return 0
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    finally:
        # Clean up
        generator.cleanup()

if __name__ == "__main__":
    sys.exit(main())
