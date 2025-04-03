"""
Command-line interface for the Tracklist Generator module.
"""

import os
import argparse
import json
from tracklist_generator import TracklistGenerator
from database import create_database
from config import DATABASE_CONFIG

def main():
    """
    Main entry point for the Tracklist Generator CLI.
    """
    parser = argparse.ArgumentParser(description='DJ Set Tracklist Generator')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Initialize database command
    init_parser = subparsers.add_parser('init', help='Initialize the database')
    
    # Fingerprint reference tracks command
    fingerprint_parser = subparsers.add_parser('fingerprint', help='Fingerprint reference tracks')
    fingerprint_parser.add_argument('path', help='Path to directory containing reference tracks or a single track file')
    
    # Identify tracks in mix command
    identify_parser = subparsers.add_parser('identify', help='Identify tracks in a DJ mix')
    identify_parser.add_argument('path', help='Path to the DJ mix audio or video file')
    identify_parser.add_argument('--output', '-o', help='Path to save the tracklist JSON file')
    
    args = parser.parse_args()
    
    if args.command == 'init':
        print("Initializing database...")
        if create_database(DATABASE_CONFIG):
            print("Database initialized successfully.")
        else:
            print("Failed to initialize database.")
    
    elif args.command == 'fingerprint':
        generator = TracklistGenerator()
        path = os.path.abspath(args.path)
        
        if os.path.isdir(path):
            print(f"Fingerprinting tracks in directory: {path}")
            count = generator.fingerprint_reference_tracks(path)
            print(f"Fingerprinted {count} tracks.")
        elif os.path.isfile(path):
            print(f"Fingerprinting track: {path}")
            song_id = generator.fingerprint_single_track(path)
            if song_id:
                print(f"Track fingerprinted successfully with ID: {song_id}")
            else:
                print("Failed to fingerprint track.")
        else:
            print(f"Path not found: {path}")
    
    elif args.command == 'identify':
        generator = TracklistGenerator()
        path = os.path.abspath(args.path)
        
        if not os.path.exists(path):
            print(f"File not found: {path}")
            return
        
        print(f"Identifying tracks in: {path}")
        
        # Check if it's a video file
        _, ext = os.path.splitext(path)
        if ext.lower() in ['.mp4', '.avi', '.mov', '.mkv', '.webm']:
            print("Extracting audio from video...")
            tracklist = generator.generate_tracklist_from_video(path)
        else:
            # Assume it's an audio file
            tracklist = generator.identify_tracks_in_mix(path)
            tracklist = {
                "file": os.path.basename(path),
                "processed_date": None,  # Will be filled by the function
                "track_count": len(tracklist),
                "tracks": tracklist
            }
        
        # Print results
        if tracklist["track_count"] > 0:
            print(f"Found {tracklist['track_count']} tracks:")
            for track in tracklist["tracks"]:
                print(f"{track['id']}. {track['track_name']} - "
                      f"Start: {track['start_time_formatted']} - "
                      f"Confidence: {track['confidence']:.2f}")
        else:
            print("No tracks identified. Make sure you have fingerprinted reference tracks.")
        
        # Save to file if output path is provided
        if args.output:
            output_path = os.path.abspath(args.output)
            generator.save_tracklist_to_json(tracklist, output_path)
            print(f"Tracklist saved to: {output_path}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
