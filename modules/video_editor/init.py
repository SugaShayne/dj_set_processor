"""
Module initialization file for the Video Editor.
"""

from .video_editor import VideoEditor
from .config import VIDEO_EDITING_CONFIG, LOGGING_CONFIG

__all__ = [
    'VideoEditor',
    'VIDEO_EDITING_CONFIG',
    'LOGGING_CONFIG'
]
