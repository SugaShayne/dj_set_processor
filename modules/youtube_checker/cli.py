"""
Command-line interface for the YouTube Compatibility Checker module.
"""

import os
import sys
import json
import argparse
from youtube_checker import YouTubeCompatibilityChecker
from config import YOUTUBE_API_CONFIG, STATUS_CODES

def main():
    """
    Main entry point for the YouTube Compatibility Checker CLI.
    """
    parser = argparse.ArgumentParser(description='YouTube Compatibility Checker')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Check single track command
    check_parser = subparsers.add_parser('check', help='Check YouTube compatibility for a track')
    check_parser.add_argument('--artist', required=True, help='Artist name')
    check_parser.add_argument('--title', required=True, help='Track title')
    check_parser.add_argument('--region', help='Region code (default: US)')
    check_parser.add_argument('--output', '-o', help='Path to save the result JSON file')
    
    # Check tracklist command
    tracklist_parser = subparsers.add_parser('check-tracklist', help='Check YouTube compatibility for a tracklist')
    tracklist_parser.add_argument('file', help='Path to tracklist JSON file')
    tracklist_parser.add_argument('--region', help='Region code (default: US)')
    tracklist_parser.add_argument('--output', '-o', help='Path to save the results JSON file')
    
    # Set API key command
    key_parser = subparsers.add_parser('set-key', help='Set YouTube API key')
    key_parser.add_argument('key', help='YouTube API key')
    
    args = parser.parse_args()
    
    if args.command == 'check':
        # Initialize checker
        checker = YouTubeCompatibilityChecker()
        
        print(f"Checking YouTube compatibility for: {args.artist} - {args.title}")
        result = checker.check_track_compatibility(args.artist, args.title, args.region)
        
        # Print result
        status = result.get('status', STATUS_CODES['UNKNOWN'])
        reason = result.get('reason', 'Unknown')
        
        print(f"Status: {status}")
        print(f"Reason: {reason}")
        
        if 'checked_videos' in result:
            print(f"Checked {len(result['checked_videos'])} videos:")
            for i, video in enumerate(result['checked_videos']):
                video_status = video['restrictions']['status']
                video_reason = video['restrictions']['reason']
                print(f"  {i+1}. {video['url']} - {video_status} ({video_reason})")
        
        # Save to file if output path is provided
        if args.output:
            output_path = os.path.abspath(args.output)
            with open(output_path, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"Result saved to: {output_path}")
        
        # Close checker
        checker.close()
        
        # Return exit code based on status
        if status == STATUS_CODES['BLOCKED']:
            return 1
        elif status == STATUS_CODES['RESTRICTED']:
            return 2
        elif status == STATUS_CODES['UNKNOWN']:
            return 3
        else:
            return 0
    
    elif args.command == 'check-tracklist':
        # Check if file exists
        file_path = os.path.abspath(args.file)
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return 1
        
        # Load tracklist
        try:
            with open(file_path, 'r') as f:
                tracklist_data = json.load(f)
        except json.JSONDecodeError:
            print(f"Invalid JSON file: {file_path}")
            return 1
        
        # Extract tracks from tracklist
        if 'tracks' in tracklist_data:
            tracks = tracklist_data['tracks']
        else:
            tracks = tracklist_data
        
        if not tracks:
            print("No tracks found in tracklist")
            return 1
        
        # Initialize checker
        checker = YouTubeCompatibilityChecker()
        
        print(f"Checking YouTube compatibility for {len(tracks)} tracks...")
        results = []
        
        for track in tracks:
            # Extract artist and title from track
            artist = track.get('artist', track.get('track_name', '').split(' - ')[0] if ' - ' in track.get('track_name', '') else '')
            title = track.get('title', track.get('track_name', '').split(' - ')[1] if ' - ' in track.get('track_name', '') else track.get('track_name', ''))
            
            if not artist or not title:
                print(f"Skipping track with missing artist or title: {track}")
                continue
            
            print(f"Checking: {artist} - {title}")
            result = checker.check_track_compatibility(artist, title, args.region)
            
            # Add original track info to result
            result['original_track'] = track
            
            # Print result
            status = result.get('status', STATUS_CODES['UNKNOWN'])
            reason = result.get('reason', 'Unknown')
            print(f"  Status: {status}")
            print(f"  Reason: {reason}")
            
            results.append(result)
        
        # Save to file if output path is provided
        if args.output:
            output_path = os.path.abspath(args.output)
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"Results saved to: {output_path}")
        
        # Close checker
        checker.close()
        
        # Count blocked tracks
        blocked_count = sum(1 for r in results if r.get('status') == STATUS_CODES['BLOCKED'])
        if blocked_count > 0:
            print(f"Warning: {blocked_count} out of {len(results)} tracks are blocked on YouTube")
            return 1
        else:
            print("All tracks are compatible with YouTube")
            return 0
    
    elif args.command == 'set-key':
        # Update config file with new API key
        config_path = os.path.join(os.path.dirname(__file__), 'config.py')
        
        try:
            with open(config_path, 'r') as f:
                config_content = f.read()
            
            # Replace API key in config
            new_config = config_content.replace(
                f'"api_key": "{YOUTUBE_API_CONFIG["api_key"]}"',
                f'"api_key": "{args.key}"'
            )
            
            with open(config_path, 'w') as f:
                f.write(new_config)
            
            print(f"API key updated successfully")
            return 0
        except Exception as e:
            print(f"Error updating API key: {str(e)}")
            return 1
    
    else:
        parser.print_help()
        return 1

if __name__ == "__main__":
    sys.exit(main())
