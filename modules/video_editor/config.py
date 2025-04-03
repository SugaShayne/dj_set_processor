"""
Configuration for the Video Editor module.
"""

# Video editing configuration
VIDEO_EDITING_CONFIG = {
    # Transition type between clips
    # Options: "crossfade", "fade", "none"
    "transition_type": "crossfade",
    
    # Duration of transition in seconds
    "transition_duration": 2.0,
    
    # Output video codec
    "codec": "libx264",
    
    # Output video bitrate
    "bitrate": "8000k",
    
    # Output audio codec
    "audio_codec": "aac",
    
    # Output audio bitrate
    "audio_bitrate": "192k",
    
    # Output video resolution (width, height)
    # None means keep original resolution
    "resolution": None,
    
    # Output video format
    "format": "mp4",
    
    # Temporary directory for processing
    "temp_dir": "/tmp/video_editor",
    
    # Whether to show progress bar during processing
    "show_progress": True,
    
    # Threads to use for processing
    "threads": 4,
    
    # Minimum segment duration in seconds
    # Segments shorter than this will be merged with adjacent segments
    "min_segment_duration": 5.0
}

# Logging configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": None  # Set to a file path to enable file logging
}
