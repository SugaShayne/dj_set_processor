"""
Test script for the YouTube Compatibility Checker module.
"""

import os
import sys
import json
import argparse
from youtube_checker import YouTubeCompatibilityChecker
from config import YOUTUBE_API_CONFIG, STATUS_CODES

def test_single_track(api_key=None):
    """
    Test checking compatibility for a single track.
    
    Args:
        api_key: YouTube API key (optional)
    """
    print("Testing single track compatibility check...")
    
    # Test track (commonly available)
    artist = "Rick Astley"
    title = "Never Gonna Give You Up"
    
    checker = YouTubeCompatibilityChecker(api_key=api_key)
    result = checker.check_track_compatibility(artist, title)
    
    print(f"Track: {artist} - {title}")
    print(f"Status: {result.get('status')}")
    print(f"Reason: {result.get('reason')}")
    
    if 'checked_videos' in result:
        print(f"Checked {len(result['checked_videos'])} videos:")
        for i, video in enumerate(result['checked_videos']):
            video_status = video['restrictions']['status']
            video_reason = video['restrictions']['reason']
            print(f"  {i+1}. {video['url']} - {video_status} ({video_reason})")
    
    checker.close()
    return result['status'] == STATUS_CODES['AVAILABLE']

def test_tracklist(api_key=None):
    """
    Test checking compatibility for a tracklist.
    
    Args:
        api_key: YouTube API key (optional)
    """
    print("\nTesting tracklist compatibility check...")
    
    # Sample tracklist
    tracklist = [
        {"artist": "Rick Astley", "title": "Never Gonna Give You Up"},
        {"artist": "Toto", "title": "Africa"},
        {"artist": "A-ha", "title": "Take On Me"}
    ]
    
    checker = YouTubeCompatibilityChecker(api_key=api_key)
    results = checker.check_tracklist_compatibility(tracklist)
    
    print(f"Checked {len(results)} tracks:")
    for i, result in enumerate(results):
        track = result['track']
        status = result.get('status')
        reason = result.get('reason')
        print(f"  {i+1}. {track['artist']} - {track['title']}: {status} ({reason})")
    
    checker.close()
    return all(r['status'] == STATUS_CODES['AVAILABLE'] for r in results)

def test_caching(api_key=None):
    """
    Test caching functionality.
    
    Args:
        api_key: YouTube API key (optional)
    """
    print("\nTesting caching functionality...")
    
    # Test track
    artist = "Queen"
    title = "Bohemian Rhapsody"
    
    checker = YouTubeCompatibilityChecker(api_key=api_key)
    
    # First check (should hit API)
    print("First check (should hit API):")
    start_time = __import__('time').time()
    result1 = checker.check_track_compatibility(artist, title)
    end_time = __import__('time').time()
    first_duration = end_time - start_time
    print(f"Duration: {first_duration:.2f} seconds")
    
    # Second check (should hit cache)
    print("\nSecond check (should hit cache):")
    start_time = __import__('time').time()
    result2 = checker.check_track_compatibility(artist, title)
    end_time = __import__('time').time()
    second_duration = end_time - start_time
    print(f"Duration: {second_duration:.2f} seconds")
    
    # Check if results are the same
    results_match = result1 == result2
    print(f"Results match: {results_match}")
    
    # Check if second check was faster (cache hit)
    cache_working = second_duration < first_duration
    print(f"Cache working: {cache_working}")
    
    checker.close()
    return results_match and cache_working

def main():
    """
    Main entry point for the test script.
    """
    parser = argparse.ArgumentParser(description='Test the YouTube Compatibility Checker module')
    parser.add_argument('--api-key', help='YouTube API key')
    parser.add_argument('--test', choices=['single', 'tracklist', 'cache', 'all'], default='all',
                      help='Test to run (default: all)')
    
    args = parser.parse_args()
    
    # Run tests
    success = True
    
    if args.test in ['single', 'all']:
        single_success = test_single_track(args.api_key)
        success = success and single_success
    
    if args.test in ['tracklist', 'all']:
        tracklist_success = test_tracklist(args.api_key)
        success = success and tracklist_success
    
    if args.test in ['cache', 'all']:
        cache_success = test_caching(args.api_key)
        success = success and cache_success
    
    print("\nTest summary:")
    if success:
        print("All tests passed!")
        return 0
    else:
        print("Some tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
