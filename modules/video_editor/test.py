"""
Test script for the Video Editor module.
"""

import os
import sys
import json
import argparse
import tempfile
from video_editor import VideoEditor
from config import VIDEO_EDITING_CONFIG

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
        ).with_duration(segment_duration).with_position('center').with_start(start_time)
        
        clips.append(text)
    
    # Composite the clips
    video = CompositeVideoClip(clips)
    
    # Add audio (1kHz test tone)
    video = video.with_audio(video.audio)
    
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

def test_edit_video():
    """
    Test editing a video to remove segments.
    """
    print("Testing video editing functionality...")
    
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a test video
        test_video_path = os.path.join(temp_dir, "test_video.mp4")
        create_test_video(test_video_path)
        
        # Define segments to remove (segment 2 and 4)
        segments_to_remove = [
            {"start_time": 6, "end_time": 12},   # Segment 2
            {"start_time": 18, "end_time": 24}   # Segment 4
        ]
        
        # Initialize editor
        editor = VideoEditor()
        
        # Edit the video
        output_path = os.path.join(temp_dir, "edited_video.mp4")
        result_path = editor.edit_video(test_video_path, segments_to_remove, output_path)
        
        # Check if output file exists
        if os.path.exists(result_path):
            print(f"✓ Video edited successfully: {result_path}")
            
            # Check if output file has content
            if os.path.getsize(result_path) > 0:
                print(f"✓ Output file has content: {os.path.getsize(result_path)} bytes")
            else:
                print("✗ Output file is empty")
                return False
        else:
            print(f"✗ Failed to create output file: {result_path}")
            return False
        
        # Clean up
        editor.cleanup()
    
    return True

def test_extract_frame():
    """
    Test extracting a frame from a video.
    """
    print("\nTesting frame extraction functionality...")
    
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a test video
        test_video_path = os.path.join(temp_dir, "test_video.mp4")
        create_test_video(test_video_path)
        
        # Initialize editor
        editor = VideoEditor()
        
        # Extract a frame
        output_path = os.path.join(temp_dir, "frame.jpg")
        result_path = editor.extract_frame(test_video_path, 15, output_path)
        
        # Check if output file exists
        if os.path.exists(result_path):
            print(f"✓ Frame extracted successfully: {result_path}")
            
            # Check if output file has content
            if os.path.getsize(result_path) > 0:
                print(f"✓ Output file has content: {os.path.getsize(result_path)} bytes")
            else:
                print("✗ Output file is empty")
                return False
        else:
            print(f"✗ Failed to create output file: {result_path}")
            return False
        
        # Clean up
        editor.cleanup()
    
    return True

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
        
        # Initialize editor
        editor = VideoEditor()
        
        # Edit the video from tracklist
        output_path = os.path.join(temp_dir, "edited_from_tracklist.mp4")
        result_path = editor.edit_video_from_tracklist(test_video_path, tracklist_path, output_path)
        
        # Check if output file exists
        if os.path.exists(result_path):
            print(f"✓ Video edited from tracklist successfully: {result_path}")
            
            # Check if output file has content
            if os.path.getsize(result_path) > 0:
                print(f"✓ Output file has content: {os.path.getsize(result_path)} bytes")
            else:
                print("✗ Output file is empty")
                return False
        else:
            print(f"✗ Failed to create output file: {result_path}")
            return False
        
        # Clean up
        editor.cleanup()
    
    return True

def main():
    """
    Main entry point for the test script.
    """
    parser = argparse.ArgumentParser(description='Test the Video Editor module')
    parser.add_argument('--test', choices=['edit', 'frame', 'tracklist', 'all'], default='all',
                      help='Test to run (default: all)')
    
    args = parser.parse_args()
    
    # Run tests
    success = True
    
    if args.test in ['edit', 'all']:
        edit_success = test_edit_video()
        success = success and edit_success
    
    if args.test in ['frame', 'all']:
        frame_success = test_extract_frame()
        success = success and frame_success
    
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
