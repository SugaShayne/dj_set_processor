"""
Test script for the Thumbnail Generator module.
"""

import os
import sys
import json
import argparse
import tempfile
from thumbnail_generator import ThumbnailGenerator
from config import THUMBNAIL_CONFIG

def create_test_video(output_path, duration=30):
    """
    Create a test video for testing.
    
    Args:
        output_path: Path to save the test video
        duration: Duration of the test video in seconds
        
    Returns:
        Path to the test video
    """
    from moviepy.editor import ColorClip, TextClip, CompositeVideoClip
    
    # Create a background clip
    background = ColorClip(size=(1280, 720), color=(0, 0, 0), duration=duration)
    
    # Create text clips for different segments
    clips = [background]
    
    segment_duration = duration / 5
    for i in range(5):
        start_time = i * segment_duration
        text = TextClip(
            f"Segment {i+1}\nTime: {start_time:.1f}s - {start_time + segment_duration:.1f}s",
            fontsize=70,
            color='white',
            font="Arial"
        ).set_duration(segment_duration).set_position('center').set_start(start_time)
        
        clips.append(text)
    
    # Composite the clips
    video = CompositeVideoClip(clips)
    
    # Write the video
    video.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac",
        fps=30
    )
    
    # Close clips
    for clip in clips:
        clip.close()
    video.close()
    
    return output_path

def test_generate_thumbnails():
    """
    Test generating thumbnails from a video.
    """
    print("Testing thumbnail generation functionality...")
    
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a test video
        test_video_path = os.path.join(temp_dir, "test_video.mp4")
        create_test_video(test_video_path)
        
        # Initialize generator
        generator = ThumbnailGenerator()
        
        # Generate thumbnails
        output_dir = os.path.join(temp_dir, "thumbnails")
        os.makedirs(output_dir, exist_ok=True)
        
        thumbnail_paths = generator.generate_thumbnails(
            test_video_path, 
            output_dir, 
            5  # Generate 5 thumbnails
        )
        
        # Check if thumbnails were generated
        if len(thumbnail_paths) > 0:
            print(f"✓ Generated {len(thumbnail_paths)} thumbnails")
            
            # Check if thumbnail files exist
            all_exist = all(os.path.exists(path) for path in thumbnail_paths)
            if all_exist:
                print(f"✓ All thumbnail files exist")
            else:
                print("✗ Some thumbnail files are missing")
                return False
        else:
            print("✗ No thumbnails were generated")
            return False
        
        # Clean up
        generator.cleanup()
    
    return True

def test_extraction_methods():
    """
    Test different frame extraction methods.
    """
    print("\nTesting frame extraction methods...")
    
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a test video
        test_video_path = os.path.join(temp_dir, "test_video.mp4")
        create_test_video(test_video_path)
        
        methods = ['uniform', 'key_moments', 'random']
        success = True
        
        for method in methods:
            print(f"\nTesting '{method}' extraction method:")
            
            # Create config with specific method
            config = THUMBNAIL_CONFIG.copy()
            config['extraction_method'] = method
            
            # Initialize generator
            generator = ThumbnailGenerator(config)
            
            # Generate thumbnails
            output_dir = os.path.join(temp_dir, f"thumbnails_{method}")
            os.makedirs(output_dir, exist_ok=True)
            
            try:
                thumbnail_paths = generator.generate_thumbnails(
                    test_video_path, 
                    output_dir, 
                    3  # Generate 3 thumbnails
                )
                
                # Check if thumbnails were generated
                if len(thumbnail_paths) > 0:
                    print(f"✓ Generated {len(thumbnail_paths)} thumbnails using '{method}' method")
                else:
                    print(f"✗ No thumbnails were generated using '{method}' method")
                    success = False
            except Exception as e:
                print(f"✗ Error with '{method}' method: {str(e)}")
                success = False
            
            # Clean up
            generator.cleanup()
        
    return success

def test_tracklist_integration():
    """
    Test integration with tracklist data.
    """
    print("\nTesting tracklist integration...")
    
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a test video
        test_video_path = os.path.join(temp_dir, "test_video.mp4")
        create_test_video(test_video_path)
        
        # Create a test tracklist
        tracklist = {
            "tracks": [
                {
                    "id": 1,
                    "track_name": "Track 1",
                    "artist": "Artist 1",
                    "title": "Title 1",
                    "start_time": 0,
                    "end_time": 6,
                    "status": "available"
                },
                {
                    "id": 2,
                    "track_name": "Track 2",
                    "artist": "Artist 2",
                    "title": "Title 2",
                    "start_time": 6,
                    "end_time": 12,
                    "status": "blocked"
                },
                {
                    "id": 3,
                    "track_name": "Track 3",
                    "artist": "Artist 3",
                    "title": "Title 3",
                    "start_time": 12,
                    "end_time": 18,
                    "status": "available"
                },
                {
                    "id": 4,
                    "track_name": "Track 4",
                    "artist": "Artist 4",
                    "title": "Title 4",
                    "start_time": 18,
                    "end_time": 24,
                    "status": "blocked"
                },
                {
                    "id": 5,
                    "track_name": "Track 5",
                    "artist": "Artist 5",
                    "title": "Title 5",
                    "start_time": 24,
                    "end_time": 30,
                    "status": "available"
                }
            ]
        }
        
        # Save tracklist to file
        tracklist_path = os.path.join(temp_dir, "tracklist.json")
        with open(tracklist_path, 'w') as f:
            json.dump(tracklist, f)
        
        # Initialize generator
        generator = ThumbnailGenerator()
        
        # Generate thumbnails from tracklist
        output_dir = os.path.join(temp_dir, "thumbnails_tracklist")
        os.makedirs(output_dir, exist_ok=True)
        
        thumbnail_paths = generator.generate_thumbnails_from_tracklist(
            test_video_path, 
            tracklist_path, 
            output_dir, 
            3  # Generate 3 thumbnails
        )
        
        # Check if thumbnails were generated
        if len(thumbnail_paths) > 0:
            print(f"✓ Generated {len(thumbnail_paths)} thumbnails from tracklist")
            
            # Check if thumbnail files exist
            all_exist = all(os.path.exists(path) for path in thumbnail_paths)
            if all_exist:
                print(f"✓ All thumbnail files exist")
            else:
                print("✗ Some thumbnail files are missing")
                return False
        else:
            print("✗ No thumbnails were generated from tracklist")
            return False
        
        # Clean up
        generator.cleanup()
    
    return True

def main():
    """
    Main entry point for the test script.
    """
    parser = argparse.ArgumentParser(description='Test the Thumbnail Generator module')
    parser.add_argument('--test', choices=['generate', 'methods', 'tracklist', 'all'], default='all',
                      help='Test to run (default: all)')
    
    args = parser.parse_args()
    
    # Run tests
    success = True
    
    if args.test in ['generate', 'all']:
        generate_success = test_generate_thumbnails()
        success = success and generate_success
    
    if args.test in ['methods', 'all']:
        methods_success = test_extraction_methods()
        success = success and methods_success
    
    if args.test in ['tracklist', 'all']:
        tracklist_success = test_tracklist_integration()
        success = success and tracklist_success
    
    print("\nTest summary:")
    if success:
        print("All tests passed!")
        return 0
    else:
        print("Some tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
