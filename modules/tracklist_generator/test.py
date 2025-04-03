"""
Test script for the Tracklist Generator module.
"""

import os
import sys
import argparse
from tracklist_generator import TracklistGenerator
from database import create_database
from config import DATABASE_CONFIG

def setup_test_environment():
    """
    Set up the test environment by initializing the database.
    """
    print("Setting up test environment...")
    if create_database(DATABASE_CONFIG):
        print("Database initialized successfully.")
        return True
    else:
        print("Failed to initialize database.")
        return False

def test_fingerprinting(reference_dir):
    """
    Test fingerprinting functionality with reference tracks.
    
    Args:
        reference_dir: Directory containing reference tracks
    """
    if not os.path.exists(reference_dir):
        print(f"Reference directory not found: {reference_dir}")
        return False
    
    print(f"Testing fingerprinting with reference tracks in: {reference_dir}")
    generator = TracklistGenerator()
    
    try:
        count = generator.fingerprint_reference_tracks(reference_dir)
        print(f"Successfully fingerprinted {count} tracks.")
        return True
    except Exception as e:
        print(f"Error during fingerprinting: {str(e)}")
        return False

def test_identification(mix_file):
    """
    Test track identification in a mix.
    
    Args:
        mix_file: Path to a DJ mix file
    """
    if not os.path.exists(mix_file):
        print(f"Mix file not found: {mix_file}")
        return False
    
    print(f"Testing track identification with mix file: {mix_file}")
    generator = TracklistGenerator()
    
    try:
        # Check if it's a video file
        _, ext = os.path.splitext(mix_file)
        if ext.lower() in ['.mp4', '.avi', '.mov', '.mkv', '.webm']:
            print("Extracting audio from video...")
            tracklist = generator.generate_tracklist_from_video(mix_file)
        else:
            # Assume it's an audio file
            tracklist = generator.identify_tracks_in_mix(mix_file)
            tracklist = {
                "file": os.path.basename(mix_file),
                "processed_date": None,
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
            return True
        else:
            print("No tracks identified. Make sure you have fingerprinted reference tracks.")
            return False
    except Exception as e:
        print(f"Error during identification: {str(e)}")
        return False

def main():
    """
    Main entry point for the test script.
    """
    parser = argparse.ArgumentParser(description='Test the Tracklist Generator module')
    parser.add_argument('--setup', action='store_true', help='Set up the test environment')
    parser.add_argument('--fingerprint', help='Test fingerprinting with reference tracks directory')
    parser.add_argument('--identify', help='Test track identification with a mix file')
    
    args = parser.parse_args()
    
    if args.setup:
        if not setup_test_environment():
            return 1
    
    if args.fingerprint:
        if not test_fingerprinting(args.fingerprint):
            return 1
    
    if args.identify:
        if not test_identification(args.identify):
            return 1
    
    if not (args.setup or args.fingerprint or args.identify):
        parser.print_help()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
