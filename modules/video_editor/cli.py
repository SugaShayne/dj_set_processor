"""
Command-line interface for the Video Editor module.
"""

import os
import sys
import json
import argparse
from video_editor import VideoEditor
from config import VIDEO_EDITING_CONFIG

def main():
    """
    Main entry point for the Video Editor CLI.
    """
    parser = argparse.ArgumentParser(description='Video Editor for DJ Sets')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Edit video command
    edit_parser = subparsers.add_parser('edit', help='Edit a video to remove segments')
    edit_parser.add_argument('video', help='Path to the input video file')
    edit_parser.add_argument('--segments', '-s', required=True, 
                           help='JSON file with segments to remove or JSON string with segments array')
    edit_parser.add_argument('--output', '-o', help='Path to save the output video')
    edit_parser.add_argument('--transition', choices=['crossfade', 'fade', 'none'], 
                           help='Transition type between clips')
    edit_parser.add_argument('--duration', type=float, 
                           help='Duration of transition in seconds')
    
    # Edit from tracklist command
    tracklist_parser = subparsers.add_parser('edit-from-tracklist', 
                                           help='Edit a video based on a tracklist with compatibility info')
    tracklist_parser.add_argument('video', help='Path to the input video file')
    tracklist_parser.add_argument('tracklist', help='Path to the tracklist JSON file')
    tracklist_parser.add_argument('--output', '-o', help='Path to save the output video')
    tracklist_parser.add_argument('--transition', choices=['crossfade', 'fade', 'none'], 
                                help='Transition type between clips')
    tracklist_parser.add_argument('--duration', type=float, 
                                help='Duration of transition in seconds')
    
    # Extract frame command
    frame_parser = subparsers.add_parser('extract-frame', help='Extract a frame from a video')
    frame_parser.add_argument('video', help='Path to the input video file')
    frame_parser.add_argument('--time', '-t', type=float, required=True, 
                            help='Time in seconds to extract frame')
    frame_parser.add_argument('--output', '-o', help='Path to save the output image')
    
    args = parser.parse_args()
    
    # Create config with command line overrides
    config = VIDEO_EDITING_CONFIG.copy()
    
    if args.command in ['edit', 'edit-from-tracklist']:
        if hasattr(args, 'transition') and args.transition:
            config['transition_type'] = args.transition
        if hasattr(args, 'duration') and args.duration:
            config['transition_duration'] = args.duration
    
    # Initialize editor
    editor = VideoEditor(config)
    
    try:
        if args.command == 'edit':
            # Parse segments
            try:
                # Try to parse as JSON file
                if os.path.exists(args.segments):
                    with open(args.segments, 'r') as f:
                        segments_data = json.load(f)
                        
                    # Extract segments from JSON
                    if isinstance(segments_data, list):
                        segments = segments_data
                    elif 'segments' in segments_data:
                        segments = segments_data['segments']
                    else:
                        print("Invalid segments JSON format. Expected array or object with 'segments' property.")
                        return 1
                else:
                    # Try to parse as JSON string
                    segments = json.loads(args.segments)
            except json.JSONDecodeError:
                print(f"Invalid JSON format in segments: {args.segments}")
                return 1
            
            # Edit video
            output_path = editor.edit_video(args.video, segments, args.output)
            print(f"Video edited successfully. Output saved to: {output_path}")
        
        elif args.command == 'edit-from-tracklist':
            # Edit video from tracklist
            output_path = editor.edit_video_from_tracklist(args.video, args.tracklist, args.output)
            print(f"Video edited successfully. Output saved to: {output_path}")
        
        elif args.command == 'extract-frame':
            # Extract frame
            output_path = editor.extract_frame(args.video, args.time, args.output)
            print(f"Frame extracted successfully. Output saved to: {output_path}")
        
        else:
            parser.print_help()
            return 1
        
        return 0
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    finally:
        # Clean up
        editor.cleanup()

if __name__ == "__main__":
    sys.exit(main())
